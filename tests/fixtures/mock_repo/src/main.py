"""Main application entry point for the mock project.

This module provides the core application logic including
configuration loading and the main run loop.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TypedDict

logger = logging.getLogger(__name__)


class AppConfig(TypedDict):
    """Application configuration state."""

    app_name: str
    debug: bool
    log_level: str
    data_dir: str


class ApplicationRunner:
    """Main application runner with configuration support."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._running = False

    def start(self) -> dict:
        """Start the application and return status."""
        logger.info("Starting %s", self.config["app_name"])
        self._running = True
        return {"status": "running", "app_name": self.config["app_name"]}

    def stop(self) -> dict:
        """Stop the application and return status."""
        logger.info("Stopping %s", self.config["app_name"])
        self._running = False
        return {"status": "stopped"}


def load_config(config_path: Path | None = None) -> AppConfig:
    """Load application configuration from file or defaults.

    Args:
        config_path: Optional path to configuration file.

    Returns:
        AppConfig with loaded or default values.
    """
    if config_path and config_path.exists():
        logger.info("Loading config from %s", config_path)

    return AppConfig(
        app_name="mock-project",
        debug=False,
        log_level="INFO",
        data_dir="data",
    )


def process_data(input_data: list[str]) -> dict[str, int]:
    """Process input data and return summary statistics.

    Args:
        input_data: List of string items to process.

    Returns:
        Dictionary with processing statistics.
    """
    result = {
        "total_items": len(input_data),
        "unique_items": len(set(input_data)),
        "empty_items": sum(1 for item in input_data if not item.strip()),
    }
    logger.debug("Processed %d items", result["total_items"])
    return result


def main() -> None:
    """Main entry point for the application."""
    config = load_config()
    runner = ApplicationRunner(config)
    status = runner.start()
    logger.info("Application status: %s", status["status"])


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()