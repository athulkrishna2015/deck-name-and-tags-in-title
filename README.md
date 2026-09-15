# Deck Name & Tags in Title

An Anki 2.1 add-on that shows the current **deck name** and/or the current
card's **tags** in the Anki window title, so you always know where you are.

Inspired by the classic ospalh
[`deck_name_in_title`](https://github.com/ospalh/anki-addons/tree/develop/deck_name_in_title)
add-on and extended with tag support and a graphical configuration dialog.

## Features

- Show the **deck name**, the **current card's tags**, **both** (default) or
  **nothing extra in the window title, fully configurable from the GUI.
- Tags are read from the card being reviewed, so you see at a glance which
  topic you are studying.
- **Custom config dialog** (**Tools → Add-ons → Deck Name & Tags in Title →
  Config**) — no manual JSON editing needed.
- Configurable separators, maximum tag count, sub-deck handling and program
  name behaviour.
- Settings apply immediately (no restart required).

## Install

### From the package (`.ankiaddon)

1. Open Anki.
2. **Tools → Add-ons → Get Add-ons… → Install from file…** and pick the
   `.ankiaddon` file (or Vendor / install the package).
3. Restart Anki.

### From source (development)

Clone the repository and symlink the `addon/` folder into your Anki add-ons
folder:

```shell
# Linux / macOS
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/deck_name_and_tags_in_title
```

See [docs/setup.md](docs/setup.md) for full instructions, the symlink helper,
building and the packaging/release workflow.

## Configuration

The behaviour is fully described in [docs/configuration.md](docs/configuration.md)
(A JSON key reference with defaults) and in the in-app settings dialog.

| Key | Default | Meaning |
|-----|---------|---------|
| `title_content` | `"both"` | `"both"`, `"deck"`, `"tags"` or `"none"` |
| `title_separator` | `" – "` | separator between title parts |
| `tag_separator` | `", "` | separator between tags |
| `max_tags` | `5` | max tags shown (`0` = no limit) |
| `show_subdeck` | `true` | show the sub-deck during review |
| `subdeck_format` | `{parent}::{child}` | sub-deck template |
| `use_argv_0` | `false` | use program file name instead of "Anki" |

## Documentation

- [Setup / Install & Symlink](docs/setup.md)
- [Configuration (keys, defaults, JSON)](docs/configuration.md)
- [Architecture & Code](docs/architecture.md)

## Changelog

See [changelog.md](changelog.md).

## License

GNU AGPL, version 3 or later — http://www.gnu.org/licenses/agpl.html