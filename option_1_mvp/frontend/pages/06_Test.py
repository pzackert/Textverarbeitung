from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, Optional

import requests
import streamlit as st
from streamlit.delta_generator import DeltaGenerator

LOGGER = logging.getLogger("frontend.llm_test")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

st.set_page_config(page_title="LLM Test", layout="wide")
LOGGER.info("page_view | {'page': 'llm_test'}")

if "llm_test_state" not in st.session_state:
    st.session_state.llm_test_state = {
        "result": "",
        "error": "",
        "duration": 0.0,
        "running": False,
        "selected_model": None,
        "rag_running": False,
        "rag_file_message": "",
        "rag_file_error": "",
        "rag_results": None,
        "rag_response_time": 0.0,
        "rag_raw_output": "",
        "rag_parse_error": "",
    }

BASE_PATH = Path("/Users/patrick.zackert/projects/masterprojekt")
DOC_TEST_FILES: Dict[str, Path] = {
    "antrag_1": BASE_PATH / "tests/data/projektantrag_gut.txt",
    "antrag_2": BASE_PATH / "tests/data/projektantrag_schlecht.txt",
}
DOC_LABELS: Dict[str, str] = {
    "antrag_1": "Projektantrag 1 (gut)",
    "antrag_2": "Projektantrag 2 (schlecht)",
}

RAG_CRITERIA = (
    ("innovationsgrad", "Innovationsgrad"),
    ("finanzplan", "Finanzplan"),
    ("marktpotential", "Marktpotential"),
    ("projektteam", "Projektteam"),
    ("zeitplan", "Zeitplan"),
)


def _run_lms_cli(args: list[str], timeout: int = 90) -> tuple[bool, str]:
    command = ["lms", *args]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        LOGGER.error("llm_test | lms_cli_not_found | command=%s", command)
        return False, "LM Studio CLI nicht vorhanden"
    except subprocess.TimeoutExpired:
        LOGGER.error("llm_test | lms_cli_timeout | command=%s", command)
        return False, "LM Studio CLI Timeout"
    if result.returncode != 0:
        LOGGER.error("llm_test | lms_cli_error | command=%s | stderr=%s", command, result.stderr)
        return False, (result.stderr or result.stdout).strip()
    return True, (result.stdout or "").strip()


def _list_loaded_model_ids() -> tuple[bool, list[str]]:
    success, output = _run_lms_cli(["ps", "--json"])
    if not success:
        return False, []
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        LOGGER.error("llm_test | ps_parse_error | output=%s", output)
        return False, []
    if isinstance(data, list):
        models = data
    else:
        models = data.get("models") or data.get("llms") or []
    if isinstance(models, dict):
        models = models.get("running", [])
    identifiers: list[str] = []
    if not isinstance(models, list):
        LOGGER.warning("llm_test | ps_unexpected_format")
        return True, []
    for entry in models:
        identifier = entry.get("identifier") or entry.get("id") or entry.get("model")
        if identifier:
            identifiers.append(identifier)
    return True, identifiers


def _get_loaded_model_identifier() -> tuple[bool, Optional[str]]:
    success, identifiers = _list_loaded_model_ids()
    if not success:
        return False, None
    if identifiers:
        return True, identifiers[0]
    return True, None


def _list_available_models() -> tuple[bool, list[dict]]:
    success, output = _run_lms_cli(["ls", "--json"], timeout=120)
    if not success:
        return False, []
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        LOGGER.error("llm_test | ls_parse_error | output=%s", output)
        return False, []
    if isinstance(data, list):
        candidates = data
    else:
        candidates = data.get("llms") or data.get("models") or data
    if isinstance(candidates, dict):
        candidates = candidates.get("items") or candidates.get("entries") or []
    if not isinstance(candidates, list):
        LOGGER.warning("llm_test | ls_unexpected_format")
        return True, []
    llm_entries: list[dict] = []
    for entry in candidates:
        if entry.get("type") == "llm" or entry.get("architecture"):
            llm_entries.append(entry)
    return True, llm_entries


def _load_model(identifier: str) -> tuple[bool, str]:
    LOGGER.info("llm_test | loading_model | identifier=%s", identifier)
    return _run_lms_cli([
        "load",
        identifier,
        "--identifier",
        identifier,
        "--gpu",
        "max",
        "-y",
    ], timeout=180)


def _unload_model(identifier: Optional[str]) -> None:
    if not identifier:
        return
    success, message = _run_lms_cli(["unload", identifier])
    if success:
        LOGGER.info("llm_test | model_unloaded | identifier=%s", identifier)
    else:
        LOGGER.warning("llm_test | unload_failed | identifier=%s | message=%s", identifier, message)


def _ensure_model_available(
    identifier: str,
    progress: Optional[DeltaGenerator] = None,
    progress_value: Optional[int] = None,
    progress_text: str | None = None,
) -> tuple[bool, str]:
    loaded_ok, loaded_models = _list_loaded_model_ids()
    if not loaded_ok:
        return False, "LM Studio nicht erreichbar"
    if identifier in loaded_models:
        return True, "Modell bereits geladen"
    if progress and progress_value is not None:
        progress.progress(progress_value, text=progress_text or "Modell laden...")
    load_ok, load_message = _load_model(identifier)
    if not load_ok:
        return False, load_message or "Fehler beim Laden"
    return True, "Modell geladen"


def _run_llm_prompt(
    model_identifier: str,
    prompt: str,
    *,
    temperature: float = 0.7,
    timeout: int = 30,
) -> tuple[bool, str, float, str]:
    payload = {
        "model": model_identifier,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
    }
    start_time = time.perf_counter()
    try:
        response = requests.post(
            "http://localhost:1234/v1/chat/completions",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        duration = time.perf_counter() - start_time
        data = response.json()
        message = ""
        if matches := data.get("choices"):
            first_choice = matches[0]
            message = (first_choice.get("message", {}).get("content") or "").strip()
        if not message:
            message = data.get("error", "Keine Antwort erhalten.")
        return True, message, duration, ""
    except requests.Timeout:
        LOGGER.error("llm_test | llm_timeout | model=%s", model_identifier)
        return False, "", 0.0, "Timeout"
    except requests.ConnectionError as exc:
        LOGGER.error("llm_test | llm_connection_error | %s", exc)
        return False, "", 0.0, "Connection"
    except requests.HTTPError as exc:
        status_code = getattr(exc.response, "status_code", "unknown")
        LOGGER.error("llm_test | llm_http_error | status=%s", status_code)
        return False, "", 0.0, f"HTTP {status_code}"
    except requests.RequestException as exc:
        LOGGER.error("llm_test | llm_request_exception | %s", exc)
        return False, "", 0.0, "Request"


def _read_rag_documents() -> tuple[bool, dict[str, str]]:
    contents: dict[str, str] = {}
    for key, path in DOC_TEST_FILES.items():
        try:
            contents[key] = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            LOGGER.error("llm_test | file_missing | path=%s", path)
            return False, {}
    return True, contents


def _format_doc_summary(docs: dict[str, str]) -> str:
    lines = ["Beide Testdokumente wurden geladen:"]
    for key, path in DOC_TEST_FILES.items():
        label = DOC_LABELS.get(key, path.name)
        content = docs.get(key, "")
        lines.append(f"- {label} ({len(content)} Zeichen)")
    return "\n".join(lines)


def _normalize_status(value: str) -> str:
    return (value or "").strip().upper()


def _status_icon(status: str) -> str:
    icons = {
        "ERFÜLLT": "✅",
        "TEILWEISE": "⚠️",
        "NICHT ERFÜLLT": "❌",
    }
    return icons.get(_normalize_status(status), "⚪️")


def _format_status_cell(status: str) -> str:
    icon = _status_icon(status)
    normalized = _normalize_status(status)
    return f"{icon} {normalized or '–'}"


def _extract_json_payload(text: str) -> str:
    trimmed = text.strip()
    if trimmed.upper().startswith("JSON:"):
        return trimmed[len("JSON:"):].strip()
    return trimmed


def _parse_rag_json(text: str) -> tuple[Optional[dict], Optional[str]]:
    payload = _extract_json_payload(text)
    if not payload:
        return None, "Keine JSON-Antwort erhalten"
    try:
        return json.loads(payload), None
    except json.JSONDecodeError as exc:
        LOGGER.warning("llm_test | rag_json_parse_error | %s", exc)
        return None, str(exc)


def _save_rag_results_json(results: dict[str, dict[str, str]]) -> None:
    target_path = BASE_PATH / "data" / "rag_test_results.json"
    try:
        target_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        LOGGER.info("llm_test | rag_results_saved | path=%s", target_path)
    except OSError as exc:
        LOGGER.error("llm_test | rag_results_save_failed | %s", exc)


def _build_rag_prompt(docs: dict[str, str]) -> str:
    doc_one = docs.get("antrag_1", "").strip()
    doc_two = docs.get("antrag_2", "").strip()
    return (
        "Du bist ein Experte für die Bewertung von Förderanträgen. Prüfe die folgenden zwei Projektanträge gegen diese Kriterien:\n"
        "KRITERIEN:\n\n"
        "Innovationsgrad: Ist eine klare technische oder geschäftliche Innovation beschrieben?\n"
        "Finanzplan: Ist eine detaillierte, plausible Finanzplanung vorhanden?\n"
        "Marktpotential: Wird das Marktpotential mit konkreten Zahlen belegt?\n"
        "Projektteam: Ist das Team ausreichend qualifiziert (Erfahrung, Expertise)?\n"
        "Zeitplan: Gibt es einen realistischen, strukturierten Zeitplan?\n\n"
        "PROJEKTANTRAG 1:\n"
        f"{doc_one}\n\n"
        "PROJEKTANTRAG 2:\n"
        f"{doc_two}\n\n"
        "Bewerte jeden Antrag für jedes Kriterium mit:\n"
        "ERFÜLLT (wenn klar erfüllt)\n"
        "TEILWEISE (wenn ansatzweise erfüllt)\n"
        "NICHT ERFÜLLT (wenn nicht oder unzureichend erfüllt)\n\n"
        "Antworte im folgenden JSON-Format:\n"
        "{\n"
        "  \"antrag_1\": {\n"
        "    \"innovationsgrad\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"finanzplan\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"marktpotential\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"projektteam\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"zeitplan\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"gesamtbewertung\": \"Kurze Zusammenfassung\"\n"
        "  },\n"
        "  \"antrag_2\": {\n"
        "    \"innovationsgrad\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"finanzplan\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"marktpotential\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"projektteam\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"zeitplan\": \"ERFÜLLT/TEILWEISE/NICHT ERFÜLLT\",\n"
        "    \"gesamtbewertung\": \"Kurze Zusammenfassung\"\n"
        "  }\n"
        "}\n"
        "Gib nur das JSON-Objekt ohne zusätzlichen Text oder Erklärungen zurück."
    )


def _render_rag_file_feedback(container: DeltaGenerator) -> None:
    container.empty()
    state = st.session_state.llm_test_state
    if state.get("rag_file_error"):
        container.error(state["rag_file_error"])
    if state.get("rag_file_message"):
        container.success(state["rag_file_message"])


def _render_rag_results(container: DeltaGenerator) -> None:
    container.empty()
    state = st.session_state.llm_test_state
    results = state.get("rag_results")
    response_text = state.get("rag_raw_output", "")
    response_time = state.get("rag_response_time", 0.0)
    parse_error = state.get("rag_parse_error")
    if not results and not response_text and not parse_error:
        return
    with container.container():
        if parse_error and results is None:
            st.warning("JSON Parse Error – Rohantwort wird zusätzlich dargestellt")
            if response_text:
                st.code(response_text)
        if results:
            columns = st.columns([1, 1])
            for idx, key in enumerate(("antrag_1", "antrag_2")):
                with columns[idx]:
                    heading = "📄 Projektantrag 1" if key == "antrag_1" else "📄 Projektantrag 2"
                    st.subheader(heading)
                    table_rows = [
                        {
                            "Kriterium": label,
                            "Status": _format_status_cell(results.get(key, {}).get(field, "")),
                        }
                        for field, label in RAG_CRITERIA
                    ]
                    st.table(table_rows)
                    summary = results.get(key, {}).get("gesamtbewertung")
                    if summary:
                        st.info(summary)
            st.markdown("**Legende:** \n- ✅ = ERFÜLLT (grün)\n- ⚠️ = TEILWEISE (gelb)\n- ❌ = NICHT ERFÜLLT (rot)")
        st.caption(f"Antwortzeit: {response_time:.2f} Sekunden")

def _reset_result_state() -> None:
    st.session_state.llm_test_state.update({
        "result": "",
        "error": "",
        "duration": 0.0,
    })


def _render_result(result_placeholder: DeltaGenerator) -> None:
    result_placeholder.empty()
    state = st.session_state.llm_test_state
    if state["result"]:
        with result_placeholder.container():
            st.success(state["result"])
            st.caption(f"Antwortzeit: {state['duration']:.2f} Sekunden")
    elif state["error"]:
        with result_placeholder.container():
            st.error(state["error"])


def _execute_test(progress_placeholder: DeltaGenerator, result_placeholder: DeltaGenerator) -> None:
    _reset_result_state()
    progress = progress_placeholder.progress(0, text="Verbinde mit LLM...")
    model_identifier: Optional[str] = None
    target_model = st.session_state.llm_test_state.get("selected_model")
    if not target_model:
        st.session_state.llm_test_state["error"] = "Kein Modell verfügbar"
        LOGGER.error("llm_test | no_selection")
        progress_placeholder.empty()
        _render_result(result_placeholder)
        return
    try:
        ensure_ok, ensure_msg = _ensure_model_available(target_model, progress, 25, "Lade Modell...")
        if not ensure_ok:
            st.session_state.llm_test_state["error"] = "LM Studio nicht erreichbar"
            LOGGER.error("llm_test | ensure_failed | message=%s", ensure_msg)
            return
        model_identifier = target_model
        if not model_identifier:
            st.session_state.llm_test_state["error"] = "Kein Modell verfügbar"
            LOGGER.error("llm_test | no_model_identifier_after_load")
            return
        progress.progress(60, text="Warte auf Antwort...")
        ok, message, duration, error_code = _run_llm_prompt(
            model_identifier,
            "Hello! Please introduce yourself briefly.",
            temperature=0.7,
            timeout=30,
        )
        if not ok:
            st.session_state.llm_test_state["error"] = "LM Studio nicht erreichbar"
            LOGGER.error("llm_test | hello_prompt_failed | code=%s", error_code)
        else:
            st.session_state.llm_test_state["result"] = message
            st.session_state.llm_test_state["duration"] = duration
            LOGGER.info("llm_test | success | duration=%.2f", duration)
            progress.progress(90, text="Antwort empfangen")
    finally:
        progress.progress(100, text="Modell entladen...")
        _unload_model(model_identifier)
        progress_placeholder.empty()
        _render_result(result_placeholder)


def _execute_rag_flow(progress_placeholder: DeltaGenerator, feedback_placeholder: DeltaGenerator) -> None:
    progress = progress_placeholder.progress(0, text="Lade Dokumente...")
    state = st.session_state.llm_test_state
    state.update({
        "rag_results": None,
        "rag_raw_output": "",
        "rag_response_time": 0.0,
        "rag_parse_error": "",
        "rag_file_message": "",
        "rag_file_error": "",
    })
    LOGGER.info("llm_test | rag_flow_start")
    docs_ok, docs_content = _read_rag_documents()
    if not docs_ok:
        state["rag_file_error"] = "Testdateien nicht gefunden"
        feedback_placeholder.error(state["rag_file_error"])
        progress_placeholder.empty()
        return
    summary = _format_doc_summary(docs_content)
    state["rag_file_message"] = summary
    feedback_placeholder.info(summary)
    LOGGER.info("llm_test | rag_docs_loaded")
    progress.progress(30, text="Verbinde mit LLM...")
    target_model = state.get("selected_model")
    if not target_model:
        state["rag_file_error"] = "Kein Modell ausgewählt"
        feedback_placeholder.error(state["rag_file_error"])
        progress_placeholder.empty()
        return
    ensure_ok, ensure_msg = _ensure_model_available(target_model, progress, 45, "Lade Modell...")
    if not ensure_ok:
        state["rag_file_error"] = "LLM nicht erreichbar"
        feedback_placeholder.error(state["rag_file_error"])
        LOGGER.error("llm_test | rag_ensure_failed | message=%s", ensure_msg)
        progress_placeholder.empty()
        return
    prompt = _build_rag_prompt(docs_content)
    progress.progress(60, text="Warte auf Antwort...")
    ok, message, duration, error_code = _run_llm_prompt(
        target_model,
        prompt,
        temperature=0.2,
        timeout=60,
    )
    state["rag_response_time"] = duration
    state["rag_raw_output"] = message
    if not ok:
        state["rag_file_error"] = "LLM nicht erreichbar"
        feedback_placeholder.error(state["rag_file_error"])
        LOGGER.error("llm_test | rag_prompt_failed | code=%s", error_code)
    else:
        parsed, parse_error = _parse_rag_json(message)
        if parsed:
            state["rag_results"] = parsed
            state["rag_parse_error"] = ""
            feedback_placeholder.success("Dokumente wurden geprüft")
            LOGGER.info("llm_test | rag_success | duration=%.2f", duration)
            _save_rag_results_json(parsed)
        else:
            state["rag_results"] = None
            state["rag_parse_error"] = parse_error or "JSON konnte nicht geparst werden"
            feedback_placeholder.error("JSON Parse Error – Rohantwort wird angezeigt")
            LOGGER.error("llm_test | rag_json_parse_failed | %s", parse_error)
    progress.progress(90, text="Modell entladen...")
    _unload_model(target_model)
    progress.progress(100, text="Fertig")
    progress_placeholder.empty()

st.header("🧪 LLM Test & Diagnose")
st.subheader("Teste die Funktionalität des Large Language Models")

models_ok, available_models = _list_available_models()
model_identifiers: list[str] = []
model_labels: dict[str, str] = {}
if models_ok and available_models:
    for entry in available_models:
        identifier = entry.get("identifier") or entry.get("modelKey") or entry.get("path")
        if not identifier:
            continue
        label = entry.get("displayName") or identifier
        model_identifiers.append(identifier)
        model_labels[identifier] = label

if model_identifiers and "llm_model_selector" not in st.session_state:
    st.session_state["llm_model_selector"] = model_identifiers[0]

selected_identifier = None
if model_identifiers:
    selected_identifier = st.selectbox(
        "Modell auswählen",
        options=model_identifiers,
        format_func=lambda ident: model_labels.get(ident, ident),
        key="llm_model_selector",
    )
    st.session_state.llm_test_state["selected_model"] = selected_identifier
else:
    st.error("Keine LLM-Modelle verfügbar. Bitte in LM Studio herunterladen.")
    st.session_state.llm_test_state["selected_model"] = None

status_ok, status_model = _get_loaded_model_identifier()
status_text = f"Aktuell geladen: {status_model}" if status_ok and status_model else "Kein Modell geladen"
if selected_identifier:
    st.caption(f"Auswahl: {model_labels.get(selected_identifier, selected_identifier)}")
st.write(status_text)

st.markdown("### Test 1: Hello World")
st.write("Sendet eine einfache Nachricht an das LLM")

button_cols = st.columns([1, 2, 1])
progress_placeholder = st.empty()
result_placeholder = st.empty()

button_disabled = st.session_state.llm_test_state["running"] or not model_identifiers

with button_cols[1]:
    button_clicked = st.button(
        "Hello World Test starten",
        use_container_width=True,
        disabled=button_disabled,
    )

if button_clicked and not st.session_state.llm_test_state["running"]:
    st.session_state.llm_test_state["running"] = True
    progress_placeholder.empty()
    result_placeholder.empty()
    _execute_test(progress_placeholder, result_placeholder)
    st.session_state.llm_test_state["running"] = False
else:
    _render_result(result_placeholder)

st.divider()
st.markdown("### Test 2: Dokumentenprüfung")
st.write("Prüft zwei Projektanträge gegen Förderkriterien")

rag_button_cols = st.columns([1, 2, 1])
rag_feedback_placeholder = st.empty()
rag_results_placeholder = st.empty()
rag_progress_placeholder = st.empty()
rag_button_disabled = st.session_state.llm_test_state["rag_running"]

with rag_button_cols[1]:
    rag_button_clicked = st.button(
        "Dokumentenprüfung starten",
        use_container_width=True,
        disabled=rag_button_disabled,
        key="rag_test_button",
    )

if rag_button_clicked and not st.session_state.llm_test_state["rag_running"]:
    st.session_state.llm_test_state["rag_running"] = True
    rag_progress_placeholder.empty()
    rag_feedback_placeholder.empty()
    rag_results_placeholder.empty()
    _execute_rag_flow(rag_progress_placeholder, rag_feedback_placeholder)
    st.session_state.llm_test_state["rag_running"] = False

_render_rag_file_feedback(rag_feedback_placeholder)
_render_rag_results(rag_results_placeholder)
