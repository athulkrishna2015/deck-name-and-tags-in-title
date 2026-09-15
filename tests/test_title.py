"""Lightweight functional test for the Deck Name & Tags in Title add-on.

The test stubs anki/aqt/mw enough to import the add-on package and verify the
window title is built correctly in every ``title_content`` mode.

Run:  python3 -B tests/test_title.py
"""

import sys
import types

# --------------------------------------------------------------------------
# Stub the Anki API so the add-on can be imported without Anki installed.
# --------------------------------------------------------------------------
class _DeckBrowser:
    def show(self):
        return None


class _Overview:
    def show(self):
        return None


class _DeckCollection:
    def __init__(self):
        self._current = {"name": "Spanish"}
        self._decks = {1: {"name": "Spanish"}, 2: {"name": "Spanish::Basics"}}

    def current(self):
        return dict(self._current)

    def get(self, did):
        return dict(self._decks.get(did, {}))


class _Reviewer:
    def __init__(self):
        self.card = None


class _PM:
    def __init__(self):
        self.name = "me"
        self._n = 1

    def profiles(self):
        return list(range(self._n))


class _AddonManager:
    def __init__(self):
        self.conf = {
            "title_content": "both",
            "title_separator": " – ",
            "tag_separator": ", ",
            "max_tags": 5,
            "ignored_tags": [],
            "show_subdeck": True,
            "subdeck_format": "{parent}::{child}",
            "use_argv_0": False,
        }
        self.updated = None
        import tempfile
        self._folder = tempfile.mkdtemp(prefix="dnat_test_")

    def getConfig(self, module):
        return dict(self.conf)

    def writeConfig(self, module, conf):
        self.conf = dict(conf)

    def setConfigAction(self, module, fn):
        self.action = fn

    def setConfigUpdatedAction(self, module, fn):
        self.updated = fn

    def addonsFolder(self, module=None):
        return self._folder


class _Note:
    def __init__(self, tags):
        self.tags = list(tags)
        self.nid = 1234


class _Card:
    def __init__(self, tags, did=2, odid=None):
        self._note = _Note(tags)
        self.did = did
        self.odid = odid

    def note(self):
        return self._note


class _MW:
    def __init__(self):
        self.addonManager = _AddonManager()
        self.col = types.SimpleNamespace(decks=_DeckCollection())
        self.pm = _PM()
        self.reviewer = _Reviewer()
        self.deckBrowser = _DeckBrowser()
        self.overview = _Overview()
        self.title = ""

    def setWindowTitle(self, title):
        self.title = title


# Install the stubs into sys.modules so `from aqt import mw` works.
aqt = types.ModuleType("aqt")
aqt.mw = _MW()
sys.modules["aqt"] = aqt
aqt_qt = types.ModuleType("aqt.qt")
sys.modules["aqt.qt"] = aqt_qt


def _make_qt_stub():
    """Create trivial classes so `from aqt.qt import QDialog, ...` works."""
    names = [
        "QApplication", "QCheckBox", "QComboBox", "QCompleter", "QDesktopServices",
        "QDialog", "QFont", "QFormLayout", "QGroupBox", "QHBoxLayout", "QLabel",
        "QLineEdit", "QListView", "QListWidget", "QListWidgetItem", "QMessageBox",
        "QPlainTextEdit", "QPushButton", "QSpinBox", "QStringListModel",
        "QTabWidget", "QTimer", "QUrl", "QVBoxLayout", "QWidget",
    ]

    class _Stub:
        def __getattr__(self, item):
            raise AttributeError(item)

    for name in names:
        if not hasattr(aqt_qt, name):
            setattr(aqt_qt, name, _Stub)

    # QMessageBox.StandardButton used by _standard_button()
    class _StandardButton:
        Yes = 1
        No = 0
    aqt_qt.QMessageBox.StandardButton = _StandardButton
    aqt_qt.QMessageBox.No = 0
    aqt_qt.QMessageBox.Yes = 1
    aqt_qt.QMessageBox.question = staticmethod(lambda *a, **k: 0)


_make_qt_stub()

anki = types.ModuleType("anki")
hooks = types.ModuleType("anki.hooks")


def addHook(name, fn):
    aqt.mw._hooks = getattr(aqt.mw, "_hooks", []) + [(name, fn)]
hooks.addHook = addHook
sys.modules["anki"] = anki
sys.modules["anki.hooks"] = hooks

PROJECT_ROOT = "/mnt/0946E88701BE265B/portable/anki/addons/    deck_name_and_tags_in_title"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import addon  # noqa: E402 - triggers registration
from addon.config import get_settings, refresh_settings  # noqa: E402

mw = aqt.mw
# The add-on module-level code already registered the wrap on showQuestion.
results = []


def _conf(**overrides):
    cfg = dict(mw.addonManager.conf)
    cfg.update(overrides)
    mw.addonManager.conf = cfg
    refresh_settings()


def _check(label, expected):
    ok = mw.title == expected
    results.append((label, ok, mw.title, expected))
    return ok


# 1) Default "both"
_conf(title_content="both")
mw.reviewer.card = _Card(tags=["espana", "vocab", "marked"])
addon.deck_namer.card_title()
assert _check("both shows deck + tags", "Spanish::Basics – espana, vocab – Anki"), mw.title

# 2) "deck" only
_conf(title_content="deck")
addon.deck_namer.card_title()
assert _check("deck only", "Spanish::Basics – Anki"), mw.title

# 3) "tags" only
_conf(title_content="tags")
addon.deck_namer.card_title()
assert _check("tags only", "espana, vocab – Anki"), mw.title

# 4) "none"
_conf(title_content="none")
addon.deck_namer.card_title()
assert _check("none", "Anki"), mw.title

# 4b) max_tags truncation
_conf(title_content="tags", max_tags=1)
addon.deck_namer.card_title()
assert _check("tags truncated to 1", "espana – Anki"), mw.title

# 4c) ignored_tags filtering (case-insensitive)
_conf(title_content="tags", max_tags=0, ignored_tags=["Vocab"])
addon.deck_namer.card_title()
assert _check("ignored tag filtered", "espana – Anki"), mw.title

# 5) overview: no card -> deck only, no tags
_conf(title_content="both")
mw.reviewer.card = None
addon.deck_namer.overview_title()
assert _check("overview deck only", "Spanish – Anki"), mw.title

# 6) deck browser: profile + program name only
_conf(title_content="both")
addon.deck_namer.deck_browser_title()
assert _check("browser profile+Anki", "Anki"), mw.title  # 1 profile -> no profile string

print("\nAll checks passed:")
for label, ok, got, expected in results:
    print(f"  [{'OK' if ok else 'FAIL'}] {label}: got={got!r} expected={expected!r}")
print("\nPASSED")

# --------------------------------------------------------------------------
# Verify the Logs-tab backend (logging ring buffer + log file path).
# --------------------------------------------------------------------------
import os
from addon import logging as addon_logging

addon_logging.clear()
logger = addon_logging.get_logger()
logger.info("log-tab sanity message 42")
lines = addon_logging.snapshot(addon_logging.INFO)
hit = any("log-tab sanity message 42" in line for line in lines)
assert hit, f"ring buffer did not capture the message: {lines!r}"
assert addon_logging.ring_size() >= 1, "ring size should be >= 1"
path = addon_logging.log_file_path()
assert path and os.path.isfile(path), f"log file not created: {path!r}"
with open(path, encoding="utf-8") as fh:
    assert "log-tab sanity message 42" in fh.read(), "message missing from log file"
print("LOG-TAB BACKEND OK:", path)