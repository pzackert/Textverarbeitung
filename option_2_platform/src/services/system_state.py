from typing import Dict, Any, List, Set
import asyncio
import logging
import time
import os
from pathlib import Path
from enum import Enum
from src.core.config import load_config
from src.rag.config import RAGConfig
from src.services.model_scanner import scan_all_models
import requests

logger = logging.getLogger(__name__)

class ComponentStatus(str, Enum):
    PENDING = "pending"
    LOADING = "loading"
    READY = "ready"
    ERROR = "error"
    SKIPPED = "skipped"

class ComponentState:
    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name
        self.status = ComponentStatus.PENDING
        self.progress = 0
        self.message = "Wartet..."
        self.duration_sec = 0.0
        self.start_time = None

    def start(self):
        self.status = ComponentStatus.LOADING
        self.start_time = time.time()
        self.message = "Wird gestartet..."

    def complete(self, message: str = "Bereit"):
        self.status = ComponentStatus.READY
        self.progress = 100
        self.message = message
        if self.start_time:
            self.duration_sec = round(time.time() - self.start_time, 2)

    def fail(self, error: str):
        self.status = ComponentStatus.ERROR
        self.message = error
        if self.start_time:
            self.duration_sec = round(time.time() - self.start_time, 2)
            
    def skip(self):
        self.status = ComponentStatus.SKIPPED
        self.message = "Übersprungen"

class SystemStateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemStateManager, cls).__new__(cls)
            # Default to ready in test/dev mode; startup sequence can reset this.
            cls._instance.status = "ready"
            cls._instance.current_step = 0
            cls._instance.total_steps = 7
            cls._instance.current_action = "System wird initialisiert..."
            cls._instance.start_time = time.time()
            
            # Ordered components list for strict sequence (User Requirement: 6 Components)
            cls._instance.components = {
                "model_scanner": ComponentState("model_scanner", "Model Scanner"),
                "ai_provider": ComponentState("ai_provider", "AI Provider Check"),
                "vector_store": ComponentState("vector_store", "Vector Store (ChromaDB)"),
                "llm_loading": ComponentState("llm_loading", "LLM Model Loading"),
                "global_knowledge": ComponentState("global_knowledge", "Global Knowledge (RAG)"),
                "project_healing": ComponentState("project_healing", "Project Healing")
            }
        return cls._instance

    def get_status_dict(self) -> Dict[str, Any]:
        """
        Returns status in the format expected by the frontend:
        {
          "status": "initializing" | "ready" | "error",
          "step": 3,
          "total_steps": 5,
          "components": [...],
          "current": "Loading model..."
        }
        """
        comps_list = []
        for key in ["model_scanner", "ai_provider", "vector_store", "llm_loading", "global_knowledge", "project_healing"]:
            comp = self.components[key]
            comps_list.append({
                "name": comp.name,
                "display_name": comp.display_name,
                "status": comp.status,
                "progress": comp.progress,
                "message": comp.message,
                "duration_sec": comp.duration_sec
            })

        return {
            "status": self.status,
            "step": self.current_step,
            "total_steps": self.total_steps,
            "components": comps_list, # Array for frontend ordering
            "components_dict": {k: v.__dict__ for k, v in self.components.items()}, # Dict for easy lookup
            "current": self.current_action,
            "total_duration_sec": round(time.time() - self.start_time, 1)
        }

    def reset(self):
        self.status = "initializing"
        self.current_step = 0
        self.start_time = time.time()
        self.current_action = "System wird initialisiert..."
        for comp in self.components.values():
            comp.status = ComponentStatus.PENDING
            comp.progress = 0
            comp.message = "Wartet..."
            comp.duration_sec = 0.0

    def _dir_size_mb(self, path: Path) -> float:
        total = 0
        if not path.exists():
            return 0.0
        for root, _, files in os.walk(path):
            for f in files:
                try:
                    total += (Path(root) / f).stat().st_size
                except OSError:
                    continue
        return round(total / (1024 * 1024), 1)

    def _vector_store_stats(self, vector_store: Any, persist_directory: str) -> Dict[str, Any]:
        stats: Dict[str, Any] = {
            "chunk_count": 0,
            "doc_count": 0,
            "size_mb": 0.0,
            "path": persist_directory,
        }
        try:
            stats["chunk_count"] = vector_store.collection.count()
        except Exception:
            stats["chunk_count"] = 0

        try:
            meta_result = vector_store.collection.get(include=["metadatas"], limit=None)
            metas = meta_result.get("metadatas") or []
            if metas and isinstance(metas[0], list):
                metas = metas[0]
            doc_ids: Set[str] = set()
            for meta in metas:
                if not isinstance(meta, dict):
                    continue
                doc_key = meta.get("document_id") or meta.get("source") or meta.get("file_name")
                if doc_key:
                    doc_ids.add(str(doc_key))
            stats["doc_count"] = len(doc_ids)
        except Exception:
            stats["doc_count"] = 0

        stats["size_mb"] = self._dir_size_mb(Path(persist_directory))
        return stats
    async def _verify_llm_background(
        self, 
        target_model: str, 
        llm_conf: Any, 
        timeout: int,
        active_provider: str,
        lm_studio_url: str
    ):
        """
        Verify LLM availability with retries and progress updates.
        """
        logger.info(f"LLM Check started for {target_model} (Timeout: {timeout}s)")
        comp_model = self.components["llm_loading"]
        comp_model.status = ComponentStatus.LOADING
        comp_model.message = f"Lade Modell {target_model} ({active_provider})..."
        
        start_time = time.time()
        attempt = 1
        
        loop = asyncio.get_event_loop()
        
        while (time.time() - start_time) < timeout:
            try:
                # Determine URL and Payload based on active provider
                base_url = lm_studio_url if active_provider == "lm_studio" else (llm_conf.ollama.endpoint or "http://localhost:11434")
                api_endpoint = f"{base_url}/v1/chat/completions" if active_provider == "lm_studio" else f"{base_url}/api/generate"
                
                if active_provider == "lm_studio":
                    payload = {
                        "model": target_model,
                        "messages": [{"role": "user", "content": "Say OK"}],
                        "max_tokens": 5
                    }
                else:
                    payload = {
                        "model": target_model,
                        "prompt": "Say OK",
                        "stream": False
                    }

                # Run blocking request in thread
                resp = await loop.run_in_executor(
                    None, 
                    lambda: requests.post(api_endpoint, json=payload, timeout=30)
                )
                
                if resp.status_code == 200:
                    comp_model.complete(f"Modell geladen ✓ ({active_provider})")
                    logger.info(f"LLM {target_model} successfully loaded via {active_provider}")
                    return
                else:
                    logger.warning(f"LLM Check Attempt {attempt} failed: {resp.status_code}")
                    comp_model.message = f"Laden... (Versuch {attempt}: Fehler {resp.status_code})"
                    comp_model.progress = min(95, int(((time.time() - start_time) / timeout) * 100))
                    
            except Exception as e:
                logger.warning(f"LLM Check Attempt {attempt} connection error: {e}")
                comp_model.message = f"Laden... (Versuch {attempt}: Verbindung...)"
                comp_model.progress = min(95, int(((time.time() - start_time) / timeout) * 100))
            
            attempt += 1
            await asyncio.sleep(5) 

        # Final Failure
        comp_model.fail(f"Zeitüberschreitung beim Laden des Modells ({timeout}s)")
        if self.status != "error":
             self.status = "degraded"
        logger.error("LLM Check failed after global timeout.")

system_state = SystemStateManager()


async def run_startup_sequence():
    """
    Robust 6-Step Startup Sequence as per User Requirement.
    """
    logger.info("Starting robust system initialization (6 Steps)...")
    raw_config = load_config()
    startup_conf = raw_config.get("startup", {})
    rag_config = RAGConfig.from_yaml()
    llm_conf = rag_config.llm
    
    timeout = llm_conf.timeout or 180
    
    # Reset state
    system_state.reset()
    system_state.total_steps = 6
    
    try:
        # --- Step 1: Model Scanner ---
        system_state.current_step = 1
        system_state.current_action = "Schritt 1/6: Scanne Modelle"
        comp_scan = system_state.components["model_scanner"]
        comp_scan.start()
        comp_scan.message = "Modelle werden gescannt..."

        scan_results = scan_all_models(llm_conf)
        model_count = len(scan_results) if scan_results else 0

        if model_count > 0:
            comp_scan.complete(f"{model_count} Modelle gefunden")
        else:
            comp_scan.fail("Kein Modell vorhanden - Bitte installieren Sie ein Modell")
            system_state.status = "degraded"

        # --- Step 2: AI Provider Check ---
        system_state.current_step = 2
        system_state.current_action = "Schritt 2/6: Prüfe AI Provider"
        comp_prov = system_state.components["ai_provider"]
        comp_prov.start()
        comp_prov.message = "Prüfe LM Studio und Ollama..."

        lm_studio_url = llm_conf.lm_studio.endpoint or "http://127.0.0.1:1234"
        ollama_url = llm_conf.ollama.endpoint or "http://localhost:11434"
        
        lm_available = False
        ollama_available = False
        
        # Check LM Studio
        try:
            r = requests.get(f"{lm_studio_url}/v1/models", timeout=2)
            if r.status_code == 200: lm_available = True
        except Exception as exc:
            logger.debug(f"LM Studio check failed: {exc}")
        
        # Check Ollama
        try:
            r = requests.get(f"{ollama_url}/api/tags", timeout=2)
            if r.status_code == 200: ollama_available = True
        except Exception as exc:
            logger.debug(f"Ollama check failed: {exc}")
        
        active_provider = "lm_studio" if lm_available else ("ollama" if ollama_available else None)
        target_model = llm_conf.model or "unknown"

        if active_provider:
             msg = "2 Provider verfügbar (LM Studio bevorzugt)" if (lm_available and ollama_available) else f"1 Provider verfügbar ({'LM Studio' if lm_available else 'Ollama'})"
             comp_prov.complete(msg)
        else:
             comp_prov.fail("Kein Provider erreichbar - Degraded Mode aktiv")
             system_state.status = "degraded"

        # --- Step 3: Vector Store ---
        system_state.current_step = 3
        system_state.current_action = "Schritt 3/6: Vector Store verbinden"
        comp_vs = system_state.components["vector_store"]
        comp_vs.start()
        comp_vs.message = "ChromaDB wird initialisiert..."
        
        try:
            from src.rag.vector_store import VectorStore
            rag_conf = raw_config.get("rag", {})
            col_name = rag_conf.get("collection_name", "ifb_documents")
            persist_dir = rag_conf.get("persist_directory", "data/chromadb")
            vs = VectorStore(
                collection_name=col_name,
                persist_directory=persist_dir
            )
            vs_stats = system_state._vector_store_stats(vs, persist_dir)
            comp_vs.complete(
                f"ChromaDB verbunden - {vs_stats['doc_count']} Dokumente, {vs_stats['chunk_count']} Chunks, {vs_stats['size_mb']} MB ({persist_dir})"
            )
            comp_vs.progress = 100
        except Exception as e:
            comp_vs.fail(f"ChromaDB Verbindung fehlgeschlagen: {str(e)}")
            system_state.status = "error"

        # --- Step 4: LLM Model Loading ---
        system_state.current_step = 4
        system_state.current_action = "Schritt 4/6: Lade LLM"
        comp_llm = system_state.components["llm_loading"]
        if active_provider:
            comp_llm.start()
            comp_llm.progress = 10
            comp_llm.message = f"Lade Modell {target_model} ({active_provider})..."
            await system_state._verify_llm_background(
                target_model, llm_conf, timeout, active_provider, lm_studio_url
            )
        else:
            comp_llm.skip()

        # --- Step 5: Global Knowledge (RAG) ---
        system_state.current_step = 5
        system_state.current_action = "Schritt 5/6: Global Knowledge"
        comp_rag = system_state.components["global_knowledge"]
        comp_rag.start()
        comp_rag.message = "Globales Wissen wird indexiert..."
        
        try:
            from src.rag.vector_store import VectorStore
            rag_conf = raw_config.get("rag", {})
            vector_store = VectorStore(
                collection_name=rag_conf.get("collection_name", "ifb_documents"),
                persist_directory=rag_conf.get("persist_directory", "data/chromadb")
            )
            global_dir = Path("data/global_knowledge")
            doc_names = [p.name for p in global_dir.iterdir() if p.is_file()] if global_dir.exists() else []
            chunk_count = vector_store.count_by_metadata({"type": "global_knowledge"})

            if chunk_count == 0 and not doc_names:
                comp_rag.complete("Kein globales Wissen vorhanden - Bitte Dokumente hochladen")
            elif chunk_count == 0 and doc_names:
                from src.api.routers.rag_global import start_background_load
                start_background_load() # Runs in thread
                comp_rag.complete(f"Indexierung gestartet ({len(doc_names)} Dateien)")
            else:
                preview = ", ".join(doc_names[:3]) if doc_names else ""
                extra = f" | Dateien: {preview}" if preview else ""
                comp_rag.complete(f"{chunk_count} Chunks aus globalem Wissen geladen{extra}")
        except Exception as e:
            comp_rag.fail(f"Indexierung fehlgeschlagen: {str(e)}")
            system_state.status = "degraded"

        # --- Step 6: Project Healing ---
        system_state.current_step = 6
        system_state.current_action = "Schritt 6/6: Prüfe Projekte"
        comp_proj = system_state.components["project_healing"]
        comp_proj.start()
        comp_proj.message = "Projektstruktur wird geprüft..."
        
        try:
            from src.services.project_service import project_service
            reports = project_service.heal_all_projects()
            healed = len(reports)
            comp_proj.complete(f"{healed} Anträge verfügbar")
        except Exception as e:
            comp_proj.fail(f"Projektstruktur-Fehler: {str(e)}")
            system_state.status = "error"
            
        # --- Finalize ---
        if system_state.status not in ["degraded", "error"]:
            system_state.status = "ready"
            
        system_state.current_action = "Startup abgeschlossen"
        logger.info(f"Startup sequence finished. Final Status: {system_state.status}")

    except Exception as e:
        logger.error(f"Startup crash: {e}")
        system_state.status = "error"
        system_state.current_action = f"Kritischer Fehler: {str(e)}"


