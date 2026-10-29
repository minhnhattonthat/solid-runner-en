-- Scene list for warp.lua (load it with --script before warp.lua). Each entry:
--   area, room   map to load instead of the new game's first map ($7E:1AA8 / $7E:1AA9; table A7:F000)
--   flags        {[0x70xxxx] = byte}: SRAM story flags/state written at the warp (room scripts test them, op 1C)
--   run          event-VM bytes injected over the first map's opening thread (95:84BC); needs area $01 room $00
--   keys         {{frames after warp, "x"}, ...}; mash = {key, every, from}
--   wait         {{addr, byte}, ...}: keys count from when these hold (mash stops then); warp.lua fails if never
--   god          pin HP to max (same as --var GOD=1)
--   frames       run length from power-on for run_scenes.py (the warp lands at ~f1560; default 2400)
-- Areas $16 (system: dives, title, name entry, save, shop) and $17 (intro, endings, credits) are listed by room;
-- story areas by their room 0 (more rooms: run_scenes.py --raw AA:RR). Area $00 is the battle arena (entered by
-- battle records, op 7D), $18 is code (87:8000), never a map.
local S = {}

-- Field control after the opening: mashing A through Tao's scene ends it ~3500 frames after the warp ($70:0013 -> 1,
-- $7E:1745 -> 0; the length varies run to run). Ending the thread at once (run = {0x00}, or its tail ops) leaves the
-- player without control, so the menu scenes mash through it and press their keys once the flags hold.
local function field(keys)
  local k = {}  -- no A after the opening: it talks to Tao again
  for _, v in ipairs(keys or {}) do k[#k + 1] = { v[1] + 120, v[2] } end
  return { area = 0x01, room = 0x00, mash = { "a", 30, 100 }, wait = { { 0x700013, 1 }, { 0x7E1745, 0 } },
    keys = k, frames = 6400 }
end
local function battle(lo, hi, bank, frames)
  return { area = 0x01, room = 0x00, run = { 0x7D, lo, hi, bank, 0x00 }, frames = frames or 2600 }
end

S.list = {
  -- boot and system screens (area $16)
  dive_1 = { area = 0x16, room = 0x00 },
  dive_2 = { area = 0x16, room = 0x01 },
  dive_3 = { area = 0x16, room = 0x02 },
  title = { area = 0x16, room = 0x03 },
  name_entry_a = { area = 0x16, room = 0x04 },
  name_entry = { area = 0x16, room = 0x05 },
  save_load = { area = 0x16, room = 0x06 },
  shop_greeting = { area = 0x16, room = 0x07 },
  shop_parts_view = { area = 0x16, room = 0x08 },
  shop_menu = { area = 0x16, room = 0x09, frames = 3000 },
  shop_buy = { area = 0x16, room = 0x09, keys = { { 1200, "a" } }, frames = 3000 },
  shop_sell = { area = 0x16, room = 0x09, keys = { { 1200, "down" }, { 1240, "a" } }, frames = 3000 },
  shop_buy_items = { area = 0x16, room = 0x09, keys = { { 1200, "a" }, { 1260, "a" } }, frames = 3100 },
  shop_buy_weapons = { area = 0x16, room = 0x09, keys = { { 1200, "a" }, { 1260, "down" }, { 1300, "a" } }, frames = 3100 },
  -- intro, endings, credits (area $17)
  staff_intro = { area = 0x17, room = 0x00 },
  ending_a = { area = 0x17, room = 0x01, frames = 3000 },
  ending_b = { area = 0x17, room = 0x02, frames = 3000 },
  cutscene_17_03 = { area = 0x17, room = 0x03 },
  cutscene_17_04 = { area = 0x17, room = 0x04 },
  cutscene_17_05 = { area = 0x17, room = 0x05 },
  turbofile_menu = { area = 0x17, room = 0x06 },
  results = { area = 0x17, room = 0x07 },
  credits = { area = 0x17, room = 0x08 },
  -- first map: the opening event, then the field menu and its submenus
  opening = { area = 0x01, room = 0x00 },
  opening_done = field(),
  -- every box of the opening, slowly (width tests: emu.py --shot-every 20)
  opening_talk = { area = 0x01, room = 0x00, mash = { "a", 50, 100 }, frames = 4000 },
  menu = field({ { 0, "x" } }),
  menu_item = field({ { 0, "x" }, { 100, "a" } }),
  menu_setup = field({ { 0, "x" }, { 60, "down" }, { 120, "a" } }),
  menu_info = field({ { 0, "x" }, { 60, "down" }, { 100, "down" }, { 160, "a" } }),
  menu_config = field({ { 0, "x" }, { 60, "down" }, { 100, "down" }, { 140, "down" }, { 200, "a" } }),
  -- scripted battles: op 7D records {id, formation, callback} found in the event banks
  battle_97DFE8 = battle(0xE8, 0xDF, 0x97),
  battle_9E87F3 = battle(0xF3, 0x87, 0x9E),
  battle_A587C0 = battle(0xC0, 0x87, 0xA5),
  battle_A5CDED = battle(0xED, 0xCD, 0xA5),
  battle_A5CDF0 = battle(0xF0, 0xCD, 0xA5),
  battle_A5CDF3 = battle(0xF3, 0xCD, 0xA5),
  battle_A5CDF6 = battle(0xF6, 0xCD, 0xA5),
  battle_A8AE90 = battle(0x90, 0xAE, 0xA8),
  battle_A8AE93 = battle(0x93, 0xAE, 0xA8),
  battle_A9A6D7 = battle(0xD7, 0xA6, 0xA9),
  battle_A9A6DA = battle(0xDA, 0xA6, 0xA9),
  battle_ADE38B = battle(0x8B, 0xE3, 0xAD),
  -- fighting with HP pinned (battle messages, damage, status windows); the scripted battles' enemies show HP 9999,
  -- so no won battle yet
  battle_fight = { area = 0x01, room = 0x00, run = { 0x7D, 0xED, 0xCD, 0xA5, 0x00 }, mash = { "a", 30, 300 }, god = true,
    frames = 4400 },
  -- mash A through the first scripted battle with the new-game party: it loses, the game shows Game Over
  game_over = { area = 0x01, room = 0x00, run = { 0x7D, 0xED, 0xCD, 0xA5, 0x00 }, mash = { "a", 30, 300 }, frames = 3400 },
  -- story areas, room 0 each (one line per scene: run_scenes.py reads the names from this file)
  area_01 = { area = 0x01, room = 0x00 },
  area_02 = { area = 0x02, room = 0x00 },
  area_03 = { area = 0x03, room = 0x00 },
  area_04 = { area = 0x04, room = 0x00 },
  area_05 = { area = 0x05, room = 0x00 },
  area_06 = { area = 0x06, room = 0x00 },
  area_07 = { area = 0x07, room = 0x00 },
  area_08 = { area = 0x08, room = 0x00 },
  area_09 = { area = 0x09, room = 0x00 },
  area_0A = { area = 0x0A, room = 0x00 },
  area_0B = { area = 0x0B, room = 0x00 },
  area_0C = { area = 0x0C, room = 0x00 },
  area_0D = { area = 0x0D, room = 0x00 },
  area_0E = { area = 0x0E, room = 0x00 },
  area_0F = { area = 0x0F, room = 0x00 },
  area_10 = { area = 0x10, room = 0x00 },
  area_11 = { area = 0x11, room = 0x00 },
  area_12 = { area = 0x12, room = 0x00 },
  area_13 = { area = 0x13, room = 0x00 },
  area_14 = { area = 0x14, room = 0x00 },
  area_15 = { area = 0x15, room = 0x00 },
  area_19 = { area = 0x19, room = 0x00 },
  area_1A = { area = 0x1A, room = 0x00 },
  area_1B = { area = 0x1B, room = 0x00 },
  area_1C = { area = 0x1C, room = 0x00 },
  area_1D = { area = 0x1D, room = 0x00 },
  area_1E = { area = 0x1E, room = 0x00 },
  area_1F = { area = 0x1F, room = 0x00 },
}

SCENES = S
return S
