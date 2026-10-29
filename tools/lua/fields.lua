-- Log where each string starts in the text bitmap: on entry to the instant draw (84:A87B) and on the typewriter's
-- first glyph of a string (84:A7E1, once per string pointer) log frame, string pointer ($18B2-$18B4), column $18BA
-- and strip $18BB, once per distinct (pointer, column, strip). tools/fields.py turns the logs into per-entry field
-- budgets; pc=84A7E1 marks typewriter text (dialogue boxes).
--   emu.py ... --script tools/lua/fields.lua
local mem = emu.memType.snesMemory
local seen = {}
local function ptr()
  return emu.read(0x7E18B2, mem) | emu.read(0x7E18B3, mem) << 8 | emu.read(0x7E18B4, mem) << 16
end
local function log(pc, p)
  local col, row = emu.read(0x7E18BA, mem), emu.read(0x7E18BB, mem)
  local key = string.format("%06X %d %d", p, col, row)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("FIELD f%d pc=%06X ptr=%06X col=%d row=%d", L.frame, pc, p, col, row))
end
L.on_exec(0x84A87B, 0x84A87B, function() log(0x84A87B, ptr()) end)
local last
L.on_exec(0x84A7E1, 0x84A7E1, function()
  -- $18B2 advances per glyph: log a string start ($18B8 glyph count 0) or a jump to another string
  local p = ptr()
  if emu.read(0x7E18B8, mem) == 0 or not last or p < last or p > last + 6 then log(0x84A7E1, p) end
  last = p
end)
