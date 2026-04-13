import os
import sys
import time
import subprocess
import traceback
import warnings

warnings.filterwarnings("ignore")

import requests
import pytest
import pandas as pd
import json
from testcontainers.compose import DockerCompose

from evidently import Report, Dataset, DataDefinition
from evidently.presets import TextEvals, DataDriftPreset
from evidently.descriptors import (
    ContextRelevance, CompletenessLLMEval, FaithfulnessLLMEval,
    Sentiment, TextLength, RegExp,
)
from evidently.legacy.utils.llm.wrapper import OpenAIWrapper, LLMResult

#  PATCH : Force JSON Mode for Evidently LLM Judges 
_original_complete = OpenAIWrapper.complete

async def _clean_complete_with_json(self, messages):
    """S'assure que LiteLLM reçoit l'instruction JSON mode et nettoie la réponse."""
    msg_dicts = [{"role": m.role, "content": m.content} for m in messages]
    resp = await self.client.chat.completions.create(
        model=self.model,
        messages=msg_dicts,
        response_format={"type": "json_object"}
    )
    content = (resp.choices[0].message.content or "{}").strip()
    usage = resp.usage
    return LLMResult(content, usage.prompt_tokens if usage else 0, usage.completion_tokens if usage else 0)

OpenAIWrapper.complete = _clean_complete_with_json


# ── Configuration ────────────────────────────────────────────────────────────

API_URL = "http://localhost:18000/search"
REPORT_PATH = "/app/reports/e2e_logs.json"
EVAL_MODEL = "groq-qwen3"

os.environ["OPENAI_BASE_URL"] = "http://localhost:4000/v1"
os.environ["OPENAI_API_KEY"] = os.getenv("PROXY_KEY", "sk-litellm-proxy-key")
os.environ["OPENAI_TIMEOUT"] = "120"
os.environ["HTTPX_TIMEOUT"] = "120"


# ── Logging ──────────────────────────────────────────────────────────────────

TEST_LOGS: list[dict] = []

def log_qa(question: str, response: str, contexts: list, test_name: str):
    """Enregistre un échange Q&A dans les logs."""
    TEST_LOGS.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_name": test_name,
        "question": question,
        "response": response,
        "contexts": contexts,
    })

def log_error(test_name: str, error: Exception):
    """Enregistre une erreur avec sa traceback dans les logs."""
    TEST_LOGS.append({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_name": test_name,
        "status": "ERROR",
        "error": str(error),
        "traceback": traceback.format_exc(),
    })

def save_logs():
    """Persiste les logs dans un fichier JSON."""
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump(TEST_LOGS, f, indent=4)
    print(f"\n[CI] Logs sauvegardés → {REPORT_PATH}")


# ── Helpers ──────────────────────────────────────────────────────────────────
def load_golden_dataset() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "golden_dataset.json")
    with open(path) as f:
        return json.load(f)

def query_rag(query: str, k: int = 3) -> dict:
    """Appelle l'API RAG et retourne la réponse JSON."""
    return requests.post(API_URL, json={"query": query, "k": k}, timeout=120).json()


# ── Fixture : Stack RAGOPS éphémère ──────────────────────────────────────────

@pytest.fixture(scope="module", autouse=True)
def ragops_stack():
    """Monte l'architecture RAGOPS, ingère les données, puis détruit tout."""
    compose_path = os.path.join(os.path.dirname(__file__), "..")
    print("\n[CI] Démarrage de l'environnement via Testcontainers...")

    with DockerCompose(compose_path, compose_file_name="docker-compose.yml", wait=False) as compose:

        # 1. Attente du backend
        print("[CI] En attente du Backend...")
        for _ in range(60):
            try:
                if requests.get("http://localhost:18000/health", timeout=5).status_code == 200:
                    break
            except (requests.ConnectionError, requests.Timeout):
                pass
            time.sleep(3)
        else:
            pytest.fail("Le backend n'a pas démarré dans le temps imparti.")

        # 2. Ingestion des données
        print("[CI] Lancement de l'ingestion (rag_setup.py)...")
        setup_path = os.path.join(os.path.dirname(__file__), "rag_setup.py")
        for attempt in range(5):
            print(f"[CI] Tentative d'ingestion {attempt + 1}/5...")
            proc = subprocess.run(
                [sys.executable, setup_path],
                capture_output=True, text=True,
            )
            print(proc.stdout)
            if proc.returncode == 0:
                print("[CI] Ingestion réussie !")
                break
            if attempt < 4:
                print(f"[CI] Échec (code {proc.returncode}). Retry dans 15s...")
                time.sleep(15)
        else:
            pytest.fail("L'ingestion a échoué après 5 tentatives.")

        # 3. Attente de l'indexation Meilisearch
        print("[CI] Attente de l'indexation Meilisearch...")
        headers = {"Authorization": f"Bearer {os.getenv('MEILI_KEY', 'password123')}"}
        for _ in range(30):
            try:
                tasks = requests.get(
                    "http://localhost:7700/tasks?statuses=enqueued,processing",
                    headers=headers,
                ).json().get("results", [])
                if not tasks:
                    time.sleep(2)
                    break
            except Exception:
                pass
            time.sleep(2)

        print("[CI] Environnement RAGOPS prêt !")
        yield
        save_logs()

    print("\n[CI] Environnement de test détruit.")