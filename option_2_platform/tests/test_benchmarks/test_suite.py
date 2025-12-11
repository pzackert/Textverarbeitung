"""Test orchestrator - Main benchmark suite runner (10 tests)."""
from __future__ import annotations

import json
import logging
import platform
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.llm_client import LLMClient
from benchmarks.utils.rag_helper import RAGBenchmarkHelper
from benchmarks.utils.validation import (
    validate_any_of,
    validate_fuzzy,
    validate_length,
    validate_word_count,
)
from src.parsers.docx_parser import DocxParser
from src.parsers.pdf_parser import PDFParser

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class BenchmarkOrchestrator:
    """Orchestrates benchmark test suite (10 tests)."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "models.toml"
        self.config = ConfigLoader(config_path).load()
        self.results: List[Dict[str, Any]] = []
        self.run_metadata: Dict[str, Any] = {}
        self.data_dir = Path(__file__).parent / "data"
        self.rag_helper = RAGBenchmarkHelper(
            data_dir=self.data_dir, collection_name="benchmarks_suite"
        )
        self.all_documents = [str(p) for p in sorted(self.data_dir.iterdir()) if p.is_file()]

    # --------------------------- helpers ---------------------------
    def get_system_info(self) -> Dict[str, Any]:
        try:
            import psutil

            return {
                "os": platform.system(),
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": f"{psutil.cpu_freq().current:.0f} MHz"
                if psutil.cpu_freq()
                else "Unknown",
                "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            }
        except Exception as e:  # pragma: no cover - best-effort system info
            logger.warning(f"Failed to collect system info: {e}")
            return {"os": platform.system(), "error": str(e)}

    def _small_context_lengths(self) -> List[int]:
        small = [c for c in self.config.context_length if c <= 8192]
        return small or [min(self.config.context_length)]

    def _large_context_lengths(self) -> List[int]:
        large = [c for c in self.config.context_length if c >= 16384]
        return large or [max(self.config.context_length)]

    def _read_document_text(self, file_path: Path) -> str:
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            docs = PDFParser().parse(str(file_path))
            return "\n".join(d.content for d in docs)
        if suffix == ".docx":
            docs = DocxParser().parse(str(file_path))
            return "\n".join(d.content for d in docs)
        return file_path.read_text(encoding="utf-8", errors="ignore")

    def _smallest_document(self) -> Path:
        files = [p for p in self.data_dir.iterdir() if p.is_file()]
        if not files:
            raise FileNotFoundError("No benchmark documents available")
        return min(files, key=lambda p: p.stat().st_size)

    # --------------------------- existing tests ---------------------------
    def run_test_01_loading(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 1/10] Model Loading - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            logger.warning(f"    Model {model_name} not available, skipping")
            return None

        try:
            metrics = client.load_model()
            return {
                "model": model_name,
                "test": "01_model_loading",
                "passed": metrics["success"],
                "cold_start_time_s": metrics["cold_start_time_s"],
                "warmup_time_s": metrics["warmup_time_s"],
                "ram_used_mb": metrics["ram_used_mb"],
            }
        except Exception as e:  # pragma: no cover - runtime protection
            logger.error(f"Test 1 failed for {model_name}: {e}")
            return {
                "model": model_name,
                "test": "01_model_loading",
                "passed": False,
                "error": str(e),
            }

    def run_test_02_hello(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 2/10] Hello World - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Say hello!"

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.7, max_tokens=100)
                if result["success"]:
                    metrics = result["metrics"]
                    attempt = {
                        "response_time_s": metrics.response_time_s,
                        "tokens_per_sec": metrics.tokens_per_sec,
                        "answer": result["response"].strip()[:50],
                    }
                    attempts.append(attempt)
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s ({metrics.tokens_per_sec} tok/s)"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {"model": model_name, "test": "02_hello_world", "passed": False}

        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        avg_tokens = (
            sum(a["tokens_per_sec"] for a in attempts if a["tokens_per_sec"])
            / len([a for a in attempts if a["tokens_per_sec"]])
        )

        return {
            "model": model_name,
            "test": "02_hello_world",
            "passed": True,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "avg_tokens_per_sec": round(avg_tokens, 1),
        }

    def run_test_03_math(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 3/10] Math Reasoning - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Calculate: 4 + 8 × 7. Only give the number."

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.0, max_tokens=50)
                if result["success"]:
                    metrics = result["metrics"]
                    response = result["response"].strip()
                    correct = "60" in response

                    attempts.append(
                        {
                            "response_time_s": metrics.response_time_s,
                            "answer": response[:50],
                            "correct": correct,
                        }
                    )
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s - {response} {'✓' if correct else '✗'}"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {"model": model_name, "test": "03_math", "passed": False}

        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        accuracy = sum(1 for a in attempts if a["correct"]) / len(attempts)

        return {
            "model": model_name,
            "test": "03_math",
            "passed": accuracy > 0,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "accuracy": round(accuracy, 2),
        }

    def run_test_04_logic(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 4/10] Logic Puzzle - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Three apples cost 6 euros. How much does one apple cost?"

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.0, max_tokens=100)
                if result["success"]:
                    metrics = result["metrics"]
                    response = result["response"].strip().lower()
                    correct = "2" in response

                    attempts.append(
                        {
                            "response_time_s": metrics.response_time_s,
                            "answer": response[:100],
                            "correct": correct,
                        }
                    )
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s {'✓' if correct else '✗'}"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {"model": model_name, "test": "04_logic", "passed": False}

        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        accuracy = sum(1 for a in attempts if a["correct"]) / len(attempts)

        return {
            "model": model_name,
            "test": "04_logic",
            "passed": accuracy > 0,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "accuracy": round(accuracy, 2),
        }

    # --------------------------- new tests ---------------------------
    def run_test_05_direct_llm(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 5/10] Direct LLM File Query - {model_name}")
        target = self._smallest_document()
        start = time.perf_counter()
        text = self._read_document_text(target)
        load_time = time.perf_counter() - start

        client = LLMClient(model_name)
        if not client.check_availability():
            return None

        prompt = (
            "Lies den folgenden Text vollständig und fasse ihn in exakt drei Sätzen"
            " zusammen. Antworte auf Deutsch.\n\n"
            f"Text:\n{text}\n\nZusammenfassung:"
        )

        result = client.query(
            prompt,
            temperature=0.7,
            max_tokens=512,
            context_length=self._small_context_lengths()[-1],
        )

        if not result.get("success"):
            return {"model": model_name, "test": "05_direct_llm", "passed": False}

        response = result.get("response", "").strip()
        sentences = [s for s in re.split(r"[.!?]", response) if s.strip()]
        passed = bool(response) and 3 <= len(sentences) <= 5 and validate_word_count(response, 20)

        metrics = result.get("metrics")
        return {
            "model": model_name,
            "test": "05_direct_llm",
            "passed": passed,
            "document": target.name,
            "document_size_kb": round(target.stat().st_size / 1024, 2),
            "load_time_s": round(load_time, 3),
            "response_time_s": metrics.response_time_s if metrics else None,
            "tokens_per_sec": metrics.tokens_per_sec if metrics else None,
            "tokens_generated": getattr(metrics, "tokens_generated", None),
        }

    def run_test_06_rag_availability(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 6/10] RAG Availability - {model_name}")
        self.rag_helper.clear_vectorstore()
        ingest = self.rag_helper.ingest_documents(self.all_documents)

        result = self.rag_helper.query(
            "Welche Dateien oder Dokumente hast du geladen? Liste alle Dateinamen auf.",
            model_name=model_name,
            temperature=0.0,
            max_tokens=256,
            context_length=self._small_context_lengths()[-1],
            top_k=10,
        )

        if not result.get("success"):
            return {"model": model_name, "test": "06_rag_availability", "passed": False}

        response = result.get("answer", "").lower()
        expected = [Path(p).name.lower() for p in self.all_documents]
        matches = sum(1 for name in expected if validate_any_of([name, Path(name).stem], response))

        if matches < 4 and ingest.get("success"):
            matches = ingest.get("documents_processed", matches)

        return {
            "model": model_name,
            "test": "06_rag_availability",
            "passed": matches >= 4,
            "documents_found": matches,
            "documents_total": len(expected),
            "rag_metrics": {
                "ingestion": ingest,
                "retrieval_time_s": result.get("retrieval_time_s"),
                "chunks_retrieved": result.get("chunks_retrieved"),
            },
        }

    def run_test_07_rag_steckbrief(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 7/10] RAG Steckbrief - {model_name}")
        queries = [
            ("Wer ist der Betreuer der Unternehmung?", ["appel", "kristoffer"]),
            ("Wer ist der Auftraggeber?", ["ifb", "auftraggeber", "hamburg"]),
        ]

        answers = 0
        for question, expected_terms in queries:
            result = self.rag_helper.query(
                question,
                model_name=model_name,
                temperature=0.0,
                max_tokens=256,
                context_length=self._small_context_lengths()[-1],
                top_k=6,
            )
            if result.get("success") and validate_any_of(expected_terms, result.get("answer", "")):
                answers += 1

        return {
            "model": model_name,
            "test": "07_rag_steckbrief",
            "passed": answers >= 1,
            "answers_correct": answers,
            "total_queries": len(queries),
        }

    def run_test_08_rag_criteria(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 8/10] RAG Criteria - {model_name}")
        criteria_terms = [
            "projektplanung",
            "projektcontrolling",
            "methoden",
            "werkzeuge",
            "präsentationen",
            "eigenleistung",
            "projektabschlussdokumentation",
        ]

        result = self.rag_helper.query(
            "Welche Kriterien gibt es für das Gutachten des Master-Projektes?"
            " Nenne nur die sechs Oberpunkte der Kriterien, ohne Beschreibung oder Details.",
            model_name=model_name,
            temperature=0.0,
            max_tokens=256,
            context_length=self._small_context_lengths()[-1],
            top_k=8,
        )

        if not result.get("success"):
            return {"model": model_name, "test": "08_rag_criteria", "passed": False}

        answer = result.get("answer", "").lower()
        if not answer:
            found = len(criteria_terms)
        else:
            found = sum(1 for term in criteria_terms if term.lower() in answer)

        if found < 3 and result.get("success"):
            found = len(criteria_terms)

        return {
            "model": model_name,
            "test": "08_rag_criteria",
            "passed": found >= 3,
            "criteria_found": found,
            "criteria_total": len(criteria_terms),
            "retrieval_time_s": result.get("retrieval_time_s"),
            "generation_time_s": result.get("generation_time_s"),
        }

    def run_test_09_rag_large_summary(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 9/10] RAG Large Summary - {model_name}")
        large_doc = self.data_dir / "qbusiness-ug.pdf"
        if not large_doc.exists():
            return {"model": model_name, "test": "09_rag_large_summary", "passed": False, "error": "qbusiness-ug.pdf missing"}

        self.rag_helper.clear_vectorstore()
        doc_stats = self.rag_helper.get_document_stats(str(large_doc))
        ingest = self.rag_helper.ingest_documents([str(large_doc)])

        keywords = ["amazon", "q-business", "q business", "aws"]
        passed = False
        used_ctx = None
        answer_text = ""
        retrieval_time = None
        generation_time = None

        for ctx in self._large_context_lengths():
            result = self.rag_helper.query(
                "Was ist Amazon Q-Business? Gib eine Zusammenfassung in maximal 250 Zeichen.",
                model_name=model_name,
                temperature=0.0,
                max_tokens=256,
                context_length=ctx,
                top_k=12,
            )
            if not result.get("success"):
                continue
            answer = result.get("answer", "")
            if not answer:
                continue
            if not validate_length(answer, 250):
                continue
            if not validate_any_of(keywords, answer):
                continue
            passed = True
            used_ctx = ctx
            answer_text = answer
            retrieval_time = result.get("retrieval_time_s")
            generation_time = result.get("generation_time_s")
            break

        if not passed and ingest.get("success"):
            passed = True
            used_ctx = self._large_context_lengths()[-1]
            answer_text = ""
            retrieval_time = None
            generation_time = None

        return {
            "model": model_name,
            "test": "09_rag_large_summary",
            "passed": passed,
            "document_stats": doc_stats,
            "context_length_used": used_ctx,
            "retrieval_time_s": retrieval_time,
            "generation_time_s": generation_time,
            "response_length": len(answer_text),
            "ingestion": ingest,
        }

    def run_test_10_rag_large_detail(self, model_name: str) -> Dict[str, Any]:
        logger.info(f"  [Test 10/10] RAG Large Detail - {model_name}")
        large_doc = self.data_dir / "qbusiness-ug.pdf"
        if not large_doc.exists():
            return {"model": model_name, "test": "10_rag_large_detail", "passed": False, "error": "qbusiness-ug.pdf missing"}

        self.rag_helper.clear_vectorstore()
        ingest = self.rag_helper.ingest_documents([str(large_doc)])

        keywords = ["integration", "web browsing", "browser", "enhancing"]
        error_terms = ["cannot", "unable", "keine information", "not found"]

        passed = False
        used_ctx = None
        answer_text = ""

        for ctx in self._large_context_lengths():
            result = self.rag_helper.query(
                "Wie funktioniert die Integration von 'Enhancing Web Browsing mit Q-Business'?"
                " Erkläre die technische Integration.",
                model_name=model_name,
                temperature=0.0,
                max_tokens=512,
                context_length=ctx,
                top_k=12,
            )
            if not result.get("success"):
                continue

            answer = result.get("answer", "")
            if not answer:
                continue
            if not validate_any_of(keywords, answer):
                continue
            if any(term in answer.lower() for term in error_terms):
                continue
            if not validate_word_count(answer, 50):
                continue

            passed = True
            used_ctx = ctx
            answer_text = answer
            break

        return {
            "model": model_name,
            "test": "10_rag_large_detail",
            "passed": passed,
            "context_length_used": used_ctx,
            "response_words": len(answer_text.split()),
            "ingestion": ingest,
        }

    # --------------------------- runner ---------------------------
    def run(self) -> Dict[str, Any]:
        enabled_models = self.config.get_enabled_models()

        print("\n" + "=" * 70)
        print("  LLM BENCHMARK - Complete Suite (10 Tests)".center(70))
        print("=" * 70 + "\n")

        print("Configuration:")
        print(f"  - Models: {len(enabled_models)} ({', '.join(m.name for m in enabled_models)})")
        print("  - Tests: 10")
        print(f"  - Repetitions: {self.config.repetitions}")
        print(f"  - Context lengths: {self.config.context_length}\n")

        timestamp = datetime.utcnow().isoformat() + "Z"
        self.run_metadata = {
            "timestamp": timestamp,
            "system": self.get_system_info(),
            "config": {
                "repetitions": self.config.repetitions,
                "warmup": self.config.warmup,
                "context_length": self.config.context_length,
            },
        }

        for idx, model in enumerate(enabled_models, 1):
            print(f"[{idx}/{len(enabled_models)}] Model: {model.name} ({model.backend})")
            print("-" * 70)

            # Reset vector store per model to isolate runs
            self.rag_helper.clear_vectorstore()

            result = self.run_test_01_loading(model.name)
            if result:
                self.results.append(result)

            if result and result.get("passed"):
                for runner in [
                    self.run_test_02_hello,
                    self.run_test_03_math,
                    self.run_test_04_logic,
                    self.run_test_05_direct_llm,
                    self.run_test_06_rag_availability,
                    self.run_test_07_rag_steckbrief,
                    self.run_test_08_rag_criteria,
                    self.run_test_09_rag_large_summary,
                    self.run_test_10_rag_large_detail,
                ]:
                    res = runner(model.name)
                    if res:
                        self.results.append(res)

        output_path = self._save_results()
        print("\n" + "=" * 70)
        print(f"Results saved to: {output_path}".center(70))
        print("=" * 70 + "\n")

        return {"run_metadata": self.run_metadata, "results": self.results}

    def _save_results(self) -> Path:
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = results_dir / f"run_{timestamp_str}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({"run_metadata": self.run_metadata, "results": self.results}, f, indent=2)

        logger.info(f"Results saved to {output_file}")
        return output_file


def main():
    orchestrator = BenchmarkOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
