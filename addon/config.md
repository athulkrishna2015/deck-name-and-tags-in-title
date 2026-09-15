# Deck Name & Tags in Title — Configuration

This add-on shows the current deck name and/or the current card's tags in the
Anki window title. All behaviour is controlled from the JSON below, but the
recommended way to change it is the graphical settings window:

1. Open Anki.
2. **Tools → Add-ons** → select *Deck Name & Tags in Title*.
3. Click **Config** to open the settings dialog.

The dialog covers everything below; you normally never need to touch the
raw JSON.

## Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `title_content` | string | `"both"` | What appears in the window title: `"both"` (deck name + tags), `"deck"`, `"tags"`, or `"none"`. |
| `title_separator` | string | `" – "` | Text placed between the content, the profile name and the program name (a spaced en-dash by default). |
| `tag_separator` | string | `", "` | Text used to join several tags (e.g. `"foo, bar"`). |
| `max_tags` | integer | `5` | Maximum number of tags shown (`0` = no limit). Keeps the title short. |
| `show_subdeck` | boolean | `true` | When reviewing a card in a sub-deck, show which sub-deck you are in. |
| `subdeck_format` | string | `"{parent}::{child}"` | Templates how the parent deck and sub-deck are combined. Available fields: `{parent}`, `{child}`, `{homeDeck}`. |
| `use_argv_0` | boolean | `false` | Use the program's file name instead of the literal word "Anki". |

## Notes

* Tags are only available while a card is being reviewed; the deck browser
  and the deck overview therefore only ever use the deck name / program name.
* Internal scheduling markers (`marked`, `suspended`, `leech`) are filtered
  out of the tag list.
* Changes are applied immediately (no restart required).