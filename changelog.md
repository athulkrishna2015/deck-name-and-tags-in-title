# Changelog

All notable changes to the *Deck Name & Tags in Title* add-on are recorded
here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/).

## [2.0.0] — (unreleased)

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