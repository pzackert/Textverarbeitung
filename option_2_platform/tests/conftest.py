import os
from pathlib import Path


# Ensure required directories exist for tests only
Path("data/projects").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

# Mark test mode for components that check this flag
os.environ.setdefault("PYTEST_CURRENT_TEST", "1")

import pytest  # noqa: F401

# Shared fixtures can be added here as needed
