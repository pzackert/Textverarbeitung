# System Requirements

**Version:** 2.0 (Architektur-Varianten)  
**Stand:** 10. November 2025

---

## 🎯 ÜBERSICHT

Systemanforderungen variieren je nach gewählter Architektur-Option:
- **Super-Lite:** Lokales Development/Testing
- **Lite:** Production Single-User
- **Full:** Enterprise Multi-User Cloud

---

## 🔧 Option 1: Super-Lite Requirements

### Hardware (Empfohlen für MVP)
- **CPU:** Apple M1/M2 oder Intel i5/AMD Ryzen 5 (4+ Kerne)
- **RAM:** 16GB minimum, 24GB empfohlen
- **Storage:** 20GB SSD (10GB für LM Studio + Modelle, 10GB für Daten)
- **GPU:** Optional (Metal auf Mac, CUDA auf Windows/Linux beschleunigt)

### Software
- **OS:** macOS 11+, Windows 10/11, Linux (Ubuntu 20.04+)
- **Python:** 3.11+ (mit pip)
- **LM Studio:** Latest (Download: https://lmstudio.ai)
- **Git:** Für Version Control

### LM Studio Modelle
- **Qwen 2.5 3B Instruct** (3-4 GB) - Schnell, ausreichend für Tests
- **Qwen 2.5 7B Instruct** (6-7 GB) - Bessere Qualität, empfohlen

### Dependencies (Python)
```txt
openai==1.3.0
chromadb==0.4.18
sentence-transformers==2.2.2
pymupdf==1.23.8
python-docx==1.1.0
openpyxl==3.1.2
streamlit==1.28.0
pydantic==2.5.0
```

**Gesamtgröße:** ~5GB (Python Packages + Embedding Model)

### Network
- **Lokal:** Kein Internet nach Setup benötigt
- **Ports:** 1234 (LM Studio), 8501 (Streamlit)

### Performance-Erwartungen
- **Dokument-Indexierung:** 2-5 Sekunden (10 Seiten PDF)
- **Kriterien-Prüfung:** 5-10 Sekunden pro Kriterium
- **Gesamt-Prüfung:** 30-60 Sekunden (6 Kriterien)
- **Gleichzeitige User:** 1

### Features
- ✅ Single-User-Modus
- ✅ Lokale Dokumenten-Verarbeitung
- ✅ Basic RAG mit ChromaDB
- ✅ Streamlit UI
- ✅ Dokumentgröße: Bis 30MB
- ✅ 100% Datenschutz (alles lokal)

### Einschränkungen
- ❌ Kein Multi-User
- ❌ Keine Cloud-Integration
- ❌ Begrenzte Skalierung
- ❌ Einfaches Error-Handling

---

## 🚀 Option 2: Lite Requirements

### Hardware (Production Single/Small Team)
- **CPU:** Intel i7/AMD Ryzen 7 (6+ Kerne)
- **RAM:** 32GB empfohlen (24GB minimum)
- **Storage:** 50GB SSD
- **GPU:** 8GB VRAM empfohlen (NVIDIA RTX 3060 oder besser)

### Software
- **OS:** Linux (Ubuntu 22.04) empfohlen, macOS/Windows möglich
- **Python:** 3.11+
- **LM Studio:** Latest
- **Docker:** Optional (für Container-Deployment)
- **Git:** Für Version Control

### LM Studio Modelle
- **Qwen 2.5 7B Instruct** (6-7 GB) - Standard
- **Qwen 2.5 14B Instruct** (12-14 GB) - Optional, wenn genug VRAM

### Dependencies (Python)
```txt
# Alle aus Super-Lite +
langchain==0.1.0
langchain-community==0.1.0
```

**Gesamtgröße:** ~7GB

### Network
- **Internet:** Für Updates & Monitoring
- **Lokales Netzwerk:** Für Team-Zugriff
- **Ports:** 1234 (LM Studio), 8501 (Streamlit), 8000 (FastAPI optional)

### Performance-Erwartungen
- **Dokument-Indexierung:** 1-3 Sekunden (10 Seiten PDF)
- **Kriterien-Prüfung:** 3-5 Sekunden pro Kriterium (GPU)
- **Gesamt-Prüfung:** 20-30 Sekunden (6 Kriterien)
- **Gleichzeitige User:** 1-5

### Features
- ✅ Alle aus Super-Lite +
- ✅ Erweiterte RAG-Pipeline (LangChain)
- ✅ Bessere Chunking-Strategie
- ✅ Optimierte Embeddings
- ✅ Dokumentgröße: Bis 100MB
- ✅ Basic API-Endpunkte
- ✅ Monitoring & Logging

### Optional (Lite+)
- Docker-Deployment
- Reverse Proxy (Nginx)
- Redis Cache
- PostgreSQL für Metadaten

---

## ⭐ Option 3: Full Requirements (Enterprise)

### Hardware (Cloud/On-Premise Cluster)
- **CPU:** Multi-Core Server (16+ Kerne)
- **RAM:** 64GB+ (128GB empfohlen)
- **Storage:** 500GB+ SSD (NVMe empfohlen)
- **GPU:** 
  - Development: NVIDIA A10/A100 (24GB+ VRAM)
  - Production: Multi-GPU Setup (A100 80GB empfohlen)

### Software Stack
- **OS:** Linux (Ubuntu 22.04 LTS)
- **Container:** Docker + Kubernetes
- **LLM Runtime:** vLLM oder Text-Generation-Inference (TGI)
- **Vector DB:** Weaviate oder Qdrant (Cluster-Mode)
- **API Gateway:** Kong oder Traefik
- **Message Queue:** RabbitMQ oder Kafka
- **Database:** PostgreSQL 15+ (Replicated)
- **Cache:** Redis Cluster
- **Monitoring:** Prometheus + Grafana
- **Logging:** ELK Stack

### LLM Models
- **Qwen 2.5 14B+** oder größer
- **Custom Fine-Tuned Models** (optional)
- **Multi-Model Support** (verschiedene Modelle für verschiedene Tasks)

### Cloud Provider (Beispiel AWS)
- **EC2:** p4d.24xlarge (8x A100 80GB) oder ähnlich
- **S3:** Für Dokument-Speicherung
- **RDS:** Managed PostgreSQL
- **ElastiCache:** Managed Redis
- **EKS:** Kubernetes Cluster
- **ALB:** Load Balancing

### Network
- **High-Speed Internet:** Gigabit+
- **VPN:** Für sichere Zugriffe
- **CDN:** Optional für Frontend
- **API Gateway:** Rate Limiting, Auth

### Performance-Erwartungen
- **Dokument-Indexierung:** <1 Sekunde (10 Seiten PDF)
- **Kriterien-Prüfung:** 1-2 Sekunden pro Kriterium
- **Gesamt-Prüfung:** 10-15 Sekunden (6 Kriterien)
- **Gleichzeitige User:** Unbegrenzt (Auto-Scaling)
- **Throughput:** 100+ Anfragen/Sekunde

### Features
- ✅ Enterprise Multi-Tenant
- ✅ Unlimited Users
- ✅ Advanced RAG mit Custom Embeddings
- ✅ Multiple LLM Models
- ✅ REST & GraphQL APIs
- ✅ Real-time Collaboration
- ✅ Document Version Control
- ✅ Advanced Analytics
- ✅ Dokumentgröße: 500MB+
- ✅ Automated Backups
- ✅ Disaster Recovery
- ✅ GDPR/SOC2 Compliance
- ✅ CI/CD Pipeline

### DevOps Requirements
- Kubernetes Knowledge
- Infrastructure as Code (Terraform)
- Monitoring & Alerting Setup
- Security Hardening
- Load Testing
- Disaster Recovery Plans

---

## 📊 Vergleichstabelle

| Feature | Super-Lite | Lite | Full |
|---------|------------|------|------|
| **Setup-Zeit** | 1 Tag | 3-5 Tage | 2-3 Monate |
| **Kosten (Hardware)** | €1.500 Laptop | €3.000 Workstation | €50.000+ Server |
| **Kosten (Cloud/Monat)** | €0 | €0-100 | €2.000-10.000+ |
| **Users** | 1 | 1-5 | Unbegrenzt |
| **Dokument-Größe** | 30MB | 100MB | 500MB+ |
| **Verarbeitungszeit** | 30-60s | 20-30s | 10-15s |
| **Skalierbarkeit** | Keine | Begrenzt | Auto-Scaling |
| **Wartung** | Minimal | Mittel | Hoch |
| **Internet nötig** | Nein | Teilweise | Ja |
| **Deployment** | Lokal | Lokal/Docker | K8s/Cloud |

---

## 🎯 EMPFEHLUNG FÜR IFB-PROJEKT

**Starten mit: Option 1 (Super-Lite)**

**Begründung:**
1. ✅ Schnellster Start (MVP in 1 Woche)
2. ✅ Minimale Kosten (vorhandene Hardware)
3. ✅ 100% Datenschutz (lokal)
4. ✅ Ausreichend für Proof-of-Concept
5. ✅ Einfach zu warten

**Upgrade-Pfad:**
- **Nach MVP:** Evaluation mit echten IFB-Dokumenten
- **Bei Bedarf:** Upgrade zu Lite für bessere Performance
- **Nur wenn nötig:** Full für Multi-User-Szenarien

**Kritische Entscheidungspunkte:**
- Mehr als 5 User? → Lite oder Full
- Cloud-Integration erforderlich? → Full
- Budget-Beschränkungen? → Super-Lite
- Proof-of-Concept? → Super-Lite

---

## 🔧 INSTALLATIONS-GUIDE (Super-Lite)

### 1. System vorbereiten
```bash
# Python 3.11+ installieren
python --version  # Sollte 3.11+ sein

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows
```

### 2. LM Studio installieren
1. Download: https://lmstudio.ai
2. Installieren & starten
3. Modell laden: Qwen 2.5 7B Instruct
4. Server starten (Port 1234)

### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 4. Projekt-Setup
```bash
# Ordnerstruktur erstellen
mkdir -p data/{chromadb,projects,regelwerke}

# Config kopieren
cp config/config.example.yaml config/config.yaml
```

### 5. Testen
```bash
# Streamlit starten
streamlit run frontend/app.py

# Browser öffnet automatisch: http://localhost:8501
```

**Erwartete Ausgabe:**
```
[SYSTEM] IFB PROFI System gestartet
[LLM] ✓ Verbunden mit LM Studio (localhost:1234)
[CHROMADB] ✓ Vector Store bereit
[SYSTEM] ✓ System bereit!
```

---

**Ende System Requirements**

**Siehe auch:**
- `TECHNICAL_ARCHITECTURE.md` für Architektur-Details
- `DEVELOPMENT_PRINCIPLES.md` für Best Practices
