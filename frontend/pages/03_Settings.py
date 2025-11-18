"""Streamlit settings page with LM Studio CLI integration."""
from __future__ import annotations

import json
import logging
import select
import subprocess
from typing import Sequence

import streamlit as st
from streamlit.components.v1 import html

LOGGER = logging.getLogger("frontend.app")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

LM_STUDIO_CMD = "lms"
LOG_WINDOW = 200
STATUS_REFRESH_MS = 5000


def _run_cli(args: Sequence[str], timeout: int = 15) -> tuple[bool, str]:
    """Execute an LM Studio CLI command and return success flag plus output."""
    command = [LM_STUDIO_CMD, *args]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except FileNotFoundError:
        msg = "LM Studio CLI (lms) wurde nicht gefunden."
        LOGGER.error("lms_cli_missing | command=%s", command)
        st.session_state["lms_missing"] = True
        return False, msg
    except subprocess.TimeoutExpired:
        msg = "Timeout beim Ausführen des LM Studio Befehls."
        LOGGER.error("lms_cli_timeout | command=%s", command)
        return False, msg

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    if result.returncode != 0:
        message = stderr or stdout or "Unbekannter Fehler."
        LOGGER.error(
            "lms_cli_error | command=%s | code=%s | message=%s",
            command,
            result.returncode,
            message,
        )
        return False, message

    return True, stdout


def _fetch_status() -> tuple[bool, str]:
    success, output = _run_cli(["status"], timeout=5)
    if not success:
        return False, output
    running = "not" not in output.lower() or "running" in output.lower()
    return running, output


def _fetch_models() -> list[str]:
    success, output = _run_cli(["ls", "--json"], timeout=10)
    if not success:
        st.session_state["model_error"] = output
        return []
    try:
        payload = json.loads(output or "[]")
    except json.JSONDecodeError:
        LOGGER.warning("model_list_parse_failed | payload=%s", output)
        return []

    models: list[str] = []
    if isinstance(payload, list):
        for entry in payload:
            if isinstance(entry, dict):
                model_name = (
                    entry.get("name")
                    or entry.get("model")
                    or entry.get("id")
                    or entry.get("path")
                )
                if model_name:
                    models.append(str(model_name))
            elif isinstance(entry, str):
                models.append(entry)
    elif isinstance(payload, dict):
        models = [str(key) for key in payload.keys()]

    return sorted(dict.fromkeys(models))


def _load_model(model: str) -> tuple[bool, str]:
    LOGGER.info("model_load_requested | model=%s", model)
    return _run_cli(["load", model, "--gpu", "max", "-y"], timeout=120)


def _unload_model(model: str) -> tuple[bool, str]:
    LOGGER.info("model_unload_requested | model=%s", model)
    return _run_cli(["unload", model], timeout=30)


def _ensure_log_stream() -> None:
    if st.session_state.get("lms_missing"):
        return
    process = st.session_state.get("log_process")
    if process and process.poll() is None:
        return
    try:
        process = subprocess.Popen(
            [LM_STUDIO_CMD, "log", "stream"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        st.session_state["log_error"] = "LM Studio CLI (lms) wurde nicht gefunden."
        LOGGER.error("log_stream_cli_missing")
        st.session_state["lms_missing"] = True
        return

    st.session_state["log_process"] = process
    LOGGER.info("log_stream_started | pid=%s", process.pid)


def _read_log_stream() -> list[str]:
    logs = st.session_state.setdefault("log_lines", [])
    process = st.session_state.get("log_process")
    if not process or not process.stdout:
        return logs

    try:
        while True:
            ready, _, _ = select.select([process.stdout], [], [], 0)
            if not ready:
                break
            line = process.stdout.readline()
            if not line:
                break
            logs.append(line.rstrip())
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.warning("log_stream_read_error | %s", exc)

    st.session_state["log_lines"] = logs[-LOG_WINDOW:]
    return st.session_state["log_lines"]


def _cleanup_finished_log_stream() -> None:
    process = st.session_state.get("log_process")
    if process and process.poll() is not None:
        LOGGER.info("log_stream_exited | code=%s", process.returncode)
        st.session_state.pop("log_process")


def _inject_auto_refresh(interval_ms: int) -> None:
    """Force the page to rerun after the given interval using built-in HTML support."""
    html(
        f"""
        <script>
            const refreshDelay = {interval_ms};
            setTimeout(() => window.parent.location.reload(), refreshDelay);
        </script>
        """,
        height=0,
        width=0,
    )


LOGGER.info("page_view | {'page': 'settings'}")

st.set_page_config(page_title="LM Studio Settings", layout="wide")
st.title("⚙️ Settings")
st.caption("Verwalte LM Studio Instanzen und beobachte Live-Logs.")

_inject_auto_refresh(STATUS_REFRESH_MS)

cli_missing = st.session_state.get("lms_missing", False)

status_running = False
status_text = "LM Studio Status konnte nicht abgerufen werden."
if not cli_missing:
    status_running, status_text = _fetch_status()

with st.container():
    st.subheader("LM STUDIO STATUS")
    indicator = "🟢" if status_running else "🔴"
    if status_running:
        st.success(f"{indicator} LM Studio läuft\n\n{status_text}")
    else:
        st.error(f"{indicator} LM Studio läuft nicht\n\n{status_text}")
    if cli_missing:
        st.warning("Bitte installiere die LM Studio CLI (lms), damit diese Seite funktioniert.")

st.divider()

st.subheader("MODELL-STEUERUNG")
models: list[str] = []
if not cli_missing:
    models = _fetch_models()

current_model = st.session_state.get("selected_model")
if models and (current_model not in models):
    current_model = models[0]

col_select, col_start, col_stop = st.columns([3, 1, 1])

with col_select:
    if models:
        selected_model = st.selectbox(
            "Verfügbare Modelle",
            options=models,
            index=models.index(current_model) if current_model in models else 0,
            key="selected_model",
        )
    else:
        st.info("Keine Modelle gefunden oder CLI nicht verfügbar.")
        selected_model = None

with col_start:
    start_disabled = selected_model is None or cli_missing
    if st.button("Start", use_container_width=True, disabled=start_disabled):
        if selected_model:
            success, message = _load_model(selected_model)
            LOGGER.info("model_load_result | model=%s | success=%s", selected_model, success)
            if success:
                st.success(f"Modell '{selected_model}' geladen.")
                st.toast(f"{selected_model} geladen")
            else:
                st.error(message)

with col_stop:
    stop_disabled = selected_model is None or cli_missing
    if st.button("Stop", use_container_width=True, disabled=stop_disabled):
        if selected_model:
            success, message = _unload_model(selected_model)
            LOGGER.info("model_unload_result | model=%s | success=%s", selected_model, success)
            if success:
                st.success(f"Modell '{selected_model}' entladen.")
                st.toast(f"{selected_model} entladen")
            else:
                st.error(message)

st.divider()

st.subheader("LOG-STREAM")
if not cli_missing:
    _ensure_log_stream()
    _cleanup_finished_log_stream()
    log_lines = _read_log_stream()
else:
    log_lines = []

log_text = "\n".join(log_lines[-LOG_WINDOW:]) if log_lines else "Keine Logs verfügbar."
st.text_area(
    "LM Studio Logs",
    value=log_text,
    height=280,
    key="lm_studio_logs",
    disabled=True,
)
