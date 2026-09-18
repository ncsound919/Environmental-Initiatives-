"""
Configuration management for Overlay Cheetah
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration handler for the autocoder"""

    def __init__(self, data: Dict[str, Any] = None):
        """Initialize configuration

        Args:
            data: Configuration dictionary
        """
        self.data = data or self._default_config()

    @staticmethod
    def load(config_path: str) -> "Config":
        """Load configuration from file

        Args:
            config_path: Path to configuration file

        Returns:
            Config object

        Raises:
            SystemExit: If config file exists but cannot be loaded
        """
        if not os.path.exists(config_path):
            return Config()

        try:
            with open(config_path, "r") as f:
                if config_path.endswith(".yaml") or config_path.endswith(".yml"):
                    data = yaml.safe_load(f)
                else:
                    # Default to YAML
                    data = yaml.safe_load(f)

            return Config(data)
        except yaml.YAMLError as e:
            print(
                f"Error: Failed to parse configuration file '{config_path}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            print(
                f"Error: Failed to load configuration file '{config_path}': {e}",
                file=sys.stderr,
            )
            sys.exit(1)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value
        """
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value

        Args:
            key: Configuration key
            value: Value to set
        """
        self.data[key] = value

    def _default_config(self) -> Dict[str, Any]:
        """Get default configuration

        Returns:
            Default configuration dictionary
        """
        return {
            "version": "3.0.0",
            "model": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 2000,
            "language_defaults": {
                "python": {"style": "pep8", "max_line_length": 88},
                "javascript": {"style": "airbnb", "max_line_length": 100},
            },
            "output": {"format": "auto", "encoding": "utf-8"},
        }
