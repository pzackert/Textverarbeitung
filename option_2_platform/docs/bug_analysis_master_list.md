# Comprehensive Bug Analysis & Fix Plan (2026-01-06)

This document tracks the deep analysis and resolution of the 7 critical issues reported by the user.

## 1. Global Chat Deletion (UI/Backend)
**Issue:** Clicking delete icon is sluggish/non-functional.
**Analysis Status:** Pending
**Backend Check:** `/api/chats/global/{id}` DELETE endpoint efficiency.
**Frontend Check:** `chat.html` event bubbling/AlpineJS logic.
**Resolution:** TBD

## 2. Global RAG Ingestion Failure (Large PDF)
**Issue:** `the-state-of-enterprise-ai_2025-report.pdf` (10MB) uploaded but not found in RAG.
**Analysis Status:** Pending
**Hypothesis:** Timeouts, Parsing failures (PyPDF/Docling), or silently skipped chunks.
**Actions:**
- Check if file exists in `data/global_knowledge`.
- Check ChromaDB for chunks with this `source` or `doc_name`.
- Simulate ingestion with debug logging.
**Resolution:** TBD

## 3. Settings / Stats Discrepancy
**Issue:** Total chunks (139) too low for large PDF.
**Analysis Status:** Pending
**Hypothesis:** PDF was not chunked at all, or only partially.
**Resolution:** TBD

## 4. Dashboard Status "Waiting"
**Issue:** Modules show "Wartet..." even after system is running.
**Analysis Status:** Pending
**Hypothesis:** Frontend polling logic in `index.html` or `system_state` endpoint returning default values.
**Resolution:** TBD

## 5. Project RAG / Chat Issues
**Issue:**
- Documents "loaded" but Chat says "Failed to retrieve".
- Context leaks between projects.
- UI Formatting (Sources visibility).
**Analysis Status:** Pending
**Actions:** Test Project RAG isolation and Ingestion trigger on Project Load.
**Resolution:** TBD

## 6. Document Viewer Interaction
**Issue:** Cannot click in document viewer / Annotations not working.
**Analysis Status:** Pending
**Resolution:** TBD

## 7. Criteria Check Status Update
**Issue:** "Check All" runs, but Status remains "Open" (Gray) instead of Green/Red/Yellow.
**Analysis Status:** Pending
**Hypothesis:** Evaluation result (`status` field in JSON) is not being written back to the Criterion object in the Database/JSON store.
**Resolution:** TBD

---
## Verification Protocol
1. **Analysis**: Inspect Code & Data.
2. **Fix**: Apply Code Change.
3. **Backend Test**: Verify logic via Script.
4. **Frontend Test**: Verify UI via Browser Agent.
