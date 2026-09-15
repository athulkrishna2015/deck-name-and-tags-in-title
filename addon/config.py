# -*- mode: python ; coding: utf-8 -*-
"""Configuration loading, coercion and caching.

The add-on stores its configuration through Anki's ``addonManager``.  A
``config.json`` ships the default values; any user overrides are stored by
Anki in ``meta.json`` and merged on top of the defaults by ``getConfig``.

This module exposes a frozen ``Settings`` object so the rest of the code
never deals with raw, un-validated JSON values.  ``get_settings()`` returns a
cached copy; ``refresh_settings()`` re-reads it (used after the config editor
saves) so changes take effect without restarting Anki.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aqt import mw

from .constants import (
    CFG_CONTENT,
    CFG_SEPARATOR,
    CFG_TAG_SEPARATOR,
    CFG_MAX_TAGS,
    CFG_IGNORED_TAGS,
    CFG_SHOW_SUBDECK,
    CFG_SUBDECK_FORMAT,
    CFG_USE_ARGV0,
    CONTENT_VALUES,
    DEFAULTS,
)


@dataclass
class Settings:
    """Coerced, validated configuration values used at runtime."""

    title_content: str = DEFAULTS[CFG_CONTENT]
    title_separator: str = DEFAULTS[CFG_SEPARATOR]
    tag_separator: str = DEFAULTS[CFG_TAG_SEPARATOR]
    max_tags: int = DEFAULTS[CFG_MAX_TAGS]
    ignored_tags: list = field(default_factory=list)
    show_subdeck: bool = DEFAULTS[CFG_SHOW_SUBDECK]
    subdeck_format: str = DEFAULTS[CFG_SUBDECK_FORMAT]
    use_argv_0: bool = DEFAULTS[CFG_USE_ARGV0]


# Module-level cache so we do not hit ``getConfig`` on every title update.
_settings: Settings | None = None


def get_config() -> dict[str, Any]:
    """Return the raw merged configuration (defaults + user overrides)."""
    # Anki returns None when no config.json is shipped; plain dict otherwise.
    return mw.addonManager.getConfig(__name__) or {}


def save_config(cfg: dict[str, Any]) -> None:
    """Persist a full configuration dictionary through Anki's addonManager."""
    mw.addonManager.writeConfig(__name__, cfg)


def ensure_defaults() -> dict[str, Any]:
    """Backfill any missing keys with defaults and persist the result."""
    cfg = get_config()
    changed = False
    for key, value in DEFAULTS.items():
        if key not in cfg:
            cfg[key] = value
            changed = True
    if changed:
        save_config(cfg)
    return cfg


# ---------------------------------------------------------------------------
# Coercion helpers
# ---------------------------------------------------------------------------

def _as_str(value: Any, default: str) -> str:
    if isinstance(value, str):
        return value
    return default


def _as_content(value: Any) -> str:
    """Validate/normalise the ``title_content`` value."""
    if isinstance(value, str) and value in CONTENT_VALUES:
        return value
    return DEFAULTS[CFG_CONTENT]


def _as_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"1", "true", "yes", "on"}:
            return True
        if normalized in {"0", "false", "no", "off", ""}:
            return False
    return default


def _as_int(value: Any, default: int, minimum: int = 0, maximum: int = 10**9) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _as_tag_list(value: Any) -> list[str]:
    """Normalise the ``ignored_tags`` value to a clean list of tag names."""
    raw: list[Any] = []
    if isinstance(value, str):
        import re

        raw = [p for p in re.split(r"[,\s;]+", value) if p]
    elif isinstance(value, (list, tuple)):
        raw = list(value)
    cleaned: list[str] = []
    seen: set[str] = set()
    for item in raw:
        text = str(item).strip().strip(",;")
        if not text:
            continue
        lowered = text.lower()
        if lowered not in seen:
            seen.add(lowered)
            cleaned.append(text)
    return cleaned


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _build_settings(cfg: dict[str, Any]) -> Settings:
    return Settings(
        title_content=_as_content(cfg.get(CFG_CONTENT)),
        title_separator=_as_str(cfg.get(CFG_SEPARATOR), DEFAULTS[CFG_SEPARATOR]),
        tag_separator=_as_str(cfg.get(CFG_TAG_SEPARATOR), DEFAULTS[CFG_TAG_SEPARATOR]),
        max_tags=_as_int(cfg.get(CFG_MAX_TAGS), DEFAULTS[CFG_MAX_TAGS], minimum=0, maximum=50),
        ignored_tags=_as_tag_list(cfg.get(CFG_IGNORED_TAGS)),
        show_subdeck=_as_bool(cfg.get(CFG_SHOW_SUBDECK), DEFAULTS[CFG_SHOW_SUBDECK]),
        subdeck_format=_as_str(cfg.get(CFG_SUBDECK_FORMAT), DEFAULTS[CFG_SUBDECK_FORMAT]),
        use_argv_0=_as_bool(cfg.get(CFG_USE_ARGV0), DEFAULTS[CFG_USE_ARGV0]),
    )


def refresh_settings() -> Settings:
    """Re-read the configuration from disk and refresh the cached copy."""
    global _settings
    cfg = ensure_defaults()
    _settings = _build_settings(cfg)
    return _settings


def get_settings() -> Settings:
    """Return the cached, validated settings (loaded lazily)."""
    global _settings
    if _settings is None:
        _settings = _build_settings(ensure_defaults())
    return _settings