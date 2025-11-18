"""Start the Streamlit app and optionally attach to its logs.

By default the script runs Streamlit in the background and writes logs to
`streamlit.log` so the terminal stays free. Pass `--attach` to stream logs
directly in the terminal instead.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


def _iter_lines(stream) -> Iterable[str]:
    """Yield lines from a process stream in a robust way.

    Works with text mode streams opened by subprocess.Popen.
    """
    while True:
        line = stream.readline()
        if not line:
            break
        yield line.rstrip("\n")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    app_file = base_dir / "Home.py"
    if not app_file.exists():
        raise FileNotFoundError(f"Streamlit-App nicht gefunden: {app_file}")

    parser = argparse.ArgumentParser(description="Start the Streamlit frontend")
    parser.add_argument("--attach", action="store_true", help="Stream logs in current terminal")
    parser.add_argument("--port", type=int, default=8501, help="Port to run Streamlit on")
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.port",
        str(args.port),
        "--browser.gatherUsageStats",
        "false",
    ]

    url = f"http://localhost:{args.port}"
    print("\nStarting Streamlit...")

    if not args.attach:
        logfile = base_dir / "streamlit.log"
        with logfile.open("a", encoding="utf-8") as fh:
            process = subprocess.Popen(command, cwd=base_dir, stdout=fh, stderr=subprocess.STDOUT)
        print("Streamlit started in background ✨")
        print(f"PID: {process.pid}")
        print(f"URL: {url}")
        print(f"Logs: {logfile}")
        print("To follow logs:")
        print("  tail -f frontend/streamlit.log")
        print("To stop: pkill -f 'streamlit run' or use the PID above.")
        return

    # Attach to process and stream stdout/stderr to the current terminal.
    process = subprocess.Popen(command, cwd=base_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    print("Streamlit started — attached to current terminal ✨")
    print(f"PID: {process.pid}")
    print(f"URL: {url}\n")

    try:
        # Print lines as they arrive — this blocks the terminal until the process exits
        for line in _iter_lines(process.stdout):
            # Prefix time for easier scanning
            print(f"[streamlit] {time.strftime('%Y-%m-%d %H:%M:%S')} {line}")
    except KeyboardInterrupt:
        print("\nReceived interrupt — exiting and leaving Streamlit running in background.")
        return


if __name__ == "__main__":
    main()
