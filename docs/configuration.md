# Configuration Reference

All behaviour is stored in a JSON object that Anki merges for you: the
add-on ships default values in `addon/config.json`, and any user overrides
are kept in Anki's `meta.json` and merged on top of the defaults by
`addonManager.getConfig()`.

The recommended way to edit these values is the **graphical settings dialog**
(**Tools → Add-ons → Deck Name & Tags in Title → Config**), which maps
1:1 onto the keys below.

## Shipped default file (`addon/config.json`)

```json
{
  "title_content": "both",
  "title_separator": " – ",
  "tag_separator": ", ",
  "max_tags": 5,
  "show_subdeck": true,
  "subdeck_format": "{parent}::{child}",
  "use_argv_0": false
}
```

## Key reference

### `title_content` — *string*, default `"both"`

Controls what appears in the window title while reviewing.

| Value | Effect |
|-------|--------|
| `"both"` | Deck name **and** the note's tags. *(default)* |
| `"deck"` | Only the deck name (classic behaviour). |
| `"tags"` | Only the note's tags. |
| `"none"` | Nothing extra — just your profile & "Anki". |

Tags belong to *notes*, not cards; they are read from the note behind the
reviewed card via `card.note().tags`. Tags are only available while a card is
being reviewed — the deck browser and the deck overview never show tags.

### `title_separator` — *string*, default `" – "`

Text placed between the title parts (content, profile name, program name).
Defaults to a spaced en-dash. Common alternatives: `" : "`, `" - "`, `" • "`.

### `tag_separator` — *string*, default `", "`

How several tags are joined, e.g. `"tags:English, Grammar"`.

### `max_tags` — *integer*, default `5`

Maximum number of tags printed before they are truncated (`0` = no limit).
Keeps the window title short on decks with many tags.

### `show_subdeck` — *boolean*, default `true`

When reviewing a card that lives in a sub-deck, prepend the sub-deck name to
the title so you know how deep you are. When `false`, only the parent
(clicked-on) deck is shown.

### `subdeck_format` — *string*, default `"{parent}::{child}"`

Template for combining the parent deck and the sub-deck. Supported fields:

| Field | Meaning |
|-------|---------|
| `{parent}` | The deck you clicked on in the deck browser. |
| `{child}` | The sub-deck you descended into (relative path). |
| `{homeDeck}` | The home deck (when reviewing a filtered/cram deck). |

`"{parent}:–:{child} ({homeDeck})"` reproduces the classic layout.

### `use_argv_0` — *boolean*, default `false`

When `true`, use `os.path.basename(sys.argv[0])` as the program name instead
of the literal string `"Anki"` (mostly relevant for custom launchers).

## Validation / coercion

`addon/config.py` never trusts the raw JSON. Each key is coerced when read:

- `title_content` is restricted to `both / deck / tags / none`
  (anything else falls back to `"both"`).
- `max_tags` is clamped to `0..50`.
- booleans accept `true/false`, `1/0`, and common string forms.
- Unknown keys / stale user config are handled by `ensure_defaults()`, which
  back-fills every missing key from the defaults and persists the result.

## Changing settings

- **From the GUI (recommended)** — the settings dialog writes the full dict
  via `addonManager.writeConfig` and calls `refresh_settings()`, so the
  change is applied immediately — no restart needed.
- **From `meta.json`** — open the add-ons window → the add-on → **View
  Files** → edit `meta.json` → `"config": { … }`.
- If you hand-edit, avoid underscore-prefixed key names (reserved by Anki).

## Where the defaults live (source of truth)

The canonical defaults are declared in **`addon/constants.py`** (`DEFAULTS`).
`addon/config.json` mirrors them so Anki can show the config editor, and
`docs/configuration.md` keeps this human-readable reference in sync.