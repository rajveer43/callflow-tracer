"""OpenTelemetry configuration management for callflow-tracer.

Supports YAML/JSON config files for advanced OTel export settings.
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


class OTelConfig:
    """Manages OpenTelemetry export configuration."""

    DEFAULT_CONFIG = {
        "service_name": "callflow-tracer",
        "environment": "production",
        "sampling_rate": 1.0,
        "include_metrics": False,
        "exporter": {
            "type": "console",  # console, otlp_grpc, otlp_http, jaeger
            "endpoint": "http://localhost:4317",
            "headers": {},
        },
        "resource_attributes": {
            "service.version": "unknown",
        },
        "batch_processor": {
            "max_queue_size": 2048,
            "max_export_batch_size": 512,
            "schedule_delay_millis": 5000,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """Initialize OTel config from file or defaults.

        Parameters
        ----------
        config_path : str, optional
            Path to .callflow_otel.yaml or .callflow_otel.json config file.
            If None, checks for .callflow_otel.yaml in current directory.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path

        if config_path is None:
            config_path = self._find_config_file()

        if config_path and os.path.exists(config_path):
            self.load_from_file(config_path)

    def _find_config_file(self) -> Optional[str]:
        """Find .callflow_otel config file in current or parent directories."""
        for name in [".callflow_otel.yaml", ".callflow_otel.yml", ".callflow_otel.json"]:
            if os.path.exists(name):
                return name
        return None

    def load_from_file(self, path: str) -> None:
        """Load configuration from YAML or JSON file.

        Parameters
        ----------
        path : str
            Path to config file (.yaml, .yml, or .json).
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        try:
            if path.suffix in [".yaml", ".yml"]:
                if not _YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML config files. Install with: pip install pyyaml")
                with open(path, "r") as f:
                    data = yaml.safe_load(f) or {}
            elif path.suffix == ".json":
                with open(path, "r") as f:
                    data = json.load(f)
            else:
                raise ValueError(f"Unsupported config file format: {path.suffix}")

            # Deep merge with defaults
            self._merge_config(data)
        except Exception as e:
            raise RuntimeError(f"Failed to load OTel config from {path}: {e}")

    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Recursively merge new config into existing config."""
        for key, value in new_config.items():
            if isinstance(value, dict) and key in self.config and isinstance(self.config[key], dict):
                self._merge_config_dict(self.config[key], value)
            else:
                self.config[key] = value

    def _merge_config_dict(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Recursively merge source dict into target dict."""
        for key, value in source.items():
            if isinstance(value, dict) and key in target and isinstance(target[key], dict):
                self._merge_config_dict(target[key], value)
            else:
                target[key] = value

    def load_from_env(self) -> None:
        """Load configuration from environment variables.

        Supported env vars:
        - CALLFLOW_OTEL_SERVICE_NAME
        - CALLFLOW_OTEL_ENVIRONMENT
        - CALLFLOW_OTEL_SAMPLING_RATE
        - CALLFLOW_OTEL_EXPORTER_TYPE
        - CALLFLOW_OTEL_EXPORTER_ENDPOINT
        """
        if service_name := os.getenv("CALLFLOW_OTEL_SERVICE_NAME"):
            self.config["service_name"] = service_name

        if environment := os.getenv("CALLFLOW_OTEL_ENVIRONMENT"):
            self.config["environment"] = environment

        if sampling_rate := os.getenv("CALLFLOW_OTEL_SAMPLING_RATE"):
            try:
                self.config["sampling_rate"] = float(sampling_rate)
            except ValueError:
                pass

        if exporter_type := os.getenv("CALLFLOW_OTEL_EXPORTER_TYPE"):
            self.config["exporter"]["type"] = exporter_type

        if endpoint := os.getenv("CALLFLOW_OTEL_EXPORTER_ENDPOINT"):
            self.config["exporter"]["endpoint"] = endpoint

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by dot-notation key.

        Examples:
            config.get("service_name")
            config.get("exporter.type")
            config.get("batch_processor.max_queue_size")
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def to_dict(self) -> Dict[str, Any]:
        """Return config as dictionary."""
        return self.config.copy()

    def to_json(self) -> str:
        """Return config as JSON string."""
        return json.dumps(self.config, indent=2)

    def save_to_file(self, path: str, format: str = "yaml") -> None:
        """Save config to file.

        Parameters
        ----------
        path : str
            Path to save config file.
        format : str
            Format: 'yaml' or 'json'.
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if format == "yaml":
                if not _YAML_AVAILABLE:
                    raise ImportError("PyYAML is required for YAML format. Install with: pip install pyyaml")
                with open(path, "w") as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif format == "json":
                with open(path, "w") as f:
                    json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            raise RuntimeError(f"Failed to save OTel config to {path}: {e}")


def create_example_config(output_path: str = ".callflow_otel.yaml") -> None:
    """Create an example OTel config file.

    Parameters
    ----------
    output_path : str
        Path to save example config file.
    """
    config = OTelConfig()
    config.save_to_file(output_path, format="yaml" if output_path.endswith(".yaml") else "json")
    print(f"Example OTel config created at: {output_path}")
