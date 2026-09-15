# -*- mode: python ; coding: utf-8 -*-
"""Open the config dialog on the Support tab after an update.

Called once per version (stored in meta.json ``last_seen_version``) and
skipped when the supporter opted out. Scheduling is deferred via
``QTimer.singleShot`` / ``profileLoaded`` so Anki startup is not slowed.
"""
from __future__ import annotations

_TAB_TITLE = "Support"


def _addon_package() -> str:
    try:
        from aqt import mw

        key = mw.addonManager.addonFromModule(__name__)
        if key:
            return key
    except Exception:
        pass
    name = (__package__ or "").split(".")[0]
    if name:
        return name
    return "deck_name_and_tags_in_title"


def _current_version() -> str:
    try:
        from .constants import ADDON_VERSION
        if ADDON_VERSION:
            return str(ADDON_VERSION)
    except Exception:
        pass
    try:
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, "VERSION"), encoding="utf-8") as fh:
            return fh.read().strip()
    except Exception:
        return "0"


def _read_meta() -> dict:
    try:
        from aqt import mw
        return dict(mw.addonManager.addonMeta(_addon_package()) or {})
    except Exception:
        return {}


def _write_meta(meta: dict) -> None:
    try:
        from aqt import mw
        mw.addonManager.writeAddonMeta(_addon_package(), meta)
    except Exception:
        pass


def should_show_welcome() -> bool:
    """True when the version changed and the user did not opt out."""
    meta = _read_meta()
    if bool(meta.get("supporter_opt_out", False)):
        return False
    return str(meta.get("last_seen_version", "")) != _current_version()


def mark_welcome_seen() -> None:
    meta = _read_meta()
    meta["last_seen_version"] = _current_version()
    _write_meta(meta)


def open_config_on_support_tab() -> None:
    """Open the settings dialog focused on the Support tab."""
    try:
        from aqt import mw
        from .ui import open_settings
        open_settings(initial_tab=_TAB_TITLE)
    except Exception:
        pass


def _maybe_show() -> None:
    try:
        if should_show_welcome():
            mark_welcome_seen()
            open_config_on_support_tab()
    except Exception:
        pass


def schedule_update_welcome(delay_ms: int = 1200) -> None:
    """Schedule the welcome check after startup without blocking it."""
    try:
        from aqt import mw, gui_hooks
    except Exception:
        return
    def _arm() -> None:
        try:
            from aqt.qt import QTimer
            QTimer.singleShot(int(delay_ms), _maybe_show)
        except Exception:
            try:
                _maybe_show()
            except Exception:
                pass
    try:
        gui_hooks.profile_did_open.append(lambda: _arm())
    except Exception:
        pass
    try:
        # Fallback for tests / environments without the hook run yet.
        _arm()
    except Exception:
        pass
