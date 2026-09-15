# -*- mode: python ; coding: utf-8 -*-
"""Deck Name & Tags in Title — Anki 2.1 add-on.

Shows the deck name and/or the current card's tags in the Anki window title,
so you always know where you are.  The behaviour is fully configurable from
**Tools → Add-ons → deck_name_and_tags_in_title → Config**:

* ``title_content`` — show the deck name, the current card tags, both
  (default) or nothing.
* separators, sub-deck handling, tag limit and program-name behaviour.

Inspired by the classic ospalh ``deck_name_in_title`` add-on.
"""

from __future__ import annotations

import functools
import os
import sys
import types

from anki.hooks import addHook
from aqt import mw

from .config import get_settings, refresh_settings
from . import ui


def wrapmethod(orig, wrapper, pos="after"):
    """Like ``anki.hooks.wrap``, but for bound methods.

    Caveat: does not preserve function signatures.
    """

    if pos == "after":
        def wrapped(self, *args, **kwargs):
            orig(*args, **kwargs)
            return wrapper(*args, **kwargs)
    elif pos == "before":
        def wrapped(self, *args, **kwargs):
            wrapper(*args, **kwargs)
            return orig(*args, **kwargs)
    else:
        def wrapped(self, *args, **kwargs):
            return wrapper(_old=orig, *args, **kwargs)
    if not isinstance(wrapper, types.MethodType) or wrapper.__self__ is None:
        # wrapper is not a bound method, need to pass self
        wrapper = functools.partial(wrapper, orig.__self__)

    # Copy over attributes such as __name__ or __annotations__
    wrapped = functools.update_wrapper(wrapped, orig.__func__)
    # Convert wrapped function to bound method
    wrapped = wrapped.__get__(orig.__self__, orig.__class__)
    return wrapped


class DeckNamer(object):
    """Builds the window title from the current deck and/or card tags."""

    def __init__(self):
        self.profile_string = ""

    # -- program name -------------------------------------------------------
    def get_prog_name(self):
        """Return either "Anki" or ``argv[0]``'s base name."""
        settings = get_settings()
        if settings.use_argv_0 and sys.argv[0]:
            return os.path.basename(sys.argv[0])
        return "Anki"

    # -- data helpers ---------------------------------------------------------
    def get_deck_name(self):
        """Return the current deck's name ('' when none is available)."""
        try:
            return mw.col.decks.current()["name"]
        except Exception:
            return ""

    def get_profile_string(self):
        """Return the profile name, or '' when there is only one profile."""
        try:
            if len(mw.pm.profiles()) > 1 and mw.pm.name:
                self.profile_string = mw.pm.name
            else:
                self.profile_string = ""
        except Exception:
            self.profile_string = ""
        return self.profile_string

    def get_tags_string(self):
        """Return the tags of the card currently being reviewed ('' otherwise)."""
        settings = get_settings()
        card = getattr(mw.reviewer, "card", None)
        if card is None:
            return ""
        tags = list(getattr(card, "tags", None) or [])
        # Scheduling markers (used by some add-ons) carry no learning value.
        tags = [t for t in tags if t not in ("marked", "suspended", "leech")]
        max_tags = settings.max_tags
        if max_tags and len(tags) > max_tags:
            tags = tags[:max_tags]
        return settings.tag_separator.join(tags)

    @staticmethod
    def _join(parts):
        return get_settings().title_separator.join(p for p in parts if p)

    def _content_title(self, deck_part="", tags=""):
        """Combine deck/tags according to ``title_content``."""
        mode = get_settings().title_content
        if mode == "deck":
            return deck_part
        if mode == "tags":
            return tags
        if mode == "none":
            return ""
        # "both"
        return self._join((deck_part, tags))

    # -- title setters ---------------------------------------------------------
    def deck_browser_title(self):
        """Window title in the deck browser (no current card, so no tags)."""
        mw.setWindowTitle(
            self._join((self.get_profile_string(), self.get_prog_name()))
        )

    def overview_title(self):
        """Window title at the deck overview (tags not available there)."""
        content = self._content_title(deck_part=self.get_deck_name())
        mw.setWindowTitle(
            self._join((content, self.get_profile_string(), self.get_prog_name()))
        )

    def card_title(self):
        """Window title while reviewing: deck name and/or card tags."""
        settings = get_settings()
        deck_name = self.get_deck_name()
        subdeck_name = deck_name
        home = ""
        try:
            did = mw.reviewer.card.did
            odid = mw.reviewer.card.odid
            if did:
                subdeck_name = mw.col.decks.get(did)["name"] or deck_name
            if odid:
                home = mw.col.decks.get(odid)["name"] or ""
                if home == "Default":
                    home = ""
        except Exception:
            pass

        if (
            deck_name
            and settings.show_subdeck
            and settings.subdeck_format
            and subdeck_name != deck_name
        ):
            child = subdeck_name
            prefix = len(deck_name) + 2  # parent name + "::"
            if prefix <= len(subdeck_name):
                child = subdeck_name[prefix:]
            deck_part = settings.subdeck_format.format(
                parent=deck_name, child=child, homeDeck=home
            )
        else:
            deck_part = deck_name

        tags = self.get_tags_string()
        content = self._content_title(deck_part, tags)
        mw.setWindowTitle(
            self._join((content, self.get_profile_string(), self.get_prog_name()))
        )


def _on_config_updated(*_args, **_kwargs):
    """Re-read configuration after the user edits it (no restart needed)."""
    refresh_settings()


# Register the Config button UI and keep the runtime config in sync.
ui.register_config_action()
try:
    mw.addonManager.setConfigUpdatedAction(__name__, _on_config_updated)
except Exception:
    pass

deck_namer = DeckNamer()
try:
    mw.deckBrowser.show = wrapmethod(
        mw.deckBrowser.show, deck_namer.deck_browser_title
    )
except Exception:
    pass
try:
    mw.overview.show = wrapmethod(mw.overview.show, deck_namer.overview_title)
except Exception:
    pass
addHook("showQuestion", deck_namer.card_title)