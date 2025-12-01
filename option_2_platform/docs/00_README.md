# IFB PROFI Documentation

Welcome to the Option 2 Platform documentation. This directory contains comprehensive guides for setup, development, and testing.

## 📚 Documentation Index

### Getting Started
- **[../README.md](../README.md)** - Project overview, Quick Start, setup guides (Mac/Windows)
- **[02_testing_guide.md](02_testing_guide.md)** - Complete testing guide (PyTest, manual tests, troubleshooting)

### Project Specifications
- **[../specs/constitution.md](../specs/constitution.md)** - Project principles and guidelines
- **[../specs/plan.md](../specs/plan.md)** - Implementation plan (phase breakdown)
- **[../specs/tasks.md](../specs/tasks.md)** - Detailed task list

### Phase Specifications
- **[../specs/01_ollama_integration/spec.md](../specs/01_ollama_integration/spec.md)** - LLM integration (Phase 1) ✅
- **[../specs/02_document_parsing/spec.md](../specs/02_document_parsing/spec.md)** - Document parser (Phase 2) ⏳
- **[../specs/03_rag_system/spec.md](../specs/03_rag_system/spec.md)** - RAG system (Phase 3) ⏳
- **[../specs/04_criteria_engine/spec.md](../specs/04_criteria_engine/spec.md)** - Criteria engine (Phase 4) ⏳

### Configuration
- **[../config/ollama.toml](../config/ollama.toml)** - LLM configuration (models, tokens, parameters)

### Reports & Logs
- **[../logs/llm_integration_test_summary.txt](../logs/llm_integration_test_summary.txt)** - LLM test results
- **[../logs/test_results_*.txt](../logs/)** - Test execution logs

---

## 🚀 Quick Start

### For First-Time Users

1. **Read Project Overview:** [../README.md](../README.md)
2. **Follow Setup Guide:** 
   - Mac: See [README - macOS Setup](../README.md#-macos-setup)
   - Windows: See [README - Windows Setup](../README.md#-windows-setup)
3. **Run Tests:** [02_testing_guide.md](02_testing_guide.md)

### For Developers

1. **Understand Architecture:** [../specs/constitution.md](../specs/constitution.md)
2. **Review Implementation Plan:** [../specs/plan.md](../specs/plan.md)
3. **Check Current Tasks:** [../specs/tasks.md](../specs/tasks.md)
4. **Read Current Phase Spec:** [../specs/02_document_parsing/spec.md](../specs/02_document_parsing/spec.md)

---

## 📖 Documentation Structure

```
docs/
├── 00_README.md              # This file (entry point)
└── 02_testing_guide.md       # Testing documentation

specs/
├── constitution.md           # Project principles
├── plan.md                  # Implementation plan
├── tasks.md                 # Task breakdown
├── 01_ollama_integration/   # Phase 1 specs ✅
├── 02_document_parsing/     # Phase 2 specs ⏳
├── 03_rag_system/          # Phase 3 specs ⏳
└── 04_criteria_engine/     # Phase 4 specs ⏳

config/
└── ollama.toml             # LLM configuration

logs/
├── llm_integration_test_summary.txt  # LLM test report
└── test_results_*.txt                # Test execution logs
```

---

## 🎯 Current Project Status

**Phase:** 1 Complete ✅  
**Branch:** `feature/document-parser`  
**Next:** Phase 2 - Document Parser implementation

### Completed
- ✅ Project structure (Spec Kit compliant)
- ✅ Ollama integration (qwen2.5:7b, qwen2.5:0.5b)
- ✅ Configuration system (ollama.toml)
- ✅ Test framework (PyTest)
- ✅ Documentation (README, Testing Guide)

### In Progress
- ⏳ Document parsing (Phase 2)

### Upcoming
- ⏳ RAG system (Phase 3)
- ⏳ Criteria engine (Phase 4)
- ⏳ API layer (Phase 5)
- ⏳ UI integration (Phase 6)

---

## 🔍 Finding Information

### Setup & Installation
- **Mac Setup:** [../README.md#-macos-setup](../README.md#-macos-setup)
- **Windows Setup:** [../README.md#-windows-setup](../README.md#-windows-setup)
- **Troubleshooting:** [../README.md#-troubleshooting](../README.md#-troubleshooting)

### Testing
- **Run Tests:** [02_testing_guide.md#running-tests](02_testing_guide.md#running-tests)
- **Manual Testing:** [02_testing_guide.md#manual-testing](02_testing_guide.md#manual-testing)
- **Test Troubleshooting:** [02_testing_guide.md#troubleshooting](02_testing_guide.md#troubleshooting)

### Configuration
- **Switch Models:** [../config/ollama.toml](../config/ollama.toml)
- **Token Settings:** [../config/ollama.toml](../config/ollama.toml)
- **LM Studio Setup:** [../README.md#using-lm-studio-instead](../README.md#using-lm-studio-instead)

### Development
- **Architecture:** [../specs/constitution.md](../specs/constitution.md)
- **Current Phase:** [../specs/02_document_parsing/spec.md](../specs/02_document_parsing/spec.md)
- **Task List:** [../specs/tasks.md](../specs/tasks.md)

---

## 📝 Contributing to Documentation

When adding new documentation:

1. **Place files correctly:**
   - Setup/user guides → `docs/`
   - Technical specs → `specs/`
   - Configuration docs → `config/` (inline comments)

2. **Update this index** when adding new files

3. **Follow naming convention:**
   - Use descriptive names: `02_testing_guide.md`
   - Number sequentially: `01_`, `02_`, `03_`

4. **Include in documentation:**
   - Table of contents
   - Clear examples
   - Troubleshooting section
   - Last updated date

---

## 🤝 Support

For questions or issues:

1. Check relevant documentation section
2. Search [specs/](../specs/) for technical details
3. Review [logs/](../logs/) for test/error reports
4. Contact project team

---

**Last Updated:** 2025-12-01  
**Project Version:** Phase 1 Complete  
**Python:** 3.12.11 | **PyTest:** 9.0.1 | **UV:** 0.8.17
