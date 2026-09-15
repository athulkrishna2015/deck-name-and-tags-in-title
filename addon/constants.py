# -*- mode: python ; coding: utf-8 -*-
"""Centralised configuration field names, allowed values and defaults.

Keeping every magic string in one place makes the add-on easy to maintain:
the shipped ``config.json``, the native ``config.md`` schema-form editor, the
custom Qt settings dialog and the runtime ``config.py`` loader all agree on
the same contract.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Config keys
# ---------------------------------------------------------------------------

#: What to show in the window title: deck name, current card tags, both or none.
CFG_CONTENT = "title_content"

#: Separator placed between the content and the program name.
CFG_SEPARATOR = "title_separator"

#: Separator used to join multiple tags together.
CFG_TAG_SEPARATOR = "tag_separator"

#: Maximum number of tags to print (0 = unlimited). Avoids cluttered titles.
CFG_MAX_TAGS = "max_tags"

#: Note tags to ignore (never shown in the title). Editable in the Config UI.
CFG_IGNORED_TAGS = "ignored_tags"

#: Whether the sub-deck you descended into is shown during review.
CFG_SHOW_SUBDECK = "show_subdeck"

#: Template controlling how the parent deck and the sub-deck are combined.
CFG_SUBDECK_FORMAT = "subdeck_format"

#: Use ``argv[0]`` file name instead of the literal string "Anki".
CFG_USE_ARGV0 = "use_argv_0"

# ---------------------------------------------------------------------------
# Allowed values for ``title_content``  (value -> human readable label)
# ---------------------------------------------------------------------------

#: Valid values for :data:`CFG_CONTENT`.
CONTENT_VALUES = ("both", "deck", "tags", "none")

#: Human-readable labels shown in the configuration UI.
CONTENT_LABELS = {
    "both": "Deck name and tags",
    "deck": "Deck name only",
    "tags": "Current card tags only",
    "none": "Nothing (just program name)",
}

# ---------------------------------------------------------------------------
# Defaults (mirror ``config.json`` shipped with the add-on)
# ---------------------------------------------------------------------------

#: Default configuration values. Keep in sync with ``config.json``.
DEFAULTS = {
    CFG_CONTENT: "both",
    CFG_SEPARATOR: " – ",
    CFG_TAG_SEPARATOR: ", ",
    CFG_MAX_TAGS: 5,
    CFG_IGNORED_TAGS: [],
    CFG_SHOW_SUBDECK: True,
    CFG_SUBDECK_FORMAT: "{parent}::{child}",
    CFG_USE_ARGV0: False,
}

#: Current add-on version (mirrors ``VERSION``; used for update welcomes).
ADDON_VERSION = "2.2.0"
