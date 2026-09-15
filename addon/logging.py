# -*- mode: python ; coding: utf-8 -*-
"""Diagnostic logging for the add-on.

Provides a module-level :mod:`logging` logger that writes to a rotating file
inside the add-on's ``user_files/`` folder (preserved across upgrades) and
mirrors the last N records into an in-memory ring buffer.  The ring buffer is
what the **Logs** tab of the settings dialog shows, so you can debug the
add-on live without touching the shell.

Typical usage from other modules::

    from .logging import get_logger
    logger = get_logger()
    logger.debug("dialing deck_browser_title ...")
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from collections import deque
from typing import Callable, List, Tuple

from aqt import mw

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Number of recent records kept in memory for the UI log tab.
_RING_SIZE = 2000

#: Rotating file size cap (bytes) and number of backups.
_LOG_MAX_BYTES = 1_000_000
_LOG_BACKUP_COUNT = 2

#: Formatter used for both the file and the in-memory ring.
_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
# Ring buffer + notification
# ---------------------------------------------------------------------------

#: (levelno, formatted_line) tuples, oldest-first.
_ring: "deque[Tuple[int, str]]" = deque(maxlen=_RING_SIZE)

#: Callables invoked (with the new formatted line + levelno) after each emit.
_subscribers: List[Callable[[int, str], None]] = []


def subscribe(callback: Callable[[int, str], None]) -> None:
    """Register ``callback(levelno, line)`` to be called for each new record."""
    if callback not in _subscribers:
        _subscribers.append(callback)


def unsubscribe(callback: Callable[[int, str], None]) -> None:
    """Remove a previously registered callback."""
    if callback in _subscribers:
        _subscribers.remove(callback)


def _notify(levelno: int, line: str) -> None:
    for callback in list(_subscribers):
        try:
            callback(levelno, line)
        except Exception:
            pass


class _RingHandler(logging.Handler):
    """Appends formatted records to the ring buffer and notifies subscribers."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            line = self.format(record)
        except Exception:  # never let logging break the app
            return
        _ring.append((record.levelno, line))
        _notify(record.levelno, line)


# ---------------------------------------------------------------------------
# Logger setup (idempotent)
# ---------------------------------------------------------------------------

_log_folder = None
_file_path = None
_log = logging.getLogger("deck_name_and_tags_in_title")
_log._dnat_logging_ready = False  # type: ignore[attr-defined]


def _ensure_user_files_folder() -> str:
    global _file_path
    if _file_path is not None:
        return _file_path
    addon_dir = mw.addonManager.addonsFolder(__name__)
    user_files = os.path.join(addon_dir, "user_files")
    try:
        os.makedirs(user_files, exist_ok=True)
    except OSError:
        # Fall back to plain writing into the add-on folder if needed.
        user_files = addon_dir
    _file_path = os.path.join(user_files, "deck_name_and_tags_in_title.log")
    return _file_path


def _setup() -> None:
    if getattr(_log, "_dnat_logging_ready", False):
        return
    _log.setLevel(logging.DEBUG)
    _log.propagate = False

    fmt = logging.Formatter(_FORMAT, _DATEFMT)

    ring = _RingHandler()
    ring.setFormatter(fmt)
    ring.setLevel(logging.DEBUG)
    _log.addHandler(ring)

    try:
        path = _ensure_user_files_folder()
        file_handler = logging.handlers.RotatingFileHandler(
            path,
            maxBytes=_LOG_MAX_BYTES,
            backupCount=_LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(logging.DEBUG)
        _log.addHandler(file_handler)
    except OSError:
        # File-based logging is best-effort; the ring still works.
        pass

    _log._dnat_logging_ready = True  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_logger() -> logging.Logger:
    """Return the add-on's logger, setting it up on first use."""
    _setup()
    return _log


def snapshot(min_level: int = logging.DEBUG) -> List[str]:
    """Return recent log lines (formatted) with levelno >= ``min_level``."""
    _setup()
    if min_level > logging.NOTSET:
        return [line for lvl, line in _ring if lvl >= min_level]
    return [line for _, line in _ring]


def clear() -> None:
    """Clear the in-memory ring buffer shown in the UI."""
    _ring.clear()


def ring_size() -> int:
    """Return how many records are currently held in the in-memory ring."""
    return len(_ring)


def log_file_path() -> str:
    """Return the on-disk path of the rotating log file ('' if unavailable)."""
    _setup()
    return _file_path or ""


# Convenience: expose standard level constants at module level.
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL