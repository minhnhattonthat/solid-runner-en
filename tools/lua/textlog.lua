-- Log each distinct string pointer handed to a text reader: on exec of each PC in TEXT_PCS, read the 24-bit
-- pointer at direct page PTR_DP (default $50) plus Y, and dump 24 bytes from there.
--   emu.py ... --script tools/lua/textlog.lua [--var "TEXT_PCS={0x84A920}"] [--var PTR_DP=0x50]
local pcs = TEXT_PCS or { 0x84A920 }
local dp = PTR_DP or 0x50
local mem = emu.memType.snesMemory
local seen = {}
for _, pc in ipairs(pcs) do
  L.on_exec(pc, pc, function()
    local s = emu.getState()
    local d = s["cpu.d"] or 0
    local base = emu.read(d + dp, mem) | emu.read(d + dp + 1, mem) << 8 | emu.read(d + dp + 2, mem) << 16
    local key = string.format("%06X:%06X", pc, base)
    if seen[key] then return end
    seen[key] = true
    local t = {}
    for i = 0, 23 do t[#t + 1] = string.format("%02X", emu.read(base + s["cpu.y"] + i, mem)) end
    L.log(string.format("f%d pc=%06X ptr=%06X y=%04X off=%06X %s", L.frame, pc, base, s["cpu.y"],
      L.rom_off(base), table.concat(t, " ")))
  end)
end
