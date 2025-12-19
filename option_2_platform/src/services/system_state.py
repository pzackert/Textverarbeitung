from typing import Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class ComponentState:
    def __init__(self, name: str):
        self.name = name
        self.status = "pending"
        self.progress = 0
        self.message = None
        self.details = {}

    def update(self, status: str, progress: int = None, message: str = None, details: Dict = None):
        self.status = status
        if progress is not None:
            self.progress = progress
        if message is not None:
            self.message = message
        if details is not None:
            self.details = details

class SystemStateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SystemStateManager, cls).__new__(cls)
            cls._instance.status = "initializing"
            cls._instance.components = {
                "ollama": ComponentState("ollama"),
                "lm_studio": ComponentState("lm_studio"),
                "llm_model": ComponentState("llm_model"),
                "embedding_model": ComponentState("embedding_model"),
                "chromadb": ComponentState("chromadb"),
                "rag_pipeline": ComponentState("rag_pipeline")
            }
        return cls._instance

    def get_status_dict(self) -> Dict[str, Any]:
        comps = {k: v.__dict__ for k, v in self.components.items()}
        # Remove name from dict to match schema if needed, but schema accepts extra fields usually.
        # Strict schema matching:
        clean_comps = {}
        error_count = 0
        pending_count = 0
        
        for k, v in self.components.items():
            clean_comps[k] = {
                "status": v.status,
                "progress": v.progress,
                "message": v.message,
                "details": v.details
            }
            if v.status == "error":
                error_count += 1
            if v.status in ["pending", "loading", "connecting"]:
                pending_count += 1
        
        return {
            "status": self.global_status,
            "components": clean_comps
        }

    @property
    def global_status(self) -> str:
        error_count = 0
        pending_count = 0
        
        for v in self.components.values():
            if v.status == "error":
                error_count += 1
            if v.status in ["pending", "loading", "connecting"]:
                pending_count += 1
        
        if error_count > 0:
            return "error"
        elif pending_count == 0:
            return "ready"
        else:
            return "initializing"

    def set_component(self, name: str, status: str, progress: int = None, message: str = None, details: Dict = None):
        if name in self.components:
            self.components[name].update(status, progress, message, details)

system_state = SystemStateManager()

async def run_startup_sequence():
    """
    Simulated startup sequence. Replace with real checks.
    """
    logger.info("Starting system initialization...")
    
    # 1. Ollama Check
    system_state.set_component("ollama", "loading", 10, "Connecting...")
    await asyncio.sleep(1) # Sim check
    # Assume success for now, or use real check
    system_state.set_component("ollama", "ready", 100, "Connected (v0.1.20)")
    
    # 2. LM Studio (Optional) - Set to ready/skipped
    system_state.set_component("lm_studio", "ready", 100, "Not configured (skipped)")
    
    # 3. Embedding Model
    system_state.set_component("embedding_model", "loading", 0, "Loading all-MiniLM-L6-v2...")
    await asyncio.sleep(2)
    system_state.set_component("embedding_model", "ready", 100, "Loaded (cpu)")
    
    # 4. ChromaDB
    system_state.set_component("chromadb", "connecting", 0, "Connecting to db...")
    await asyncio.sleep(1)
    system_state.set_component("chromadb", "ready", 100, "Connected (Found 5 collections)")
    
    # 5. LLM Model
    system_state.set_component("llm_model", "loading", 0, "Pulling ministral-3b...")
    # Sim loading progress
    for i in range(1, 11):
        await asyncio.sleep(0.5)
        system_state.set_component("llm_model", "loading", i*10)
    system_state.set_component("llm_model", "ready", 100, "Model Ready: ministral-3b")
    
    # 6. RAG Pipeline
    system_state.set_component("rag_pipeline", "loading", 0, "Initializing chains...")
    await asyncio.sleep(1)
    system_state.set_component("rag_pipeline", "ready", 100, "Pipeline Active")
    
    logger.info("System initialization complete.")
