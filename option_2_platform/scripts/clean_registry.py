from pathlib import Path

DATA_DIR = Path("/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input")


def clean_registry():
    """Registry is deprecated; folder scan is now the source of truth."""
    print("registry.json is no longer used; nothing to clean.")
    print(f"Projects are discovered directly from {DATA_DIR}")


if __name__ == "__main__":
    clean_registry()
