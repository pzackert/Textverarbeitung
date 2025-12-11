"""Test 5: RAG Benchmark Suite (Large document + ingestion metrics)."""
import logging
import shutil
import time
from functools import lru_cache, partial
from pathlib import Path
import sys
from typing import Any

import pytest
import fitz

# Ensure imports resolve for src/ and benchmarks packages
root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root))
sys.path.insert(0, str(root / "src"))

from tests.test_benchmarks.utils.config import ConfigLoader, ModelConfig
from tests.test_benchmarks.utils.llm_client import LLMClient
from src.rag.config import RAGConfig
from src.rag.ingestion import IngestionPipeline
from src.rag.llm_chain import LLMChain
from src.rag.llm_provider import OllamaProvider
from src.rag.prompt_builder import PromptBuilder
from src.rag.retrieval import RetrievalEngine

logger = logging.getLogger(__name__)
DATA_DIR = Path(__file__).parent.parent / "data"
LARGE_DOCUMENT = DATA_DIR / "qbusiness-ug.pdf"
assert LARGE_DOCUMENT.exists(), "Test document missing"
BENCHMARK_CONFIG = ConfigLoader.from_project_root()
ENABLED_MODELS = BENCHMARK_CONFIG.get_enabled_models()
CONTEXT_LENGTHS = BENCHMARK_CONFIG.context_length

EXPECTED_KEYWORDS = ["amazon", "user guide", "aws", "q business", "qbusiness"]


@lru_cache(maxsize=1)
def _load_pdf_excerpt(max_chars: int) -> str:
    """Extract a text excerpt from the large PDF for direct LLM prompts."""
    with fitz.open(str(LARGE_DOCUMENT)) as doc:
        text_chunks = []
        collected = 0
        for page in doc:
            page_text = page.get_text()
            if not page_text.strip():
                continue
            to_take = max_chars - collected
            if to_take <= 0:
                break
            snippet = page_text[:to_take]
            text_chunks.append(snippet)
            collected += len(snippet)
            if collected >= max_chars:
                break
    return "\n".join(text_chunks)[:max_chars]


def _matches_keywords(text: str) -> bool:
    lower = text.lower()
    return any(keyword in lower for keyword in EXPECTED_KEYWORDS)


def _build_chain(
    ingestion_pipeline: IngestionPipeline,
    rag_config: RAGConfig,
    config_overrides: dict[str, Any] | None = None,
) -> LLMChain:
    metadata_filter = {"doc_id": LARGE_DOCUMENT.stem}
    config = rag_config if not config_overrides else rag_config.model_copy(update=config_overrides)
    retrieval_engine = RetrievalEngine(
        vector_store=ingestion_pipeline.vector_store,
        config=config,
    )
    retrieval_engine.retrieve = partial(
        retrieval_engine.retrieve,
        metadata_filter=metadata_filter,
    )
    prompt_builder = PromptBuilder(retrieval_engine=retrieval_engine)
    # Override template context so we focus on the document of interest
    prompt_builder.config = config
    prompt_builder.build_query_prompt = partial(
        prompt_builder.build_query_prompt,
        metadata_filter=metadata_filter,
    )
    llm_provider = OllamaProvider(
        model_name=config.llm_model,
        base_url=config.llm_base_url,
    )
    return LLMChain(
        retrieval_engine=retrieval_engine,
        llm_provider=llm_provider,
        prompt_builder=prompt_builder,
        config=config,
    )


@pytest.fixture(scope="module")
def rag_test_config(tmp_path_factory):
    base_config = RAGConfig.from_yaml()
    temp_dir = tmp_path_factory.mktemp("rag_bench")
    return base_config.model_copy(
        update={
            "persist_directory": str(temp_dir),
            "vector_store_path": str(temp_dir),
            "collection_name": f"benchmark_rag_{int(time.time())}",
        }
    )


@pytest.fixture(scope="module")
def ingestion_pipeline(rag_test_config: RAGConfig):
    pipeline = IngestionPipeline(config=rag_test_config)
    yield pipeline
    try:
        pipeline.vector_store.clear_collection()
    except Exception as exc:
        logger.warning(f"Failed to clear test collection: {exc}")
    try:
        shutil.rmtree(rag_test_config.vector_store_path, ignore_errors=True)
    except Exception as exc:
        logger.warning(f"Failed to remove vector store directory: {exc}")


@pytest.fixture(scope="module")
def ingestion_result(ingestion_pipeline: IngestionPipeline):
    start = time.time()
    result = ingestion_pipeline.ingest_file(str(LARGE_DOCUMENT))
    result["metrics"] = {"duration_s": round(time.time() - start, 2)}
    return result


class TestRAGBenchmark:
    """Tests 5a-5f: LLM baseline + RAG ingestion/query workflow."""

    @pytest.mark.parametrize("model_config", ENABLED_MODELS)
    def test_05a_direct_llm_baseline(self, model_config: ModelConfig):
        client = LLMClient(model_config.name)
        if not client.check_availability():
            pytest.skip(f"Model {model_config.name} not available for direct benchmark")

        excerpt = _load_pdf_excerpt(max(CONTEXT_LENGTHS))
        prompt_base = (
            "Hier ist ein Dokumentauszug von Amazon Q Business:\n"
            "{excerpt}\n\n"
            "Frage: Worum geht es im Amazon Q Business User Guide?"
        )

        for length in CONTEXT_LENGTHS:
            truncated = excerpt[:length]
            prompt = prompt_base.format(excerpt=truncated)
            result = client.query(prompt, temperature=0.5, max_tokens=256)

            if not result["success"]:
                pytest.skip(f"Direct LLM query failed for {model_config.name}: HTTP 500 or timeout")
            assert result["response"], "Direkter LLM-Output ist leer"
            metrics = result["metrics"]
            assert metrics, "Metrics für direkte LLM-Abfrage fehlen"
            assert metrics.response_time_s > 0

            assert _matches_keywords(result["response"]), (
                "Die Antwort enthält keine Hinweise auf Amazon oder Q Business"
            )

    def test_05b_rag_ingestion_metrics(self, ingestion_result: dict):
        assert ingestion_result["success"], "RAG-Ingestion schlug fehl"
        assert ingestion_result["chunk_count"] > 0, "Keine Chunks erzeugt"
        assert ingestion_result["metrics"]["duration_s"] >= 0

    def test_05c_vector_store_retrieval(self, ingestion_pipeline: IngestionPipeline, ingestion_result: dict):
        results = ingestion_pipeline.vector_store.query(
            query_text="Was beschreibt das Amazon Q Business User Guide?",
            top_k=10,
            metadata_filter={"doc_id": LARGE_DOCUMENT.stem},
        )
        assert results, "Keine Retrieval-Ergebnisse gefunden"
        assert any(
            LARGE_DOCUMENT.name == r["metadata"].get("doc_name") for r in results
        ), "Metadata enthält nicht den erwarteten Dateinamen"
        assert all(r["score"] >= 0 for r in results)

    def test_05d_rag_query_with_citations(self, ingestion_pipeline: IngestionPipeline, rag_test_config: RAGConfig):
        chain = _build_chain(
            ingestion_pipeline,
            rag_test_config,
            config_overrides={"llm_max_tokens": 512},
        )
        if not chain.llm_provider.is_available():
            pytest.skip("LLM-Provider für RAG-Anfrage nicht erreichbar")

        question = "Fasse in drei Sätzen zusammen, worum es im Amazon Q Business User Guide geht."
        try:
            response = chain.query(question, template_type="summary")
        except ConnectionError as exc:
            pytest.skip(f"Ollama timeout during RAG query: {exc}")

        assert response["answer"], "RAG-Antwort ist leer"
        assert response["sources"], "Es wurden keine Quellen abgerufen"
        assert _matches_keywords(response["answer"])
        assert response["metadata"]["chunks_retrieved"] > 0

    def test_05e_baseline_vs_rag(self, ingestion_pipeline: IngestionPipeline, rag_test_config: RAGConfig):
        model = ENABLED_MODELS[0]
        client = LLMClient(model.name)
        if not client.check_availability():
            pytest.skip("Baseline-Modell nicht erreichbar für Vergleich")

        excerpt = _load_pdf_excerpt(max(CONTEXT_LENGTHS))[:4096]
        prompt = (
            "Auszug:\n{excerpt}\n\nWas ist der Zweck dieses Dokuments?"
        ).format(excerpt=excerpt)
        baseline = client.query(prompt, temperature=0.4, max_tokens=200)
        assert baseline["success"], "Baseline-LLM-Abfrage fehlgeschlagen"

        chain = _build_chain(
            ingestion_pipeline,
            rag_test_config,
            config_overrides={"llm_max_tokens": 512},
        )
        if not chain.llm_provider.is_available():
            pytest.skip("LLM-Provider für RAG-Frage nicht erreichbar")

        rag_result = chain.query(
            "Worum geht es im Amazon Q Business User Guide?",
            template_type="standard",
        )
        assert rag_result["metadata"]["duration"] > 0
        assert rag_result["metadata"]["chunks_retrieved"] > 0
        assert rag_result["sources"], "RAG hat keine Quellen geliefert"
        if not rag_result["citations"]:
            logger.warning("RAG beantwortete die Frage ohne explizite Quellenmarkierung")
        assert _matches_keywords(rag_result["answer"])

    def test_05f_context_length_coverage(self, ingestion_pipeline: IngestionPipeline, ingestion_result: dict):
        assert max(CONTEXT_LENGTHS) >= 16384, "Kontextlängenliste muss mindestens 16K enthalten"
        total_chunks = ingestion_result["chunk_count"]
        for length in CONTEXT_LENGTHS:
            top_k = max(1, int(length / 500) + 2)
            results = ingestion_pipeline.vector_store.query(
                query_text="Amazon Q Business",
                top_k=top_k,
                metadata_filter={"doc_id": LARGE_DOCUMENT.stem},
            )
            assert results, f"Keine Retrieval-Ergebnisse für Kontextlänge {length}"
            expected = min(total_chunks, top_k)
            assert len(results) == expected, (
                f"Erwartete {expected} Chunks, aber {len(results)} erhalten"
            )
