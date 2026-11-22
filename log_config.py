import logging
import os
import sys


def setup_logging() -> None:
    """Log to stdout so Render captures it in the Logs tab. Safe to call repeatedly."""
    root = logging.getLogger()
    if getattr(root, "_research_configured", False):
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root.handlers = [handler]
    root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    # keep noisy libraries quiet
    for noisy in ("httpx", "httpcore", "urllib3", "watchdog"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    root._research_configured = True
