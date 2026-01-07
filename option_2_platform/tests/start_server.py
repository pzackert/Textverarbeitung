
import subprocess
import time
import sys
import requests

def start_server():
    print("Starting uvicorn...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd="/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for port
    for i in range(20):
        try:
            print(f"Server responded: {r.status_code}")
            # Keep server running
            print("Server is UP. Blocking to keep it alive...")
            proc.wait()
            return proc
        except:
            time.sleep(1)
            print("Waiting for server...")
            
    print("Server failed to start.")
    stdout, stderr = proc.communicate()
    print("STDOUT:", stdout.decode())
    print("STDERR:", stderr.decode())
    return None

if __name__ == "__main__":
    start_server()
