#!/usr/bin/env python3
"""Start Streamlit with live logs for local development."""

import os
import subprocess
import sys
import time
from pathlib import Path


def start_streamlit() -> None:
    """Start the Streamlit frontend with live log streaming."""

    frontend_dir = Path(__file__).parent
    venv_python = "/Users/patrick.zackert/projects/masterprojekt/venv/bin/python"

    if not Path(venv_python).exists():
        raise FileNotFoundError(f"Python-Interpreter nicht gefunden: {venv_python}")

    os.chdir(frontend_dir)

    print("🚀 Starte Streamlit...")
    print("📍 Verzeichnis:", frontend_dir)
    print("=" * 60)

    cmd = [
        venv_python,
        "-m",
        "streamlit",
        "run",
        "Home.py",
        "--server.port",
        "8501",
        "--browser.gatherUsageStats",
        "false",
    ]

    process = None
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        print(f"✅ Streamlit gestartet (PID: {process.pid})")
        print("🌐 Browser öffnet automatisch...")
        print("📊 Live-Logs:")
        print("=" * 60)

        assert process.stdout is not None  # for typing clarity
        for line in process.stdout:
            print(line, end="", flush=True)

    except KeyboardInterrupt:
        print("\n🛑 Streamlit wird beendet...")
        if process:
            process.terminate()
            process.wait()
        print("✅ Streamlit beendet")
    except Exception as exc:  # pylint: disable=broad-except
        print(f"❌ Fehler beim Start: {exc}")
        if process:
            process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    start_streamlit()
