# Glossary - Solid Runner

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Name-san). Name order: Western (given name first).
- Romanisation source: official English names, else an earlier fan patch, else Hepburn without macrons.
- Credits: English.
- Register / flavour: near-future noir with a light, wisecracking touch; plain modern American English, contractions
  in speech. Sound effects: English comic-style words, capital first ("Kaboom!", "Crack!") (D9).
- Abbreviations: full names and terms everywhere; prefer engine changes over shortening (flag any abbreviation).
- Speech layout (D10): `Name「` -> `Name: text` (no quotes); box starting `「` -> `"text"` closed in the box; no
  bracket -> plain text. Player full name `{c0C:01}＝{c0C:00}` -> `{c0C:01} {c0C:00}`.
- Name buffers (D11): Erskine (7) and Grandil (7) are longer than the 5/6-letter name buffers; phase 7 widens them.

## Style rules
- Punctuation map: 「」 -> see speech layout, 『』 -> '...', ・・・/… -> ..., ！？ -> ?!, 〜 -> drop or stretch a letter,
  censored ✕ -> `*`.
- Voices and approved examples: `docs/style-reference.md`. Plot and who is who: `docs/synopsis.md`.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|

## Decisions from earlier batches
- <batch> <JP> -> <EN> (reason)
