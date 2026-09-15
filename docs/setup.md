# Setup & Installation

This add-on runs on **Anki 2.1** (Qt 6 / PyQt 6; Python 3.10+). It has no
third-party runtime dependencies.

## Requirements

- **Anki** 2.1.x or newer.
- An existing collection with at least one deck (and, for the tag feature,
  cards carrying tags).

## Install the packaged add-on

1. Open Anki.
2. **Tools → Add-ons → Get Add-ons… → Install from file…**.
3. Select the `.ankiaddon` file and restart Anki.
4. Optional: open **Tools → Add-ons → Deck Name & Tags in Title → Config**
   to tune the title contents.

## Develop locally (symlink)

The fastest way to test changes is to symlink the `addon/` folder directly
into your Anki add-ons folder, so Anki loads your live code on every restart.

```shell
git clone <this-repo> "deck_name_and_tags_in_title"
cd "deck_name_and_tags_in_title"
```

**Linux / macOS:**

```shell
ln -s "$(pwd)/addon" ~/.local/share/Anki2/addons21/deck_name_and_tags_in_title
```

**Windows (Admin):**

```powershell
mklink /D "%APPDATA%\Anki2\addons21\deck_name_and_tags_in_title" "%CD%\addon"
```

In this workspace the equivalent link is created by:

```shell
ln -s "……/addons/    deck_name_and_tags_in_title/addon" "……/addons/deck_name_and_tags_in_title"
```

## Repository layout

```
deck_name_and_tags_in_title/
├── addon/                    # the Anki add-on itself
│   ├── __init__.py           # title logic + hook/wrap registration
│   ├── constants.py          # config keys, allowed values, defaults
│   ├── config.py             # config load/save/coercion/caching
│   ├── ui.py                 # Qt config dialog + Config action wiring
│   ├── config.json           # shipped default values
│   ├── config.md             # reference shown by the native config editor
│   ├── manifest.json         # add-on name/package/version for Anki
│   └── VERSION               # plain-text version bump.py reads/writes
├── docs/                     # documentation (this folder)
├── bump.py                   # version bumping helper
├── make_ankiaddon.py         # builds the .ankiaddon package
├── changelog.md              # release history
└── README.md                 # quick start
```

## Testing / syntax check

All modules are import-safe and syntax-checkable without a running Anki:

```shell
python3 -c "import ast; [ast.parse(open(f'addon/{m}.py').read()) for m in ('__init__','config','constants','ui')]"
```

To run within a live Anki you can temporarily print/set a title in the
reviewer; see [docs/architecture.md](docs/architecture.md) for where the
relevant methods live.

## Building a release

```shell
# Auto-bump patch and build:
python3 make_ankiaddon.py

# Build with an explicit version (also syncs VERSION + manifest.json):
python3 make_ankiaddon.py 2.0.0

# Remove older local packages first:
python3 make_ankiaddon.py --clean
```

This writes a timestamped `Deck_Name_And_Tags_In_Title_vX.Y.Z_<ts>.ankiaddon`
in the repo root. See [docs/architecture.md](docs/architecture.md#packaging)
for the included/excluded files.

## Changelog

See [changelog.md](../changelog.md) for the full release history.