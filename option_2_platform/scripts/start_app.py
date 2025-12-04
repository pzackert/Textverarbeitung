import uvicorn
import os
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.init_system import main as init_system

if __name__ == "__main__":
    # Run system checks
    init_system()
    
    print("🚀 Starting IFB PROFI Platform...")
    uvicorn.run(
        "src.main:create_app",
        host="127.0.0.1",
        port=8001,
        factory=True,
        reload=True,
        reload_dirs=["src", "frontend"],
        log_level="info"
    )
