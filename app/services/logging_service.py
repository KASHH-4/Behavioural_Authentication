from __future__ import annotations

import logging
import os


def configure_logging(app) -> None:
    log_dir = os.path.join(app.root_path, "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "system.log")

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    if not app.logger.handlers:
        app.logger.addHandler(file_handler)
    else:
        has_file_handler = any(isinstance(h, logging.FileHandler) for h in app.logger.handlers)
        if not has_file_handler:
            app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)


def log_session_activity(app, message: str) -> None:
    app.logger.info("SESSION_ACTIVITY | %s", message)


def log_prediction(app, message: str) -> None:
    app.logger.info("PREDICTION | %s", message)


def log_anomaly(app, message: str) -> None:
    app.logger.warning("ANOMALY | %s", message)
