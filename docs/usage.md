# Usage

## What you see

After installing and restarting Anki, the window title changes depending on
where you are:

| Screen | Default title (`title_content = "both"`) |
|--------|------------------------------------------|
| Deck browser | `Anki` (or `Profile – Anki` when >1 profile) |
| Deck overview | `Spanish – Anki` (deck name only — no card is selected yet) |
| Reviewing a card | `Spanish::Basics – España, 🇪🇸 – Anki` | 

The review title shows the **deck (incl. sub-deck)** and the **tags of the
note** behind the reviewed card (tags belong to notes, not cards).

## Changing what is shown

1. **Tools → Add-ons** → select *Deck Name & Tags in Title*.
2. Click **Config**.
3. Choose **Title content**:
   - **Deck name and tags** — default.
   - **Deck name only** — classic behaviour, no tags.
   - **Current card tags only** — tags replace the deck name.
   - **Nothing (just program name)** — remove the extra info.
4. Optionally tweak the separators, the tag limit, sub-deck handling and
   program name.
5. Click **Save**. The title updates immediately — no restart needed.

## Notes

- **Tags only appear while reviewing.** The deck browser and the overview
  have no "current card", so tags are never shown there.
- `max_tags` truncates long tag lists so the title stays short. Set it to
  `0` to show every tag.
- Internal markers (`marked`, `suspended`, `leech`) are filtered out and are
  never shown.
- With `show_subdeck` enabled, reviewing a card in a sub-deck shows the full
  path, e.g. `Spanish::Basics` in place of just `Spanish`.

## Debugging with the Logs tab

The settings dialog has a **Logs** tab for live debugging:

1. **Tools → Add-ons** → *Deck Name & Tags in Title* → **Config** → **Logs**.
2. Pick a **Minimum level** (DEBUG shows everything) and watch entries stream
   in — the view auto-refreshes while the dialog is open.
3. Use **Refresh** to re-read, **Copy** to put the visible log on the
   clipboard, **Clear** to wipe the in-memory buffer, and **Open log file…**
   to open the rotating file
   (`user_files/deck_name_and_tags_in_title.log`).

Each title change is logged (deck, sub-deck, tags, mode and the final title),
which makes it easy to trace why the title looks the way it does.