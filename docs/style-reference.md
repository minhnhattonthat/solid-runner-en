# Style reference - Solid Runner

Tone: near-future noir with a light, wisecracking touch (think 90s anime OVA dub at its best, not a parody). Plain
modern American English; contractions everywhere in speech; no archaisms except where a character's voice calls for
it (Sister Rachel is formal, Tao is an old-school boss). Narration and system text: short, neutral, clear.

## Speech layout (every box)

| Japanese | English | Example |
|---|---|---|
| `Name「text` (speaker named) | `Name: text` - no quotes | `Tao: Seems something big is moving in the underworld.` |
| `{c0C:01}「text` (the player) | `{c0C:01}: text` | `{c0C:01}: Like I keep saying...` |
| `「text` (new speaker, name not shown) | `"text"` - quotes closed in the same box | `"Papa!"` |
| no bracket (same speaker continues, or narration) | plain text, no quotes | `I'm marrying Irene because I love her.` |
| `『term』` | `'term'` only when it is a quoted title or a name being introduced; otherwise drop | `your organisation, the 'Dark Dragon'` |

## Voices

| Character | JP voice | English voice |
|---|---|---|
| Shu ({c0C:01}, player, ore) | casual, blunt, a bit cocky, soft spot for Irene and the Sister | short sentences, slang-light ("Forget it", "C'mon"), never crude without a JP reason |
| Irene (Tao's daughter, fiancee) | warm, feminine (〜わ, 〜よ), calls Tao パパ | "Papa"; affectionate, direct |
| Tao (mob boss, washi) | old gruff boss (わし, 〜じゃ, 〜おる) | gruff, slightly old-fashioned ("I won't hear of it", "Hmph"), no fake dialect |
| Sister Rachel (nun, watakushi) | refined, polite (〜ですわ, 〜なさい) | gentle, formal, teasing; calls Shu by full name when scolding |
| Kirk, Riff, others | see docs/synopsis.md | match the synopsis' notes |
| Shopkeepers, receptionists | polite service speech | courteous, brief |

## Approved pairs (the pilot; match this voice)

| id | JP | EN |
|---|---|---|
| ev_958480 | タオ「どうやら、裏の世界で / 大きな動きがあるようだな。 / お前達の結婚式が近いというのに…。 | Tao: Seems something big is stirring in the underworld. And with your wedding so close, too... |
| ev_9584CA | タオ「…とにかくだ。 / アイリーンは、わしの一人娘。 / 他に龍の血と符丁をつぐ者はおらん。 | Tao: ...Anyway. Irene is my only daughter. No one else carries on the Dragon's blood and its signs. |
| ev_958501 | その娘に むこどのを迎えるのだから / 式は組織をあげて盛大に行わねばな。 | She's taking a husband, so the whole organisation must throw a grand ceremony. |
| ev_95852F | {c0C:01}「何度も言うが、オレは / あんたらの組織『暗龍』と結婚するんじゃ / ないんだ。 | {c0C:01}: Like I keep telling you, I'm not marrying your organisation, the 'Dark Dragon.' |
| (next) | アイリーンを愛しているから、一緒に / なるんだ。ハデな式なんてゴメンだぜ。 | I'm marrying Irene because I love her. Spare me the flashy wedding. |
| (next) | アイリーン「パパ、 / 私も{c0C:01}と同じ気持ちよ。 / 私達の結婚に暗龍は関係ないわ。 | Irene: Papa, I feel the same as {c0C:01}. Our wedding has nothing to do with the Dark Dragon. |
| (next) | 「アイリーン おまえまで…！ | "Irene, not you too...!" |
| (next) | 「パパ！ | "Papa!" |
| (next) | 「{c0C:01}＝{c0C:00}、 / 思い出しますわね。 | "{c0C:01} {c0C:00}, do you remember?" |
| (next) | 「分かったってば！ / もう結婚式だろ〜が、仮装行列だろ〜が / 何でもやるってば！ | "Okay, okay! Wedding, costume parade, whatever - I'll do it all!" |
| (next) | 「ううむ…シスターは、わしにとっても / 恩のある方。仕方ないですな、その通りに / するとしましょう。 | "Hmm... I owe the Sister a great deal myself. Very well, we'll do as you say." |

Corrected example (a first draft that was wrong, and why):
- `「アイリーン おまえまで…！` first drafted as `Tao: Irene, even you...!` - wrong: the JP names no speaker in this box,
  so the English doesn't either (`"Irene, not you too...!"`); the reader knows from context.
- `{c0C:01}＝{c0C:00}` is the player's full name: given name, a space, family name (Western order). Never write the ＝.
