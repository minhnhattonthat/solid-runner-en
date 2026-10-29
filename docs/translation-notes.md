# Wave 1 report notes (controller)

## Phase 7 items
- Layout spaces: JP indents choices with 2 code-01 blanks (12 px each in JP; 4 px in the VWF) for the cursor, and
  pads columns with runs of blanks (elevator ev_97F109.., ev_9EB3BF, ev_9EB404; turbo Yes/No 92AEBC 92AF8A 92B027
  92B048 92B068 92B0AF; places_*/turbo_* centred by leading blanks). Translators dropped them. Phase 7: re-add the
  JP's leading indent per line as a 12 px blank, and a pad-to-x code for columns.
- Garbage / data decoded as text: ev_91940D (leading ソあラえンパブあゅすあ / ぬ), ev_92DE77 (whole entry; EN "..."),
  loose_93EED3 (選A000じゃ), turbo_929F06 (leading 選), places2_93C015 (leading H), ev_96DB26, ev_96DBF8 (EN "-"),
  ev_979F08 (garbage prefix), ev_A8D233 (EN "..."). Check in game / exclude.
- Split heads (extractor blind spot: a fake op inside a string; the head bytes are uncovered and stay JP): heads scan
  (scratch heads.py, prose filter) hits ev_93827B (head 店のオヤジ「まったく、ババリア…), ev_959A59 (「聞いて下さい！彼女が
  結婚にO…), ev_959C40 (「私、幸せです。彼の幸せ…), ev_97BA44 (news headline …ヒドロエピアン…いてっ、舌かんだ…より老化症状
  を抑える薬品の開発), ev_A8C91E (トーマス「おいおい、そこ…). Phase 7: start these entries at the real string start;
  EN already covers the full string for 959A59/959C40. The other three keep a tail-only EN (codes must match the
  current JP) until phase 7 moves the start; then use: ev_93827B "Shopkeeper: Honestly, thanks to Bavaria, business
  has been getting tough for me too. ...Whoops, keep that between us, okay?"; ev_97BA44 = ev_A8F2D3's EN (same
  string); ev_A8C91E "Thomas: Hey, hey, don't go touching the stuff in there without asking."
- Elevator/keypad columns: ev_979A81, ev_A8ECF2/A8ED43/A8ED90/A8EDE2, ev_A9EF83.
- ev_93827B starts mid-sentence (で): clause inserted elsewhere? ev_93EBC9 address printed after the text?
- LONG (engine): labels_82AB25/2A/2F/34 slot labels 36 px; missions_9296FB title 120 px; places2_93C169 Erskine,
  places2_93C20B Grandil (name buffers).

## Terms to merge
b013-016: ダイオウインコ emperor parrot; バイスハイト様 Lord Weissheit; 通路転送プログラム passage transfer program;
3枚目 clown; map labels (Night Club Dilcore, Raoel's Hideout, Tunnel to Ural Factory, Residential Area, SCBC
Station, Warehouse District 1/2, Bavaria Hideout); floors NF / BNF, Next Page / Previous Page, Now on {c04}F.
b032-035: 地下道 Tunnel; アニル社 Anil; 技術者専用キー Engineer Key; 非常階段のキー Fire Escape Key; 廃墟 Ruins; SCBC局
SCBC Station; ババリアのアジト Bavaria Hideout; テロ集団アジト Terrorist Hideout; 依頼内容 Request; 依頼人 Client;
ジョブス社 Jobs.
b001-004: 店のオヤジ Shopkeeper; バーテン Bartender; 選手 Fighter; 声 Voice; 男 Man; ストーカー Stalker; Beginner /
Normal / Expert Class; 準優勝 runner-up; machine (katakana) speech = ALL CAPS clipped.
b009-012: ランドエア政策 Land-Air policy; 生体建材 living building materials; バイオマテリアル biomaterial;
技術者専用キー Technician Key (CONFLICT: b032-035 Engineer Key); コスタ部長 Chief Costa; 黒ピラニア病 black piranha
disease; speakers 受付嬢 Receptionist, 店長 Manager, 警備員 Guard, 記者 Reporter, アシスタント Assistant, プロデューサー
Producer, 女優 Actress, 新人女優 Rookie Actress, タレント Celebrity, 女性 Woman; ブン屋 newshound.
CONFLICT: machine speech b001-004 ALL CAPS vs b032-035 Title Case (loose_90DD15...).
b021-024: 秘書 Secretary; ドラッグのバイヤー Drug Dealer; ヨッパライ Drunk; 工場長 Plant Manager; 作業員 Worker;
ホログラムシート hologram sheet; IDカード ID card; サブ電源 sub-power; 警告レベル4 Alert Level 4; ボーマンさん Bowman-san.
