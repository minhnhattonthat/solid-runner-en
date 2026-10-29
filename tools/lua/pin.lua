-- Pin bits every frame (a cheat for play.py sessions or emu.py runs): story flags a script keeps re-setting.
--   play.py SESSION --rom R --state S --script tools/lua/pin.lua --var "SET={[0x7000C2]=0x61}" --var "CLR={[0x70003D]=0x01}"
-- POKE={[addr]=byte} writes once, on the first frame: e.g. an NPC's resume script (thread x: lo $7E:B4C2+x,
-- hi $7E:B4E7+x, bank $7E:B50C+x, set by VM op 49/4A at 81:D33F) to make talking to it run another script.
local mem = emu.memType.snesMemory
local poked = false
L.on_frame(function()
  if not poked then
    for a, v in pairs(POKE or {}) do emu.write(a, v, mem) end
    poked = true
  end
  for a, m in pairs(CLR or {}) do emu.write(a, emu.read(a, mem) & ~m, mem) end
  for a, m in pairs(SET or {}) do emu.write(a, emu.read(a, mem) | m, mem) end
end)
