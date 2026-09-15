# Architecture & Code

This document describes the full architecture of the *Deck Name & Tags in
Title* add-on: module-by-module responsibilities, the data flow that ends up
in the window title, the hooks that are used, and how the package is built.

## Overview

```
                    ┌──────────────────────────────────────────────┐
                    │                 anki / aqt                    │
                    │   mw.addonManager ─ Python config (json/meta) │
                    │   mw.overview / mw.deckBrowser / mw.reviewer  │
                    └───────────────┬──────────────────────────────┘
                                    │ imports / hooks / wraps
                    ┌───────────────▼──────────────────────────────┐
                    │                  addon package                │
                    │  __init__.py   DeckNamer  (title builder)     │
                    │  config.py     Settings   (validated config)  │
                    │  constants.py  keys + DEFAULTS (contract)     │
                    │  ui.py         SettingsDialog (config UI)     │
                    └──────────────────────────────────────────────┘
```

The add-on is a tiny Python package loaded by Anki from the `addon/` folder.
At import time it (a) wires up a custom **Config** button, (b) registers a
`setConfigUpdatedAction` callback so config edits apply instantly, and
(c) patches the deck-browser/overview title setters and the reviewer
`showQuestion` hook.

## Module map

### `addon/constants.py` — the config contract

Single source of truth for configuration.

- Field-name constants (e.g. `CFG_CONTENT = "title_content"`).
- `CONTENT_VALUES` / `CONTENT_LABELS` — the allowed `title_content` values
  and their human-readable GUI labels.
- `DEFAULTS` — the canonical default dict that `config.json`,
  `ensure_defaults()`, the dialog reset and this documentation all mirror.

### `addon/config.py` — validated settings

Bridges Anki's JSON config and the rest of the code.

- `get_config()` → raw merged dict from `addonManager.getConfig`.
- `save_config(cfg)` → `addonManager.writeConfig`.
- `ensure_defaults()` → back-fills missing keys and persists.
- `_as_*` coercion helpers normalise/validate every value.
- `Settings` (a `@dataclass`) holds typed, validated values.
- `get_settings()` → lazy cached `Settings`; `refresh_settings()` re-reads it.

The cache (module-global `_settings`) lets the hot `showQuestion` path skip
re-parsing JSON on every card.

### `addon/ui.py` — the config UI

Provides the graphical configuration dialog.

- `SettingsDialog(QDialog)` — two groups of widgets.
  - **Title content:** a `QComboBox` over `CONTENT_LABELS`.
  - **Formatting:** separators (`QLineEdit`), `max_tags` (`QSpinBox`),
    `show_subdeck` (`QCheckBox`), `subdeck_format` (`QLineEdit`),
    `use_argv_0` (`QCheckBox`).
  - Save → `save_config()` + `refresh_settings()`; **Reset to defaults**
    prompts then writes `dict(DEFAULTS)`.
- `register_config_action()` → binds the add-ons list **Config** button via
  `mw.addonManager.setConfigAction`; if that API is unavailable it falls back
  to a **Tools** menu entry.
- PyQt6/PyQt5 compatibility: `QMessageBox.StandardButton` enum fallback and
  `exec()`/`exec_()` detection.
- The dialog is a `QTabWidget` with two tabs: **Settings** (title content +
  formatting) and **Logs** (live debug viewer driven by `logging.py`).

### `addon/logging.py` — diagnostic logging

- Sets up a module-level `logging.Logger` (idempotent) that writes to a
  rotating file at `user_files/deck_name_and_tags_in_title.log` (the add-on's
  `user_files/` folder is preserved across upgrades) and mirrors the last
  2000 records into an in-memory ring buffer.
- The ring buffer + `snapshot()`, `clear()`, `log_file_path()`, `ring_size()`
  helpers are what the **Logs** tab renders.
- Other modules obtain the logger via `get_logger()` and call
  `logger.debug(...)`; failures inside logging never break the app.

### `addon/__init__.py` — integration & title building

- `wrapmethod()` — a small, self-contained re-implementation of bound-method
  wrapping (used because `anki.hooks.wrap` does not preserve bound methods
  for this use-case).
- `DeckNamer` — builds the title string.
  - `get_deck_name()` → `mw.col.decks.current()["name"]`.
  - `get_profile_string()` → profile name when >1 profile exists.
  - `get_tags_string()` → the tags of the *note* behind the reviewed card,
    via `card.note().tags` (tags belong to notes, not cards), minus scheduling
    markers (`marked`, `suspended`, `leech`), truncated to `max_tags`, joined
    with `tag_separator`.
  - `_content_title()` → reduces `(deck, tags)` to one string according to
    `title_content`.
  - `_join()` → joins the non-empty parts with `title_separator`.
  - `deck_browser_title()` / `overview_title()` / `card_title()` set the
    window title via `mw.setWindowTitle`.
- At the bottom, registration:
  - `ui.register_config_action()`
  - `setConfigUpdatedAction(__name__, _on_config_updated)` → refresh cache.
  - Wrap `mw.deckBrowser.show` and `mw.overview.show`.
  - `addHook("showQuestion", deck_namer.card_title)`.

## Title-building data flow

```
showQuestion fired
      │  deck_namer.card_title()
      ▼
mw.reviewer.card  ──► did / odid ──► mw.col.decks.get(...)  ──► sub-deck name
mw.reviewer.card.tags ──► filter markers ──► truncate ──► join (tag_separator)
get_settings().title_content decides deck / tags / both / none
      ▼
title = content + separator + profile + separator + prog name
      ▼
mw.setWindowTitle(title)
```

Decks alone are shown at the overview (`overview_title`); the deck browser
shows only profile + program name (`deck_browser_title`), because there is no
"current card" from which tags could be read.

## Hooks & Anki APIs used

| API | Purpose |
|-----|---------|
| `mw.deckBrowser.show` (wrapped) | refresh title in the deck browser |
| `mw.overview.show` (wrapped) | refresh title at the deck overview |
| `addHook("showQuestion", …)` | refresh title each time a card is shown |
| `mw.col.decks.current()/get()` | resolve deck / sub-deck names |
| `mw.reviewer.card.note().tags` | tags of the note behind the reviewed card |
| `addon/logging` (`get_logger`, `snapshot`) | file + in-memory logging for the Logs tab |
| `mw.addonManager.getConfig/writeConfig` | read / persist config |
| `mw.setConfigAction` | point the Config button at our dialog |
| `mw.setConfigUpdatedAction` | re-read config when changed |
| `mw.setWindowTitle` | set the window title |

Everything is wrapped in defensive `try/except` so a missing API never
crashes the reviewer.

## Packaging

`make_ankiaddon.py` walks `addon/` and produces a timestamped
`.ankiaddon` zip with `__init__.py` at its root. It honours `.gitignore`
rules and excludes runtime state (`meta.json`, `__pycache__`, logs).
`bump.py` centralises version bumps, keeping `manifest.json` and `VERSION`
in sync.

Included in the package: the five Python modules, `config.json`,
`config.md`, `manifest.json`, `VERSION`.
Excluded: `__pycache__/`, `.pyc`, logs, `meta.json`, and any `.gitignore`d
paths.

## Testing / validation

- All modules are pure-Python importable; the syntax can be checked with
  `ast.parse` (see [docs/setup.md](setup.md#testing--syntax-check)).
- Behaviour is best validated in a live Anki reviewer: pick `title_content`
  `both`/`deck`/`tags` and observe the title while reviewing cards in a
  sub-deck that carry tags.
  `exec()`/`exec_()` detection.