"""Configuration loader for benchmark tests."""
import tomllib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    name: str
    backend: str
    enabled: bool

    def __repr__(self) -> str:
        return f"ModelConfig(name={self.name}, backend={self.backend}, enabled={self.enabled})"


@dataclass
class BenchmarkConfig:
    """Complete benchmark configuration."""
    models: List[ModelConfig]
    repetitions: int
    warmup: bool
    temperature: List[float]
    context_length: List[int]

    def get_enabled_models(self) -> List[ModelConfig]:
        """Get list of enabled models."""
        return [m for m in self.models if m.enabled]

    def __repr__(self) -> str:
        return (
            f"BenchmarkConfig("
            f"models={len(self.models)}, "
            f"repetitions={self.repetitions}, "
            f"warmup={self.warmup}, "
            f"temperatures={len(self.temperature)}, "
            f"context_lengths={len(self.context_length)})"
        )


class ConfigLoader:
    """Loads and validates benchmark configuration from TOML file."""

    def __init__(self, config_path: Path):
        """Initialize loader with config file path."""
        self.config_path = Path(config_path)
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

    def load(self) -> BenchmarkConfig:
        """Load and validate configuration."""
        with open(self.config_path, "rb") as f:
            data = tomllib.load(f)

        # Parse run settings
        run_config = data.get("run", {})
        repetitions = run_config.get("repetitions", 3)
        warmup = run_config.get("warmup", True)

        # Parse hyperparameters
        hp_config = data.get("hyperparameters", {})
        temperature = hp_config.get("temperature", [0.7])
        context_length = hp_config.get("context_length", [4096])

        # Parse models
        models_data = data.get("models", [])
        models = [
            ModelConfig(
                name=m.get("name"),
                backend=m.get("backend", "ollama"),
                enabled=m.get("enabled", True),
            )
            for m in models_data
        ]

        # Validate
        if not models:
            raise ValueError("No models configured")

        config = BenchmarkConfig(
            models=models,
            repetitions=repetitions,
            warmup=warmup,
            temperature=temperature,
            context_length=context_length,
        )

        return config

    @staticmethod
    def from_project_root() -> "BenchmarkConfig":
        """Load config from default location relative to project root."""
        config_path = (
            Path(__file__).parent.parent / "config" / "models.toml"
        )
        return ConfigLoader(config_path).load()
