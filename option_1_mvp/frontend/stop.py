#!/usr/bin/env python3
"""Stop running Streamlit processes for the frontend."""

import subprocess
import sys


def stop_streamlit() -> None:
    """Stop all running Streamlit processes started with `streamlit run`."""

    try:
        result = subprocess.run(
            ["pgrep", "-f", "streamlit run"],
            capture_output=True,
            text=True,
            check=False,
        )

        if not result.stdout.strip():
            print("ℹ️  Kein Streamlit-Prozess läuft")
            return

        pids = result.stdout.strip().splitlines()
        print(f"🛑 Stoppe {len(pids)} Streamlit-Prozess(e)...")

        for pid in pids:
            subprocess.run(["kill", pid], check=False)
            print(f"✅ Prozess {pid} beendet")

    except Exception as exc:  # pylint: disable=broad-except
        print(f"❌ Fehler: {exc}")
        sys.exit(1)

if __name__ == "__main__":
    stop_streamlit()
