-- Warp from a cold boot to any scene in scenes.lua (or a raw AREA/ROOM), no save needed.
--   emu.py ROM --out DIR --script tools/debug/scenes.lua --script tools/debug/warp.lua --var "SCENE='name'"
--          --frames 900 --sheet
--   --var AREA=0x02 --var ROOM=0x00     raw map instead of a named scene
--   --var "RUN={0x7D,0xED,0xCD,0xA5,0x00}"   with a raw map: event script to inject (scene.run below)
--   --var GOD=1   pin HP to max every frame; --var HPLOG=1 logs HP every 60 frames
-- How (docs/re/events.md, "Map loading"): mash Start through title -> NEW GAME -> name entry; the game then loads
-- area $01 room $00 through 80:C546. On that call this script rewrites the area ($7E:1AA8) and room ($7E:1AA9) and the
-- scene's SRAM story flags ($70:xxxx), so the game loads the target itself. One cold boot per scene: queueing the
-- game's map-change task (80:D2C3, as VM op 4D does) for a second warp stalled in the battle arena.
local mem = emu.memType.snesMemory
local function rd(a) return emu.read(a, mem) end
local function wr(a, v) emu.write(a, v, mem) end

local scenes = assert(SCENES, "pass --script tools/debug/scenes.lua before warp.lua")
local scene
if SCENE then
  scene = assert(scenes.list[SCENE], "unknown SCENE " .. tostring(SCENE))
else
  scene = { area = AREA or 1, room = ROOM or 0, run = RUN }
end
local warped, warp_frame, mashing = false, nil, true
local ready_frame, held

-- scene.run = {bytes}: event-VM script written (in emulator memory only, never the file) over the first map's opening
-- event thread at 95:84BC, so it runs when the scene's map (area $01 room $00) starts. E.g. {0x7D, lo, hi, bank, 0x00}
-- starts the scripted battle whose record is at bank:hi lo, then ends the thread.
if scene.run then
  for i, b in ipairs(scene.run) do emu.write(L.rom_off(0x9584BC) + i - 1, b, emu.memType.snesPrgRom) end
end

L.on_exec(0x80C546, 0x80C546, function()
  local a, r = rd(0x7E1AA8), rd(0x7E1AA9)
  if not warped and a == 0x01 and r == 0x00 then
    wr(0x7E1AA8, scene.area); wr(0x7E1AA9, scene.room)
    for addr, v in pairs(scene.flags or {}) do wr(addr, v) end
    warped, warp_frame, mashing = true, L.frame, false
    L.log(string.format("WARP f%d -> area %02X room %02X (%s)", L.frame, scene.area, scene.room, SCENE or "raw"))
  else
    L.log(string.format("load f%d area %02X room %02X", L.frame, a, r))
  end
end)

-- Start every 40 frames from f1250 until the new game reaches its first map load
emu.addEventCallback(L.safe(function()
  if mashing and L.frame >= 1250 and L.frame % 40 < 6 then emu.setInput({ start = true }, 0) end
  -- scene.mash = {key, every, from}: press key for 6 frames every `every` frames from `from` frames after the warp,
  -- until scene.wait holds (if given)
  local m = scene.mash
  local t = warped and L.frame - warp_frame
  if m and t and t >= (m[3] or 0) and not (held and held > 0) and not ready_frame and L.frame % m[2] < 6 then
    emu.setInput({ [m[1]] = true }, 0)
  end
  -- scene.keys = {{frames after the warp (or after scene.wait holds), "a+up"}, ...}: each held 6 frames
  local base = scene.wait and ready_frame or (not scene.wait and warp_frame)
  for _, k in ipairs(base and scene.keys or {}) do
    local d = L.frame - base - k[1]
    if d >= 0 and d < 6 then
      local b = {}
      for name in k[2]:gmatch("[^+]+") do b[name] = true end
      emu.setInput(b, 0)
    end
  end
end), emu.eventType.inputPolled)

L.on_frame(function(n)
  -- Mesen keeps SRAM in tools/mesen/Saves/<rom>.srm across runs (save_game fills slot 1; then the title can land
  -- on CONTINUE): blank the 8 KiB at power-on so every cold boot starts from no save
  if n == 1 then for a = 0x700000, 0x701FFF do wr(a, 0) end end
  if not warped and n > 4000 then L.fail("warp: new game never reached its first map load") end
  -- Shu: max HP $7E:1896, current $7E:189A (16-bit; verified: falls in battle, game over at 0)
  if GOD or scene.god then wr(0x7E189A, rd(0x7E1896)); wr(0x7E189B, rd(0x7E1897)) end
  if HPLOG and n % 60 == 0 then L.log(string.format("f%d hp %d/%d", n, rd(0x7E189A) | rd(0x7E189B) << 8, rd(0x7E1896) | rd(0x7E1897) << 8)) end
  if not warped then return end
  -- scene.wait = {{addr, byte}, ...}: all must hold (for 30 frames) before scene.keys start
  if scene.wait and not ready_frame then
    local ok = true
    for _, w in ipairs(scene.wait) do ok = ok and rd(w[1]) == w[2] end
    held = ok and (held or 0) + 1 or 0
    if held >= 30 then
      ready_frame = n
      for addr, v in pairs(scene.ready_flags or {}) do wr(addr, v) end
      L.log(string.format("READY f%d (+%d after the warp)", n, n - warp_frame))
    elseif n - warp_frame > 6000 then
      L.fail("warp: scene.wait never held")
    end
  end
end)
