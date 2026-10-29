-- Log where each string starts in the text bitmap: on entry to the engine's string starts (84:A87B instant draw,
-- 84:A8C6 typewriter) log frame, string pointer ($18B2-$18B4), column $18BA and strip $18BB, once per distinct
-- (pointer, column, strip). tools/fields.py turns the logs into per-entry field budgets.
--   emu.py ... --script tools/lua/fields.lua
local mem = emu.memType.snesMemory
local seen = {}
for _, pc in ipairs({ 0x84A87B, 0x84A8C6 }) do
  L.on_exec(pc, pc, function()
    local ptr = emu.read(0x7E18B2, mem) | emu.read(0x7E18B3, mem) << 8 | emu.read(0x7E18B4, mem) << 16
    local col, row = emu.read(0x7E18BA, mem), emu.read(0x7E18BB, mem)
    local key = string.format("%06X %d %d", ptr, col, row)
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("FIELD f%d pc=%06X ptr=%06X col=%d row=%d", L.frame, pc, ptr, col, row))
  end)
end
