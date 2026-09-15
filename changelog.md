# Changelog

All notable changes to the *Deck Name & Tags in Title* add-on are recorded
here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [2.2.0] — (2026-09-15)

### Added

- New `ignored_tags` config key (default `[]`): note tags that are never
  shown in the title, matched case-insensitively.
- The Config UI **Settings** tab now has an **Ignored tags** field with
  autocomplete fed by the collection's tag list, an **Ignoring now** list,
  and **Add typed tag** / **Remove selected** / **Refresh tag list** actions.
- New **Support** tab in the config dialog (`addon/tab_support.py`, QR images
  in `addon/Support/`): Ko-fi button plus UPI/BTC/ETH QR codes with
  copy-to-clipboard address rows, and an "I have supported this addon"
  checkbox stored in `meta.json` (`supporter_opt_out`).
- The config dialog now opens automatically on the **Support** tab once per
  update (`addon/update_welcome.py`, tracked via
  `meta.json:last_seen_version`), deferred past startup via
  `profile_did_open` + `QTimer.singleShot` so Anki startup is not slowed.
  Supporters who ticked the opt-out checkbox never see the auto-open.
- Config dialog refactored to one-tab-per-file: `addon/tab_settings.py`
  (Settings), `addon/tab_logs.py` (Logs), `addon/tab_support.py` (Support),
  with `addon/ui.py` kept as a thin shell.

### Fixed

- Fixed `TypeError: setCaseSensitivity(...): argument 1 has unexpected type
  'int'` crash when opening Config on Anki 26.08 / PyQt 6.11 (strict Qt6
  enums): `QCompleter.setCaseSensitivity()`, `QListWidget.setSelectionMode()`
  and `QPlainTextEdit.setLineWrapMode()` now pass real Qt6 enum values with
  Qt5 fallbacks instead of raw ints.
- Removed a leftover dead block in `SupportTabMixin.load_supporter_state()`
  that referenced an undefined `meta` variable.

## [2.1.1] — (2026-09-15)

### Fixed

- Fixed a `TypeError` crash when closing the settings dialog:
  `SettingsDialog.closeEvent()` now accepts and forwards Qt's `QCloseEvent`,
  so the **Logs** tab timer shuts down cleanly.

### Changed

- Added a **Fork / origin** section to `README.md`: this repository is not a
  GitHub fork, but a standalone extended successor of Roland Sieker's classic
  `deck_name_in_title` add-on (© 2012–2018, GNU AGPL v3+).

## [2.1.0] — (2026-09-15)

### Added

- **Logs tab** in the settings dialog (**Config → Logs**) for debugging:
  - Live view of recent add-on log records (auto-refreshes while open).
  - Filter by minimum level (DEBUG / INFO / WARNING / ERROR).
  - **Refresh**, **Copy**, **Clear** and **Open log file…** actions.
- New `addon/logging.py` module: rotating log file written to the add-on's
  `user_files/deck_name_and_tags_in_title.log` (preserved across upgrades)
  plus an in-memory ring buffer that powers the Logs tab.
- Debug logging added throughout the title-building code
  (`deck_browser_title`, `overview_title`, `card_title`, config reloads).

### Fixed

- **Tags now actually appear in the title.** Tags belong to *notes*, not
  cards — the previous code read `card.tags`, which does not exist, so tags
  silently never showed. It now resolves them correctly via
  `card.note().tags`.
- Settings dialog buttons (Save / Close / Reset) were never added to the
  dialog layout; they are now wired into the tabbed UI.

### Changed

- Settings dialog is now a `QTabWidget` with **Settings** and **Logs** tabs.

## [2.0.0] — (baseline)

### Added

- **Tags in the window title** — the current card's tags can now be shown
  while reviewing (new `title_content` mode `"tags"`).
- **"Deck name and tags" mode** — new default (`title_content = "both"`)
  shows the deck name *and* the current card's tags.
- **Graphical configuration dialog** — **Tools → Add-ons → Deck Name & Tags
  in Title → Config** now opens a Qt settings window (implemented via
  `addonManager.setConfigAction`), so no manual JSON editing is required.
- New configuration keys: `tag_separator`, `max_tags` (limit how many tags
  are printed), and `title_content` (choose `both` / `deck` / `tags` / `none`).
- Settings now apply immediately — changes are re-read via
  `setConfigUpdatedAction` without restarting Anki.
- Robust config handling in `addon/config.py` (coercion + validation) and a
  dedicated `addon/constants.py` for the config contract.
- Full developer/end-user documentation (`docs/`), a `changelog.md`, a
  `manifest.json`/`VERSION` pair, and a `config.md` reference for the native
  config editor.

### Changed

- Repo restructured from a single `addon/__init__.py` into a small package
  with clear separation of concerns (`constants.py`, `config.py`, `ui.py`,
  `__init__.py`).
- Program-name/profile handling refactored so separators are not duplicated.
- Sub-deck template now defaults to `{parent}::{child}` (fields supported:
  `{parent}`, `{child}`, `{homeDeck}`).

### Removed

- Hard-coded, edit-the-source configuration style (separator/sub-deck
  options are now real config values editable from the GUI).

## [1.4.0] — (baseline)

- Classic *deck name in title* behaviour (window title shows the current
  deck, sub-deck and profile, with a configurable separator). Config was
  edited by hand in `addon/__init__.py`.