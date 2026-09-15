# Changelog

All notable changes to the *Deck Name & Tags in Title* add-on are recorded
here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

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