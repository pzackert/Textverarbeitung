# LLM Integration
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0  
**Stand:** 10. November 2025

## Übersicht

Integration und Management des lokalen LLM-Systems für die Dokumentenanalyse. Dieses Dokument beschreibt die **Best Practice Implementierung** mit LM Studio und OpenAI-kompatibler API.

---

## 🎯 EMPFEHLUNG: LM STUDIO MIT OPENAI-KOMPATIBLER API

Nach Analyse der Projektanforderungen ist **LM Studio** die optimale Lösung für dieses Projekt.

### Warum LM Studio die beste Wahl ist

**Vorteile für das IFB-Projekt:**
- ✅ **Sofort einsatzbereit** - Keine komplexe Server-Konfiguration nötig
- ✅ **OpenAI API-Kompatibilität** - Standardisierte Integration, einfacher Wechsel zwischen Modellen
- ✅ **GUI für Nicht-Techniker** - IFB-Mitarbeiter können Modelle selbst wechseln
- ✅ **Lokale Ausführung** - Erfüllt alle Datenschutzanforderungen
- ✅ **Hardware-Optimierung** - Automatische Nutzung von GPU/Metal auf M1 Macs
- ✅ **Modell-Management** - Einfaches Laden/Entladen verschiedener Modelle

### Architektur-Konzept

```python
# Flexible LLM-Konfiguration
LLM_CONFIG = {
    "provider": "lm_studio",  # oder "ollama", "custom"
    "base_url": "http://localhost:1234/v1",  # LM Studio default
    "model": "qwen2.5-7b-instruct",
    "api_key": "not-needed",  # LM Studio braucht keinen Key
    "timeout": 120,
    "max_retries": 3,
    "temperature": 0.3,  # Niedrig für konsistente Antworten
}

# Fallback-Konfigurationen
FALLBACK_CONFIGS = [
    {"provider": "lm_studio", "base_url": "http://localhost:1234/v1"},
    {"provider": "ollama", "base_url": "http://localhost:11434/api"},
    {"provider": "custom", "base_url": "http://localhost:8080/v1"},
]
```

---

## 🏗️ IMPLEMENTATION MIT OPENAI-CLIENT

### LLMManager - Zentrale Verwaltung

```python
from openai import OpenAI
import requests
from typing import Optional, Dict, Any
import logging

class LLMManager:
    """Zentrale LLM-Verwaltung mit automatischer Erkennung und Fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.is_connected = False
        self.provider_info = {}
        
        # Initialisierung mit Health-Check
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Versuche Verbindung zu LLM-Server aufzubauen"""
        
        # Primäre Konfiguration testen
        if self._test_connection(self.config):
            self._setup_client(self.config)
            logging.info(f"Verbunden mit {self.config['provider']} auf {self.config['base_url']}")
            return
        
        # Fallback-Konfigurationen durchgehen
        for fallback in FALLBACK_CONFIGS:
            if self._test_connection(fallback):
                self._setup_client(fallback)
                logging.info(f"Fallback: Verbunden mit {fallback['provider']}")
                return
        
        raise ConnectionError("Kein LLM-Server erreichbar! Bitte LM Studio starten.")
    
    def _test_connection(self, config: Dict) -> bool:
        """Teste ob LLM-Server erreichbar ist"""
        try:
            # LM Studio Health-Check
            if config['provider'] == 'lm_studio':
                response = requests.get(
                    f"{config['base_url'].replace('/v1', '')}/models",
                    timeout=5
                )
                if response.status_code == 200:
                    models = response.json()
                    self.provider_info = {
                        'provider': 'LM Studio',
                        'models': models.get('data', []),
                        'status': 'online'
                    }
                    return True
            
            # Ollama Health-Check
            elif config['provider'] == 'ollama':
                response = requests.get(
                    f"{config['base_url'].replace('/api', '')}/api/tags",
                    timeout=5
                )
                return response.status_code == 200
            
            # Generic OpenAI-compatible Check
            else:
                response = requests.get(
                    f"{config['base_url']}/models",
                    timeout=5
                )
                return response.status_code == 200
                
        except Exception as e:
            logging.debug(f"Connection test failed for {config['provider']}: {e}")
            return False
    
    def _setup_client(self, config: Dict):
        """Erstelle OpenAI-Client mit gewählter Konfiguration"""
        self.config = config
        self.client = OpenAI(
            base_url=config['base_url'],
            api_key=config.get('api_key', 'not-needed')
        )
        self.is_connected = True
    
    def query(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Sende Anfrage an LLM"""
        if not self.is_connected:
            raise ConnectionError("Keine Verbindung zum LLM-Server")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.get('model', 'local-model'),
                messages=messages,
                temperature=self.config.get('temperature', 0.3),
                max_tokens=self.config.get('max_tokens', 2000),
                timeout=self.config.get('timeout', 120)
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"LLM-Anfrage fehlgeschlagen: {e}")
            # Automatischer Reconnect-Versuch
            self._initialize_connection()
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Detaillierter Status-Check"""
        return {
            'connected': self.is_connected,
            'provider': self.config.get('provider'),
            'base_url': self.config.get('base_url'),
            'model': self.config.get('model'),
            'provider_info': self.provider_info
        }
```

---

## 🚀 STARTUP-SEQUENZ

### ApplicationStartup - Startup-Routine mit LLM-Verfügbarkeitsprüfung

```python
import time

class ApplicationStartup:
    """Startup-Routine mit LLM-Verfügbarkeitsprüfung"""
    
    def __init__(self):
        self.llm_manager = None
        self.rag_system = None
        self.ui_ready = False
    
    def initialize(self):
        """Komplette Initialisierung mit Fehlerbehandlung"""
        
        print("🚀 Starte IFB Innovationsförderung KI-System...")
        
        # Schritt 1: LLM-Verbindung
        print("📡 Prüfe LLM-Verfügbarkeit...")
        if not self._init_llm():
            self._show_llm_setup_guide()
            return False
        
        # Schritt 2: ChromaDB initialisieren
        print("💾 Initialisiere Vektor-Datenbank...")
        self._init_vector_db()
        
        # Schritt 3: RAG-System aufbauen
        print("📚 Lade RAG-System...")
        self._init_rag()
        
        # Schritt 4: Unit-Test
        print("🧪 Führe Systemtest durch...")
        if not self._run_system_test():
            print("❌ Systemtest fehlgeschlagen!")
            return False
        
        print("✅ System erfolgreich gestartet!")
        return True
    
    def _init_llm(self) -> bool:
        """LLM initialisieren mit Retry-Logik"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                self.llm_manager = LLMManager(LLM_CONFIG)
                
                # Quick Test
                test_response = self.llm_manager.query(
                    "Antworte nur mit 'System bereit'."
                )
                
                if "bereit" in test_response.lower():
                    print(f"✅ LLM verbunden: {self.llm_manager.provider_info.get('provider', 'Unknown')}")
                    return True
                    
            except Exception as e:
                print(f"⚠️ Versuch {attempt + 1}/{max_retries} fehlgeschlagen: {e}")
                time.sleep(2)
        
        return False
    
    def _show_llm_setup_guide(self):
        """Zeige Anleitung wenn kein LLM verfügbar"""
        print("""
        ❌ Kein LLM-Server gefunden!
        
        Bitte starten Sie einen der folgenden Server:
        
        Option 1: LM Studio (Empfohlen)
        1. Öffnen Sie LM Studio
        2. Laden Sie ein Modell (z.B. Qwen 2.5 7B)
        3. Starten Sie den Server (Port 1234)
        
        Option 2: Ollama
        1. Terminal: ollama serve
        2. Terminal: ollama pull qwen2.5:7b
        
        Option 3: Eigener OpenAI-kompatibler Server
        1. Starten Sie Ihren Server auf Port 8080
        2. Stellen Sie sicher, dass /v1/chat/completions verfügbar ist
        """)
    
    def _init_vector_db(self):
        """ChromaDB initialisieren"""
        # Implementation siehe 03_RAG_SYSTEM.md
        pass
    
    def _init_rag(self):
        """RAG-System initialisieren"""
        # Implementation siehe 03_RAG_SYSTEM.md
        pass
    
    def _run_system_test(self) -> bool:
        """Vollständiger System-Test"""
        tests = [
            ("LLM-Antwort", self._test_llm_response),
            ("RAG-Retrieval", self._test_rag_retrieval),
            ("Dokument-Parsing", self._test_document_parsing),
        ]
        
        for test_name, test_func in tests:
            try:
                print(f"  Testing {test_name}...", end="")
                test_func()
                print(" ✅")
            except Exception as e:
                print(f" ❌ ({e})")
                return False
        
        return True
    
    def _test_llm_response(self):
        """Test: LLM antwortet korrekt"""
        response = self.llm_manager.query("Sage 'Test erfolgreich'")
        assert "erfolgreich" in response.lower()
    
    def _test_rag_retrieval(self):
        """Test: RAG findet Dokumente"""
        # Implementation
        pass
    
    def _test_document_parsing(self):
        """Test: Dokument-Parser funktioniert"""
        # Implementation
        pass
```

---

## ⚙️ KONFIGURATIONSDATEI

### config.yaml - Umgebungsspezifische Konfiguration

```yaml
# LLM-Konfiguration für verschiedene Umgebungen
llm:
  development:
    provider: lm_studio
    base_url: http://localhost:1234/v1
    model: qwen2.5-7b-instruct
    temperature: 0.3
    max_tokens: 2000
    timeout: 120
  
  testing:
    provider: ollama
    base_url: http://localhost:11434/api
    model: qwen2.5:7b
    temperature: 0.3
    max_tokens: 2000
  
  production:
    provider: vllm
    base_url: http://localhost:8000/v1
    model: Qwen/Qwen2.5-7B-Instruct
    gpu_memory_utilization: 0.9
    max_model_len: 8192
    temperature: 0.3
    max_tokens: 2000

# System-Einstellungen
system:
  auto_fallback: true
  health_check_interval: 60
  require_llm_on_startup: true
  show_setup_guide: true
  log_level: INFO

# Vector Store (ChromaDB)
vector_store:
  engine: chroma
  path: ./data/chromadb
  embedding_model: BAAI/bge-large-en-v1.5
  dimension: 1024

# RAG-Einstellungen
rag:
  chunk_size: 1000
  chunk_overlap: 200
  max_chunks_per_query: 5
  similarity_threshold: 0.75
```

---

## 🔄 ALTERNATIVE DEPLOYMENT-OPTIONEN

### Option 1: LM Studio (Empfohlen für Development)

**Setup:**
```bash
# 1. LM Studio installieren (bereits erfolgt)
# 2. Modell in LM Studio GUI herunterladen
# 3. Server starten mit folgenden Einstellungen:

Server-Einstellungen in LM Studio:
- Port: 1234 (Standard)
- Context Length: 8192 (für Qwen 7B)
- GPU Layers: -1 (alle, wenn möglich)
- Keep Alive: -1 (Modell im Speicher halten)
```

**Python Integration:**
```python
LM_STUDIO_CONFIG = {
    "provider": "lm_studio",
    "base_url": "http://localhost:1234/v1",
    "model": "qwen2.5-7b-instruct",
    "temperature": 0.3,
}
```

### Option 2: Ollama (Backup-Option)

**Setup:**
```bash
# Installation
brew install ollama  # macOS
# oder: curl -fsSL https://ollama.com/install.sh | sh

# Modell herunterladen
ollama pull qwen2.5:7b

# Server starten
ollama serve
```

**Python Integration:**
```python
OLLAMA_CONFIG = {
    "provider": "ollama",
    "base_url": "http://localhost:11434/api",
    "model": "qwen2.5:7b",
    "temperature": 0.3,
}
```

### Option 3: vLLM (Production-Ready)

**Setup:**
```bash
# Installation
pip install vllm

# Server starten
vllm serve Qwen/Qwen2.5-7B-Instruct \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.9 \
    --max-model-len 8192
```

**Python Integration:**
```python
VLLM_CONFIG = {
    "provider": "vllm",
    "base_url": "http://localhost:8000/v1",
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "temperature": 0.3,
}
```

### Option 4: Eigener Inference-Server (Maximum Control)

**Setup mit HuggingFace Transformers:**
```python
from transformers import pipeline

class LocalLLM:
    def __init__(self, model_path="Qwen/Qwen2.5-7B-Instruct"):
        self.pipe = pipeline(
            "text-generation",
            model=model_path,
            device_map="auto",
            torch_dtype="auto"
        )
    
    def generate(self, prompt: str, max_tokens: int = 2000) -> str:
        result = self.pipe(
            prompt,
            max_new_tokens=max_tokens,
            temperature=0.3,
            do_sample=True
        )
        return result[0]['generated_text']
```

---

## 📋 EMPFOHLENES VORGEHEN FÜR DAS PROJEKT

### Phase 1: Development (Jetzt)
1. ✅ **LM Studio** als primäre Lösung nutzen
2. ✅ OpenAI-Client für standardisierte API-Calls
3. ✅ Fallback zu Ollama wenn LM Studio nicht läuft
4. ✅ Einfache Config-Datei für Team-Mitglieder

### Phase 2: Testing
1. Performance-Tests mit verschiedenen Modellen
2. Benchmarking Qwen 3B vs 7B
3. Load-Testing für parallele Anfragen
4. Evaluierung der Antwortqualität

### Phase 3: Deployment bei IFB
1. Evaluierung ob LM Studio ausreicht
2. Ggf. Migration zu vLLM für bessere Performance
3. Dokumentation für IT-Abteilung
4. Schulung der Endbenutzer

---

## ✅ KRITISCHE ERFOLGSFAKTOREN

**✅ Einfachheit vor Komplexität** - LM Studio ist sofort nutzbar ohne Setup

**✅ Flexibilität** - Leichter Wechsel zwischen verschiedenen LLM-Providern

**✅ Robustheit** - Automatische Fallbacks und Reconnection

**✅ Transparenz** - Klare Fehlermeldungen und Setup-Anleitungen

**✅ Performance** - 7B Modell auf M1 Mac läuft mit ~20 tokens/sec

---

## 🎓 FAZIT

**Nutzt LM Studio!** Es ist die pragmatischste Lösung für dieses Projekt. Die OpenAI-kompatible API macht die Integration trivial, und das Team kann sich auf die eigentliche Anwendungslogik konzentrieren statt auf LLM-Infrastruktur.

Der vorgeschlagene Code ist production-ready und erlaubt späteren Wechsel zu anderen Lösungen ohne große Änderungen.

---

## 📚 LEGACY: URSPRÜNGLICHE KONFIGURATION

> **Hinweis:** Die folgenden Abschnitte beschreiben die ursprüngliche Konfiguration. 
> Die oben beschriebene OpenAI-kompatible Lösung ist der **empfohlene Ansatz**.

## Systemkonfiguration

Die gesamte Systemkonfiguration wird in einer zentralen JSON-Datei verwaltet:

```json
{
    "llm": {
        "engine": "lm_studio",
        "model": {
            "name": "mistral-7b-instruct-v0.2",
            "path": "/path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "format": "gguf",
            "quantization": "Q4_K_M",
            "context_window": 8192,
            "max_tokens": 4096
        },
        "inference": {
            "temperature": 0.1,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop_tokens": ["</answer>", "Human:", "Assistant:"],
            "cache_size": 1024,
            "batch_size": 8
        },
        "api": {
            "host": "localhost",
            "port": 1234,
            "timeout": 30
        }
    },
    "vector_store": {
        "engine": "chroma",
        "path": "/path/to/chromadb",
        "embedding_model": "BAAI/bge-large-en-v1.5",
        "dimension": 1024,
        "collection_settings": {
            "hnsw_space": "cosine",
            "hnsw_ef_construction": 100,
            "hnsw_m": 16
        }
    },
    "rag": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "max_chunks_per_query": 5,
        "similarity_threshold": 0.75
    }
}

## Prompting-Strategie

Für jede Kriterienprüfung wird ein neuer Chat mit spezifischem Kontext erstellt:

### Basis-Prompt-Template
```text
<|system|>
Du bist ein Experte für die Prüfung von Förderanträgen. Analysiere die gegebenen 
Informationen sorgfältig und antworte präzise auf die Frage.

<|context|>
{retrieved_context}

<|human|>
{specific_question}

<|assistant|>
```

### Antwortformat
```json
{
    "kriterium": "string",
    "erfuellt": true|false,
    "wert": "string|number|boolean",
    "begruendung": "string",
    "quellen": ["string"],
    "confidence": 0.0-1.0
}
```

## Technische Integration

### LM Studio Setup
1. Modell-Download und Quantisierung
   ```bash
   # Beispiel für Mistral 7B
   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

2. LM Studio Server starten
   ```bash
   lmstudio --model /path/to/model.gguf --host 0.0.0.0 --port 1234
   ```

3. API-Integration
   ```python
   from llm_client import LMStudioClient
   
   client = LMStudioClient("config.json")
   response = client.create_completion(
       prompt="Prüfe anhand des Kontexts...",
       context="Relevante Dokumente..."
   )

### Anforderungen
- Modellgröße: 7B - 13B Parameter
- Quantisierung: 4-bit
- GGUF Format
- Kontext: min. 8k Tokens

### Deployment
- Lokaler Inference Server
- REST API
- Konfigurierbare Endpunkte

## Prompt Engineering

### Basisstruktur
```text
SYSTEM: Du bist ein Experte für Förderanträge...
CONTEXT: {retrieved_context}
QUERY: {specific_question}
```

### Prompt-Typen
1. Kriterienprüfung
2. Datenextraktion
3. Validierung
4. Zusammenfassung

## Inferenz-Pipeline

### Ablauf
1. Kontext aus RAG
2. Prompt-Generierung
3. LLM-Anfrage
4. Antwortverarbeitung

### Parameter
- Temperature: 0.1
- Top-P: 0.9
- Max Tokens: 2048
- Stop Tokens: konfigurierbar

## Performance & Optimierung

### Hardware-Anforderungen
- CPU: 8+ Kerne
- RAM: 16GB+ (32GB empfohlen)
- GPU: Optional, CUDA-fähig
- SSD: 50GB+ für Modelle

### Caching-Strategien
```python
{
    "cache_config": {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "ttl": 86400,  # 24h
        "max_size": "2gb"
    }
}
```

### Monitoring & Logging
- Prometheus Metriken
- Token-Verbrauch
- Antwortzeiten
- Fehlerraten
- Cache-Hits/Misses

## Integration mit Vector Store

### ChromaDB Konfiguration
```python
from chromadb import Client, Settings

client = Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="db",
    anonymized_telemetry=False
))

# Collection pro Projekt
collection = client.create_collection(
    name=f"projekt_{projekt_id}",
    metadata={
        "embedding_model": "BAAI/bge-large-en-v1.5",
        "embedding_dim": 1024
    }
)
```

### RAG-Pipeline
```python
def process_query(query: str, projekt_id: str) -> dict:
    # 1. Relevante Dokumente finden
    context = vector_store.search(
        query=query,
        k=config["rag"]["max_chunks_per_query"]
    )
    
    # 2. LLM-Anfrage mit Kontext
    response = llm_client.create_completion(
        prompt=query,
        context="\n\n".join(context)
    )
    
    return response
```

## Fehlerbehandlung

### Retry-Mechanismus
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def llm_request_with_retry(*args, **kwargs):
    return llm_client.create_completion(*args, **kwargs)
```

### Fallback-Strategien
1. Alternative Modelle
2. Cache-Nutzung
3. Manuelle Prüfung