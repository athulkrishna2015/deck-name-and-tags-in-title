# Usage

## What you see

After installing and restarting Anki, the window title changes depending on
where you are:

| Screen | Default title (`title_content = "both"`) |
|--------|------------------------------------------|
| Deck browser | `Anki` (or `Profile – Anki` when >1 profile) |
| Deck overview | `Spanish – Anki` (deck name only — no card is selected yet) |
| Reviewing a card | `Spanish::Basics – España, 🇪🇸 – Anki` | 

The review title shows the **deck (incl. sub-deck)** and the **current
card's tags**.

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