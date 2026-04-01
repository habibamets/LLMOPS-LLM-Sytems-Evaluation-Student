import os
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.models.search import SearchRequest, DirectSearchResult, SearchResponse
from app.services.search_service import search_documents, search_chunks
from app.services.rag_service import rag_search
from nemoguardrails import LLMRails, RailsConfig

logger = logging.getLogger(__name__)
router = APIRouter()

# NeMo Guardrails initialization
os.environ["OPENAI_API_BASE"] = os.getenv("PROXY_URL", "http://litellm:4000") + "/v1"
os.environ["OPENAI_API_KEY"] = os.getenv("PROXY_KEY", "dummy")

# Load NeMo config from the nemo_config/ directory inside the app package
_nemo_config_path = Path(__file__).parent.parent / "nemo_config"
_rails_config = RailsConfig.from_path(str(_nemo_config_path))
_rails: LLMRails = None

async def get_rails() -> LLMRails:
    global _rails
    if _rails is None:
        logger.info("Initializing NeMo Guardrails (first use)...")
        # LLMRails constructor can be slow/IO-heavy
        _rails = LLMRails(_rails_config)
    return _rails

GUARDRAIL_REFUSAL = "I am an AI assistant and I cannot engage in jailbreaks or reveal secrets."

async def check_guardrails(query: str) -> str | None:
    """Run the query through NeMo Guardrails.
    Returns the guardrail refusal message if blocked, None if the query is safe."""
    try:
        rails = await get_rails()
        response = await rails.generate_async(
            messages=[{"role": "user", "content": query}]
        )
        content = response.get("content", "")
        # If NeMo returned its refusal message, the query was blocked
        if GUARDRAIL_REFUSAL in content:
            return content
        return None
    except Exception as e:
        logger.warning(f"NeMo Guardrails check failed, allowing query through: {e}")
        return None

# Routes
@router.post("/search-direct", response_model=DirectSearchResult)
async def search_direct(req: SearchRequest):
    if not req.query or req.k <= 0:
        raise HTTPException(422, "Invalid query or k")
    res = await search_documents(req.query, req.k)
    return DirectSearchResult(**res, query=req.query)

@router.post("/search-chunks")
async def search_chunks_route(req: SearchRequest):
    if not req.query or req.k <= 0:
        raise HTTPException(422, "Invalid query or k")
    return await search_chunks(req.query, req.k, req.use_embeddings)

@router.post("/search", response_model=SearchResponse)
async def rag_route(req: SearchRequest):
    if not req.query or req.k <= 0:
        raise HTTPException(422, "Invalid query or k")

    # Pre-screen with NeMo Guardrails
    blocked = await check_guardrails(req.query)
    if blocked:
        return SearchResponse(
            answer=blocked,
            chunks=[],
            total_chunks_found=0,
            cached=False,
            search_method="blocked_by_guardrails"
        )

    # Safe query → proceed with RAG pipeline
    res = await rag_search(req.query, req.k, req.use_embeddings)
    return SearchResponse(**res)
