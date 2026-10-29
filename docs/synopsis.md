# Solid Runner - story synopsis for translators

Reconstructed from `work/tl/script_dump.txt` (all 4080 lines). Event ids (`ev_BBxxxx`) are cited so you can find your
place. Banks are not in story order. Only one episode header survives in the dump: 第4部エピソード「破壊・誕生」
(Part 4, "Destruction / Birth", ev_A8A99B); the Part 1-3 boundaries below are my best guess.
**SPOILER** marks facts the player learns later than the scene they belong to: do not hint at them early.
Name proposals: `work/tl/terms_proposed.tsv`. Honorifics stay (`{name}-san`), Western name order (docs/decisions.md D1).

## Setting
- 21XX. Orbiselus (オルビセルス), a prosperous South American country. Solid City (ソリッドシティ): a lawless "free
  city" of 13 numbered Areas; the city's lifelines (power, water, traffic, records, reactor) are run by the main
  computer at CTI HQ (ev_97C1B7). Brazilian flavour everywhere: caipirinha, guarana, churrasco, Copacabana, Amazon.
- Intro crawl (intro_928F1F..929023): runaway robots, bio-monsters, mafia, virtual drugs, terrorists; the hero's
  trade is "Cyber Detective" (電脳探偵).
- Runners (ランナー): piloted mechs, 4 weapon mounts (L/R shoulder, L/R arm). A Navi-Robo (ナビロボ) links pilot and
  runner and talks in battle. Detectives take jobs from the home terminal (Request / News / Information / Data Library).
- Bio-monsters: products of illegal bio-research. Piranha Preta (ピラーニャ・プレタ, "black piranha disease"): an
  incurable, non-contagious disease that rots the muscles; it drives much of the plot.

## Cast (speech notes are for register; JP pronoun in brackets)
- **Shu Erskine** ({c0C:01} {c0C:00}, default シュウ アースキン): hero, 24. Foundling raised at Sister Rachel's convent
  until 15, army runner pilot 18-23, left after a war incident in which his unit killed a child. Now a detective living
  above Riff's garage. [オレ, sometimes 俺] Casual, wisecracking, skirt-chaser, money-minded on the surface, soft
  inside; hot-headed whenever Bavaria is mentioned. Calls Costa "old man/オッサン", Gloria "オバサン"/"局長さん",
  Rachel "Sister" (behind her back "the old bag" 婆さん/ババア). His runner: {c0C:02} (default Grandil).
- **Irene** (アイリーン): Shu's fiancee, 22, Tao's only daughter. Warm, teasing, feminine; "Papa". Dies early (Part 1)
  but haunts the whole story (dreams, a vision that stops Shu killing Raoel, ev_A9B561).
- **Tao** (タオ): boss of Anryu (暗龍), the Chinatown "Chinese mafia" (his men insist it is more a business
  association, ev_958ED3). Proud, old-fashioned [わし]; deferential to Sister Rachel. Killed with Irene.
- **Sister Rachel** (シスターレイチェル; nuns say レイチェル院長): head of the convent in Area 2, 41. Raised Shu and Nora.
  Very polite [わたくし], pious, and expert at guilt-tripping Shu with embarrassing childhood stories.
- **Riff** (リフ): runner mechanic, 55, owns garages at the Junkyard (Area 1). Gruff, fatherly, crude jokes
  [わし/ワシ]. Tunes runners, runs Justice entries, later joins the Resistance. Teases Ion about eating too much.
- **Kirk** (カーク): Navi-Robo Riff found on a scrapheap and gives Shu after Irene's death. Speaks like a pompous old
  English gentleman [ワシ, ～じゃ, ～おる, ～のう]; demands afternoon tea and premium oil; calls Shu
  "greenhorn" (ヒヨッコ), "fool". Bickering partners who become true friends. Insists he is "special".
- **The old Navi-Robo** (Part 1 only, plain "ナビロボ"): cheap, glitchy; talks in katakana robot-speak (ピッピッピ,
  ～デス). Battle-line pairs in bank 90 have one Kirk-style line and one katakana robot line each.
- **Ion** (イオン): female detective, 18, psycho-dive (cyberspace) specialist, pilots Brigantia. Tomboyish, bossy,
  quick to slap Shu, secretly kind [あたし, ～わ/～のよ]. Gets jealous around Anna.
- **Minerva** (ミネルバ): Ion's Navi-Robo with a female personality imprint. Very polite, "{name}-san".
- **Costa** (コスタ): CTI Security Division chief, 44. Fat, cowardly, arrogant to inferiors, stutters when angry
  [私, 貴様/キサマ]. Bavaria makes him puppet director; he ends up clinging to his chair, mad (ev_94B48A).
- **Theo** (テオ): CTI security officer, 26, Shu's liaison. Polite, dry, mocks Costa; loyal to Gloria but appalled
  when she orders Shu killed. (Profile: he is gay, database_87EAE0.)
- **Gloria** (グロリア): director of CTI's Integrated Management Bureau, 40. Cold, efficient, commanding (plain
  masculine forms mixed with ～わ). SPOILER: lost her child to Piranha Preta; wants Bavaria's research at any price.
- **Raoel** (ラオエル): golden-maned, lion-like, highly intelligent bio-monster leading a "terrorist" band of
  bio-monsters. Grave, proud [おれ], distrusts humans, warms to Shu. SPOILER: born in a Bavaria lab from Weissheit's
  sperm and an ape egg, called a "failure"; the scientist who raised him died getting him out (ev_A9BEAD..A9C084).
- **Weissheit** (バイスハイト): Bavaria's boss; his name is a reveal (ev_93E944). Grandiose, archaic villain speech
  [私; 貴様, 虫ケラ "insect", 若造, 小娘, ～ぬ]. SPOILER: test-tube son of a 20th-century European dictator who sought
  immortality and was executed; breeds an "elite" by artificial insemination; has Piranha Preta himself
  (ev_A5EE98..A5F05F). Final form "Neo Weissheit" talks in katakana machine-speak.
- **Barnes** (バーンズ): Shu's army buddy. Friendly, cynical [おれ]. SPOILER: works for Bavaria; uses Shu, then
  tries to kill him (ev_919153).
- **Garcia** (ガルシア): Bavaria hitman, ex-mercenary, Justice entrant. Brutal, boastful. Killed Tao and Irene.
- **Harold** (ハロルド, 大佐 Colonel): Weissheit's right hand, military arrogance; his attack kills Thomas.
- **Lecter** (レクター): Bivisible gang member, 26, black, flippant slang [おれ, ～ぜ]; pilots Nobleness.
- **Brundle** (ブランドル): Bivisible boss, 45, stiff and formal [私]; pilots Phantom.
  SPOILER (both): Bivisible is CTI's secret action unit, created by Gloria (ev_ADDE4D).
- **Thomas** (トーマス): reclusive ex-British-army runner scientist, Daemon's designer, once worked with Kirk's
  old master "the General" (将軍).
- **Anna Kelly** (アンナ＝ケリー): top singer, 21, Irene's double. Sweet, polite; adored detectives since childhood.
- Others: Nora (ノーラ, convent girl, Catala Company clerk), Remin (レミン, little girl, Piranha Preta, "onii-chan"),
  Sharon and David Crane, Sherry Milan (singer) and her manager Hans, Rodriguez (Anna's manager), Santos (SCBC
  reporter), Valdez (informant), Bowman (Fantasy Dome owner), Santana (Justice announcer), Daemon's pilot.

## Organisations and recurring places
- **Bavaria** (ババリア): German-born crime syndicate (drugs, smuggled military runners), moving into Solid City and
  building secret bio-labs; its runners use unique parts (Riff's clue, ev_ADB233).
- **Anryu** (暗龍): Tao's organisation; wiped out by Bavaria. **Bivisible** (バイビジブル): rival gang to Bavaria.
- **CTI**: the city/state administration (quiz glosses it 中央科学局, ev_9EFBC6); Security Division (Costa),
  Integrated Management Bureau (Gloria). **SCBC**: TV station in Area 7. **Catala Company**: shady real-estate firm.
- **Resistance** (レジスタンス): humans and bio-monsters fighting Weissheit in Part 4.
- Places: Junkyard (Riff's garage/Shu's home), convent (Area 2), Chinatown, EL'S Cafe, Dilcore night club, VR Game
  Center (Area 7), VR Host Center and Millennium Hall (Area 10), Natural Park and Alex Hospital (Area 6), Fantasy
  Dome (Area 5), Ural Factory and slums (Area 3), abandoned building (Area 8), Warehouse District (Area 11), Justice
  Dome and Parts Shop (Area 13), CTI HQ (Area 9; "Former CTI HQ" in Part 4).

## Story

### Prologue (dream)
Shu's recurring nightmare of the war: his unit is surrounded; a village child brings them food in thanks; a panicking
rookie fires; the child dies (ev_ADBB8F..ADBFF7). Irene wakes him: "It wasn't your fault" (ev_ADC832..ADC947).

### Part 1 (guess): engaged life, first cases
- Shu and Irene live above Riff's garage; Riff nags Shu to replace his glitchy Navi-Robo, suggests a test run at the
  Area 11 warehouses (ev_AD9477, ev_AD9FD3..ADA518). Irene's banter, wedding talk, slack days (ev_ADA881..ADAE06).
- Visit to Tao: he wants a huge Chinatown wedding; Sister Rachel shames everyone into a small one at her convent;
  Tao mentions Bavaria moving in (ev_958480..958A23).
- **Job: Mother and Daughter.** Rachel asks Shu to deliver a parcel to Nora (ev_87BE32, ev_9EE172). Nora's flat is
  ransacked, ransom note (ev_9684CA..968714). The parcel holds a disc: Catala Company is illegally handing the convent's
  land to Bavaria (ev_87B667). Exchange at Warehouse 2; Shu rescues Nora by runner and beats Catala's president
  (ev_96A042..96A3B9). Nora calls Rachel "Mother" (ev_9EE90F).
- **Job: A Girl's Dream.** At the VR Game Center Shu meets Ion and Minerva (ev_96C684..96CA89). Remin is trapped in
  cyberspace by a bio-monster in the VR Host Center; Shu weakens it without killing it, Ion salvages Remin
  (ev_96DECD..96E987, ev_96CAE1..96CE5D). The monster spoke: it shared Remin's suffering (Piranha Preta).
- **Job: Hunting.** Costa (phone, ev_87C09C) hires Shu to clear the Area 3 sewers; Theo briefs him; boss Lizauga;
  a mysterious half-human figure escapes (ev_96F3F9..96F986).
- **Massacre.** Tao's call for help (ev_87C010); Anryu HQ in flames, Tao dies asking Shu to save Irene, she dies
  under the collapsed ceiling - the night before the wedding (ev_9592C3..95960B).

### Part 2 (guess): revenge begins
- "A month after the day of the nightmare" (ev_AD9A7E). Shu drinks; Riff shows runner parts from the massacre that
  only Bavaria uses, and introduces Kirk (ev_ADB0ED..ADB8C9). Kirk wants tea: EL'S Cafe (no tea, ev_95A463).
- **Job: Hurricane.** At the cafe Barnes offers a 6000G bounty on an escaped bio-monster addicted to the virtual drug
  Hurricane (ev_95A60E..95AB52). Dilcore club; Lecter (unnamed at first) sells the tip: Area 8 abandoned building
  (ev_94A66B..94A818). The monster is a former human with Piranha Preta, drugged and mutated by Bavaria; Raoel
  appears and takes him in (ev_95D63E..95DBC6). **SPOILER:** Barnes is Bavaria, wanted the escaped subject, mocks
  Shu's guilt over the child; Shu kills him (ev_919153..919337); Shu apologises to Kirk (ev_919365).
- **Job: Declaration of War.** Shu decides to hit Bavaria (ev_ADC9FA); Riff gives explosives (ev_ADA6AE); drug factory
  under the Area 11 warehouses is blown up; Raoel watches: "you hate Bavaria too?" (ev_96AFD3..96B76A).
- **Job: The Man Who Never Came Home.** Sharon Crane's husband David vanished at the closed Ural Factory
  (ev_95BD9D..95C247). Under it: a Bavaria lab using workers as test subjects; password 3102; David, mutated, begs to
  die; Shu delivers his pendant and tells Sharon to leave town (ev_A9E3F5..A9FBFE, ev_95C319..95C754).
- **Job: Golden Mane.** Bowman's Fantasy Dome: 20 Firedrakes, then a hacked computer; Raoel was behind it, scouting
  for intelligent recruits (ev_A98E8A..A99F2B).
- **Job: The Failure.** Costa orders Shu to hunt the "rebels" (ev_87C1F6..87C3AA); Theo briefs (ev_ADCD61..ADD2E7);
  Santos at SCBC makes Shu tell stories (ev_979118..979736); Valdez's quiz, hideout under the Area 3 slums
  (ev_9EF9CC..9EFF12). Shu beats Raoel but Irene's vision stops the killing blow (ev_A9B33A..A9BABA). Raoel tells his
  origin (SPOILER, above). Shu quits Costa's job (ev_87C57B..87C67C), then takes a day off (ev_94A113).
- **Job: Piranha Preta.** Theo brings Shu to Gloria (ev_9EF895, ev_97C1B7..97C8D2); Alex Hospital hides a Bavaria lab
  experimenting on Piranha Preta patients (ev_97EAAD..97EFE7). **SPOILER:** Gloria and Brundle discuss Shu as their
  "pawn" (ev_97CD73); Gloria's dead child (ev_97CC01).

### Part 3 (guess): Daemon, Anna, Justice, Weissheit
- **Job: Daemon.** Ion recruits a partner to kill the rogue runner Daemon (ev_95ABCE..95AE5C, ev_ADE704..). Ion
  hints at her own hatred of Bavaria. Daemon wrecks Brigantia; Shu fights Daemon, whose pilot is overwhelmed by the
  machine (ev_ADF3D0, ev_918D32). Shu keeps Daemon's unit; hospital banter and prize-split choice (ev_ADF668..ADF9FA).
- Riff rebuilds the runner with Daemon's unit (200G) and suggests Justice for money (ev_ADD384..ADD900).
- **Job: The Idol's Idol.** Ion's bodyguard job for Anna Kelly at SCBC; Shu is stunned by her likeness to Irene
  (ev_97A007..97B0A3). At the Millennium Hall concert she is snatched during her ballad; Shu chases the "stalker" into
  the slums (ev_9EC89C..9ED0FD, ev_A9D4C8..A9D876). Sherry's manager Hans hired him; Ion flattens Hans
  (ev_9ED3C1..9ED975). Anna confesses she loves Shu (ev_97B6A2..97B7FA).
- **Job: Justice.** At the Justice Dome Shu meets Lecter, learns Garcia killed Tao and Irene (ev_9494C0..949810,
  ev_949178..94922B); Riff enters him in Normal Class (ev_948D48..948F05). Bouts vs Lecter and Garcia; Riff stops Shu
  killing Garcia (ev_919EF5..91A677).
- **Job: Psycho Dive.** At the hospital Ion dives into Garcia's brain; the boss's name is "Weissheit" (ev_949AC6..
  949EEA, loose_93E944); Ion freezes ("he killed my mama and papa"). Theo takes Garcia into CTI custody (choice
  ev_949FF8). Info menu on Garcia / Anryu / Bavaria (ev_93E466..93E8A9).
- **Job: The Enemy Before Me.** Bavaria hideout in Area 2 (ev_9EBEEC). Ion and Raoel turn up; **SPOILER** Ion's past:
  Weissheit ordered her scientist mother's egg fertilised with his sperm; her mother's lover swapped in his own; Weissheit
  killed him; Dr Carlo Kitty raised her (ev_9EA0E1..9EA2BC, ev_9EAA85..9EACAD). Weissheit flees; Garcia, sprung from
  CTI, dies fighting Shu (ev_9EAD9E..9EB2AC).
- **Takeover.** Bavaria hacks the CTI main computer (ev_97CFFA..97D19B); Costa takes Gloria's chair as Weissheit's
  puppet (ev_97D576..97D773). Ion is kidnapped (ev_87C3F3, ev_968F26..9694F3); Shu and Kirk psycho-dive to trace her
  signals to Area 12 (ev_93EB13.., ev_969320). Gloria, Brundle, Lecter and Theo reveal Bivisible (ev_ADDCEF..ADE0FF).
- **Job: Psycho Dive / rescue.** Area 12 hideout with Brundle and Lecter (ev_A59E85..). Kirk asks whether Shu loves
  Ion (choice, ev_A59F7C..A5A148). Ion rescued; Weissheit appears, insults Ion as "defective" (ev_A5A4E8..A5A743).
  **SPOILER:** CTI shells the building to bury everyone who knows too much (ev_A5A7BE..A5A920); Shu's runner is
  crippled and Weissheit gloats (ev_A5AA0E). Raoel drags him out.

### Part 4 "Destruction / Birth" (ev_A8A99B)
- Shu lies in a coma for half a year under Riff's Junkyard (the Resistance base). Ion nurses him; Raoel confesses his
  love to Ion (ev_A88C33..A892F3, confession ev_A8917B). Shu wakes calling for Irene (ev_A89333..A896EC).
- Weissheit rules openly, cutting lifelines to anyone who resists (ev_A89BDA..A89C9C). Gloria and Brundle come to
  apologise and ally; trust choice (ev_A8A4BD..A8A826).
- **Job: Devil's Power.** Shu seeks Daemon's designer Thomas in Area 8 (ev_A885B6, ev_A8B009). Kirk speaks in the
  dead General's voice; Kirk, Thomas and the General built a next-gen army runner that syncs pilot and machine and can
  absorb the pilot (ev_A8B169..A8B7DA, ev_A8BA87..A8C24E). Thomas rebuilds Shu's runner, starts to say something about
  Kirk, and is killed in Colonel Harold's attack (ev_A8C2A2..A8C803).
- Final assault: Raoel and Ion attack on the surface; Shu, Brundle and Lecter enter the Former CTI HQ via the sewers
  (ev_A89D73..A89FF8, ev_A8D713..A8D992). Labs on Piranha Preta, immortality and frozen embryos (ev_A8F16A..A8F3C4,
  ev_94B69D); Costa raving in his office (ev_94B48A..94B65A). Raoel holds 1F with Riff (ev_A5ECF5).
  Possibly branch-dependent: Brundle tries to make Shu "die with Bavaria" and explains Gloria's motive; Shu fights
  Lecter (Nobleness) and Brundle (Phantom), who dies (ev_A5E9E2..A5EBDD, ev_9194A8..9195DB).
- Weissheit, sick with Piranha Preta, raves about immortality and his father (ev_A5EE2E..A5F171), overloads his sync
  and becomes Neo Weissheit (ev_A5F271..A5F465). Ion and Raoel cut his energy feed (ev_9197CF, loose_9198D4).
- **SPOILER:** Shu loses control to the system; in a dreamscape Kirk reveals the General built a "substitute" into
  him: Kirk merges with the runner in Shu's place and says goodbye (ev_919992..919AA9, ev_93F03F..93F451). The runner
  powers up; Weissheit is destroyed (ev_919BB6..919C78).

### Endings (choice-dependent; which choices decide is not visible in the text)
- Shu destroys the main computer rather than let any system rule people; Gloria wanted it for the Piranha Preta cure
  (ev_92B419..92BA18).
- A: Raoel leaves town; Shu confesses to Ion and she accepts (ev_92BDC6..92C31C).
- B: Raoel leaves, telling Ion that Shu needs her (ev_92C4E6..92C5F7).
- C: Ion and Raoel leave together; Shu jokes about their "love child" (ev_92C726..92CA06).
- D: Shu still mourns Irene; Raoel and Ion become a couple (ev_92CADE..92CCC8).
- Epilogue: Shu still on the job, Kirk now speaking in katakana robot voice from inside the runner, Ion "eats too
  much", date tonight (ev_92CD80..92CEC3).

## Relationship arcs (watch your register)
- Shu-Kirk: insults and pet names ("greenhorn") -> "partner" -> "best friend"; Kirk's farewell is the emotional peak.
- Shu-Ion: rivals who snipe and slap -> comrades -> love (or not, depending on ending). Ion uses "あなた" to Shu when
  serious, his name otherwise.
- Shu-Raoel: hunter and target -> mutual respect -> friends; Raoel calls Shu by name, plainly.
- Shu-CTI: Costa (mutual contempt), Theo (friendly), Gloria (uneasy ally -> traitor -> ally of necessity).
- Shu-Rachel: grumbling obedience; she is the only person he cannot say no to.
