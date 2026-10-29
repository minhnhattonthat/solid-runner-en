# Translation reviewer brief - Solid Runner

You review one batch of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width) is already enforced by the check tool - judge
translation quality. Return the report as your final message: subagents cannot write files, so the controller saves
it.

## Inputs (paths in your dispatch)
- Pairs file `work/tl/<batch>.pairs.txt`: every entry as `>> id | speaker | JP` / `   EN`, in script order (so the
  neighbours are your context). Read ALL of it, in passes if large.
- `glossary.md` (rulings at the top), `docs/style-reference.md` (speech layout, voices), `docs/synopsis.md`.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Speech layout: `Name「` -> `Name: text`; box starting `「` -> `"text"`; no bracket -> plain. A name added where the
  JP shows none, or quotes on a named line, is Important.
- Consistency: glossary names/terms exactly (a one-letter slip is what players notice); honorifics kept where the JP
  has them; voice matches the style reference and the synopsis.
- Things players caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a variable
  ("1th"); abbreviated names or terms; stock phrases that read awkwardly in English ("... GET!"); a spoiler given
  away earlier than the JP does.
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, speech-layout error)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
