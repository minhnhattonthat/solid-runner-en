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

Tables are enforced by `tools/batches.py check`: when the JP term appears (whole katakana run, or the kanji
compound), its EN must appear in the line. Words that vary with context are under "Common words" (guidance only).

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| シュウ | Shu | | player's default given name ({c0C:01}) | Shuu, Syu |
| アースキン | Erskine | | player's default family name ({c0C:00}) | |
| グランディル | Grandil | | player's runner, default name ({c0C:02}) | Grandeal |
| アイリーン | Irene | | Tao's daughter, Shu's fiancee | Eileen, Aileen |
| タオ | Tao | | head of the Dark Dragon | |
| シスターレイチェル | Sister Rachel | | nun who raised Shu | |
| レイチェル院長 | Mother Superior Rachel | | | |
| レイチェル | Rachel | | | |
| カーク | Kirk | | | |
| イオン | Ion | | | |
| リフ | Riff | | mechanic | Rif, Lif |
| ミネルバ | Minerva | | | |
| コスタ | Costa | | CTI security chief | |
| テオ | Theo | | | Teo |
| グロリア | Gloria | | | |
| ラオエル | Raoel | | | Raoul |
| バイスハイト | Weissheit | | Bavaria boss | Weisheit, Vaisheit |
| ネオバイスハイト | Neo Weissheit | | | |
| バーンズ | Barnes | | | |
| アンナ＝ケリー | Anna Kelly | | | |
| アンナ | Anna | | | |
| ハロルド | Harold | | | |
| レクター | Lecter | | | Rector |
| ブランドル | Brundle | | | Brandle |
| ガルシア | Garcia | | | |
| トーマス | Thomas | | | |
| サンタナ | Santana | | | |
| サントス | Santos | | reporter | |
| ノーラ | Nora | | | |
| レミン | Remin | | | |
| シェリー＝ミラン | Sherry Milan | | | |
| シェリー | Sherry | | | Shelly |
| ハンス | Hans | | | |
| ロドリゲス | Rodriguez | | | |
| ロイ＝エンゾ | Roy Enzo | | | |
| アサド＝メンドーサ | Asad Mendoza | | | |
| シャロン＝クレイン | Sharon Crane | | | |
| シャロン | Sharon | | | |
| デビッド＝クレイン | David Crane | | | |
| デビッド | David | | | |
| バルデス | Valdez | | | |
| ボーマン | Bowman | | | |
| カルロ＝キティ | Carlo Kitty | | | |
| ダ・シルヴァ | Da Silva | | | |
| エビータ | Evita | | | |
| ドミンゴ | Domingo | | | |
| クスリ屋のサムソン | Samson | | "Samson the Pusher" | |
| 早耳のトム | Tom | | "Tom the Ear" | |
| ミサンガ売りのアドン | Adon | | "Adon the Bracelet Seller" | |
| チクリ屋ブラウン | Brown | | "Brown the Snitch" | |
| 一ッ目のスネイク | Snake | | "One-Eye Snake" | |
| 不死身のジョン | John | | "Deathless John" | |
| ハイエナ | Hyena | | | |
| カルロス | Carlos | | | |
| クビチェック | Kubitschek | | | |
| ポポス | Popos | | | |
| ナビロボ | Navi-Robo | | | Navirobo, NaviRobo |

## Places and organisations
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ソリッドシティ | Solid City | | | |
| オルビセルス | Orbiselus | | the country | Orbiseles |
| アルタニア | Altania | | | |
| チャイナタウン | Chinatown | | | |
| ジャンクヤード | Junkyard | | | |
| 臨河住宅地区 | Riverside Residential District | | | |
| 工場地区 | Factory District | | | |
| 中央住宅地区 | Central Residential District | | | |
| 臨河アミューズメント地区 | Riverside Amusement District | | | |
| 自然保護地区 | Nature Reserve District | | | |
| 南アミューズメント地区 | South Amusement District | | | |
| バイオ研究施設地区 | Bio-Research Facility District | | | |
| 行政地区 | Administrative District | | | |
| 北アミューズメント地区 | North Amusement District | | | |
| 国際港地区 | International Port District | | | |
| 商業地区 | Commercial District | | | |
| 闘技場地区 | Arena District | | | |
| ファンタジードーム | Fantasy Dome | | | |
| ナチュラルパーク | Natural Park | | | |
| アレックス病院 | Alex Hospital | | | |
| VRゲームセンター | VR Game Center | | | |
| VRホストセンター | VR Host Center | | | |
| ホストセンター | Host Center | | | |
| ディルコア | Dilcore | | night club | |
| CTI本部 | CTI HQ | | | |
| ミレニアムホール | Millennium Hall | | | |
| ジャスティスドーム | Justice Dome | | | |
| ウラル工場 | Ural Factory | | | |
| ココ・ストリート | Coco Street | | | |
| コパカバーナ | Copacabana | | | |
| レブロン | Leblon | | | |
| サント・アントニオ | Santo Antonio | | | |
| ババリア | Bavaria | | German crime syndicate | Babaria |
| 暗龍 | Dark Dragon | | Tao's Chinatown syndicate | Anryu, Anlong |
| バイビジブル | Bivisible | | | |
| CTI | CTI | | | |
| 統合管理局 | Integrated Management Bureau | | | |
| 中央科学局 | Central Science Bureau | | | |
| カタラカンパニー | Catala Company | | | |
| レジスタンス | Resistance | | | |
| SCBC | SCBC | | TV station | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ランナー | runner | | the mechs; capitalise only at sentence start | Runner robot, mech |
| バイオモンスター | bio-monster | | | biomonster, Bio Monster |
| バイオランナー | bio-runner | | | |
| 電脳探偵 | Cyber Detective | | | |
| 電脳空間 | cyberspace | | | |
| サイコダイブ | Psycho Dive | | | Psychodive |
| ピラーニャ・プレタ | Piranha Preta | | Portuguese: black piranha | |
| ハリケイン | Hurricane | | | |
| ヴァーチャルドラッグ | virtual drug | | | |
| デイモン | Daemon | | rogue runner | Demon |
| ターボファイル | Turbo File | | | |
| リペアキット | Repair Kit | | tiers keep their letters: Repair Kit L / M / H / SP / X | |
| リカバーリキッド | Recover Liquid | | | |
| リフレッシャー | Refresher | | | |
| アルカリワックス | Alkali Wax | | | |
| キュアリキッド | Cure Liquid | | | |
| フレイムコート | Flame Coat | | | |
| スタンコート | Stun Coat | | | |
| アシッドコート | Acid Coat | | | |
| ポイズンコート | Poison Coat | | | |
| パワーアシスト | Power Assist | | | |
| EXアーマー | EX Armor | | | |
| ブースターキット | Booster Kit | | | |
| スナイパーキット | Sniper Kit | | | |
| ドッジシステム | Dodge System | | | |
| アタッカー | Attacker | | | |
| ディフェンサー | Defender | | | Defenser |
| クイックムーバ | Quick Mover | | | |
| マスターキー | Master Key | | | |
| カードキー | card key | | | |
| 耐火装甲 | Fireproof Armor | | | |
| 耐電装甲 | Insulated Armor | | | |
| 耐毒装甲 | Poisonproof Armor | | | |
| 耐酸装甲 | Acidproof Armor | | | |
| 回復装甲 | Recovery Armor | | | Regen Armor |
| オーバーブースト | Overboost | | | Over Boost |
| ウィリス | Willis | | weapon line | |
| レイヴン | Raven | | weapon line | |
| ニーメイヤ | Niemeyer | | weapon line | |
| ガーシュ | Gersh | | weapon line | |
| ギガイアス | Gigaias | | weapon line | |
| ゴーント | Gaunt | | weapon line | |
| レイジア | Reizia | | weapon line | |
| ベグルド | Begld | | weapon line | |
| ベレム | Belem | | weapon line | |
| トレント | Torrent | | weapon line | |
| ジョブズ | Jobs | | weapon line | |
| ブリガンティア | Brigantia | | runner | |
| ファイアドレイク | Firedrake | | runner | |
| ヌーヴェルバーグ | Nouvelle Vague | | runner | |
| ノウブルネス | Nobleness | | runner | |
| ファントム | Phantom | | runner | |
| リザウガ | Lizauga | | runner | |

Other runner names (runners list, once each): ラヴィアン Lavian, マッドキャット Mad Cat, エミネンス Eminence,
ミーティアリック Meteoric, ゲイル Gale, デフィート Defeat, ドーガン Dorgan, セイヂ Sage, クリムゾン Crimson,
ワイルドハート Wildheart, ガシップ Gossip, メルゴス Melgos, アマデウス Amadeus, グリープハンター Greep Hunter,
マッディドッグ Muddy Dog, ウォー・クライ War Cry, グレゴリー Gregory, アキューサ Accusa, ツイン・ヘッド Twin Head,
ネイバル Naval, ブーギー Boogie, ピースリザード Peace Lizard, ジェンス Gens, スケルター Skelter, CTICPU CTI CPU,
バーサティリティー Versatility. Weapons once each: スワロー Swallow, コンドル Condor, イーグル Eagle, ポルド Pold,
オーク Orc, ノーム Gnome, エルフ Elf, ライデン Raiden, ライジン Raijin, ライリュウ Rairyu, ライオウ Raio.
Missions: 母と娘 Mother and Daughter, 少女の夢 A Girl's Dream, ハンティング Hunting, 宣戦布告 Declaration of War,
失敗作 The Failure, 眼前の敵 The Enemy Before Me, 帰らなかった男 The Man Who Never Came Home, 黄金のたてがみ Golden
Mane, アイドルのアイドル The Idol's Idol. Episode 第4部「破壊・誕生」 Part 4: Destruction / Birth.

## Common words (guidance, not enforced)
- People/roles: 将軍 the General; 局長 Director; 保安部 Security Division; 保安部長 Security Chief; 院長 Mother
  Superior; 大佐 Colonel; ストーカー stalker; デイモンのパイロット Daemon's pilot; ヒヨッコ greenhorn; お嬢さん miss.
- Places: エリア N Area N; アジト hideout; 修道院 convent; 廃ビル abandoned building; 倉庫街 Warehouse District;
  2番倉庫 Warehouse No. 2; 旧CTI本部 old CTI HQ; スラム街 slums; 地下下水道 sewers; ドラッグ工場 drug factory;
  荒れ地ゾーン Wasteland Zone; 森林ゾーン Forest Zone; パーツショップ parts shop.
- Game: 依頼 request/job; 依頼人 client; 報告 report; 報酬 reward; 端末 terminal; リクエスト Request; ニュース News;
  インフォメーション Information; データライブラリー Data Library; タレコミ情報 tip-off; チューンアップ tune-up;
  改造 modification; 強化 upgrade; 装甲 armor; 辻ランナー rogue runner; ランナー使い runner pilot; G (money) G.
- Stats: 攻撃力 Attack; 防御力 Defense; 反応速度 Reaction Speed; 命中(率) Accuracy; 回避率 Evasion; 発射数 Shots;
  弾倉 Magazine; 経験値 EXP; 防御 (command) Guard. Parts slots: 左肩 Left Shoulder, 右肩 Right Shoulder, 左腕 Left
  Arm, 右腕 Right Arm (never L./R.).
- Weapon types: ライフル rifle, マシンガン machine gun, ショットガン shotgun, グレネードガン grenade gun, バズーカ
  bazooka, ミサイルポッド missile pod, ガンポッド gun pod, パイルバンカー pile bunker, アームスパイク arm spike,
  スタンナックル stun knuckle. Status: 火 fire, 電撃 shock, 毒 poison, 酸 acid, ナパーム napalm.

## Decisions from earlier batches
- (none yet)
