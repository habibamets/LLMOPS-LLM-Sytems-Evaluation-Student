import os
import pandas as pd

from evidently import Report, Dataset, DataDefinition
from evidently.presets import TextEvals
from evidently.descriptors import (
    ContextRelevance,
    FaithfulnessLLMEval,
    CompletenessLLMEval
)
from evidently.legacy.utils.llm.wrapper import OpenAIWrapper, LLMResult
from evidently.legacy.utils.llm.base import LLMMessage

_original_complete = OpenAIWrapper.complete

async def _complete_with_json_mode(self, messages):
    """Override qui ajoute response_format={'type': 'json_object'} à chaque appel."""
    import openai
    from openai.types.chat.chat_completion import ChatCompletion
    from evidently.legacy.utils.llm.errors import LLMRateLimitError, LLMRequestError

    messages_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
    try:
        response: ChatCompletion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages_dicts,
            response_format={"type": "json_object"},  # ← LE FIX
        )
    except openai.RateLimitError as e:
        raise LLMRateLimitError(e.message) from e
    except openai.APIError as e:
        raise LLMRequestError(f"Failed to call OpenAI complete API: {e.message}", original_error=e) from e

    content = response.choices[0].message.content
    assert content is not None
    if response.usage is None:
        return LLMResult(content, 0, 0)
    return LLMResult(content, response.usage.prompt_tokens, response.usage.completion_tokens)

OpenAIWrapper.complete = _complete_with_json_mode

# Configuration Client OpenAI d'Evidently pour cibler le LiteLLM Proxy du RAGOPS
PROXY_URL = os.getenv("PROXY_URL", "http://litellm:4000")
os.environ["OPENAI_BASE_URL"] = PROXY_URL + "/v1"
os.environ["OPENAI_API_KEY"] = os.getenv("PROXY_KEY", "sk-litellm-proxy-key")

def run_semantic_evaluation():
    os.makedirs("reports", exist_ok=True)

    # 1. Jeu de test (Simulation d'un "Golden Dataset")
    # Dans la vraie vie, on enverrait des requêtes réelles à l'API de RAG et on loggerait les sorties.
    data = [
        # Cas 1: Succès total
        {
            "question": "What is Meilisearch?",
            "context": "Meilisearch is a lightning-fast, open-source search engine suitable for building fast search experiences.",
            "response": "Meilisearch is an open-source and very fast search engine."
        },
        # Cas 2: Hallucination (Erreur de Faithfulness)
        {
            "question": "Does the system use Redis?",
            "context": "The architecture includes a caching mechanism to improve response times.",
            "response": "Yes, we use Redis version 7 for caching."
        },
        # Cas 3: Hors Sujet (Erreur de Relevance)
        {
            "question": "How to scale the backend?",
            "context": "The backend is stateless and can be scaled horizontally using Docker Swarm or Kubernetes.",
            "response": "Kubernetes is a popular container orchestration system created by Google."
        },
        # Cas 4: Mauvais Retrieval (Erreur de Context Precision)
        {
            "question": "How do I configure the Proxy?",
            "context": "To add a new document, send a POST request to /ingest.",
            "response": "I cannot find proxy configuration in the documentation."
        }
    ]
    df = pd.DataFrame(data)

    eval_model = "groq-llama3"
    data_def = DataDefinition(text_columns=["question", "context", "response"])

    # A. Context Precision (Le contexte est-il utile ?)
    dataset = Dataset.from_pandas(
        df,
        data_definition=data_def,
        descriptors=[
            ContextRelevance(
                "question",
                "context",
                output_scores=True,
                aggregation_method="mean",
                method="llm",
                method_params={"provider": "openai", "model": eval_model},
                alias="Context Precision"
            ),
        ]
    )

    # B & C. Faithfulness + Answer Relevance
    dataset_llm = Dataset.from_pandas(
        df,
        data_definition=data_def,
        descriptors=[
            FaithfulnessLLMEval(
                "response",
                context="context",
                provider="openai",
                model=eval_model,
                alias="Faithfulness"
            ),
            CompletenessLLMEval(
                "response",
                context="context",
                provider="openai",
                model=eval_model,
                alias="Answer Relevance"
            )
        ]
    )

    # Les Reports consolident les métriques par dataset.
    print("Exécution du LLM-as-a-Judge en cours (via LiteLLM Proxy)...")

    report_ctx = Report(metrics=[TextEvals()])
    snapshot_ctx = report_ctx.run(reference_data=None, current_data=dataset)

    report_llm = Report(metrics=[TextEvals()])
    snapshot_llm = report_llm.run(reference_data=None, current_data=dataset_llm)

    # Sauvegarde
    snapshot_ctx.save_html("reports/chapter4_context_precision.html")
    snapshot_ctx.save_json("reports/chapter4_context_precision.json")
    snapshot_llm.save_html("reports/chapter4_semantic_report.html")
    snapshot_llm.save_json("reports/chapter4_semantic_report.json")
    print("Évaluation sémantique terminée (Rapports dans /reports).")

if __name__ == "__main__":
    run_semantic_evaluation()