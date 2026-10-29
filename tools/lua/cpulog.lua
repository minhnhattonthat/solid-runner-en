-- Log CPU registers on exec of each PC in PCS (first LIMIT hits each), e.g. to check flags/DB at a hook.
--   emu.py ... --script tools/lua/cpulog.lua --var "PCS={0x84F000,0x84AA16}" [--var LIMIT=5] [--var FROM=frame]
-- With STACK=n also logs the n bytes above SP (return addresses).
local pcs = assert(PCS, "set --var PCS={0x...}")
local limit = LIMIT or 5
local n = {}
for _, pc in ipairs(pcs) do
  n[pc] = 0
  L.on_exec(pc, pc, function()
    if n[pc] >= limit or L.frame < (FROM or 0) then return end
    n[pc] = n[pc] + 1
    local s = emu.getState()
    local t = {}
    for _, k in ipairs({ "a", "x", "y", "sp", "d", "dbr", "k", "ps", "emulationMode" }) do
      t[#t + 1] = k .. "=" .. string.format("%X", tonumber(s["cpu." .. k]) or (s["cpu." .. k] and 1 or 0))
    end
    for i = 1, STACK or 0 do
      t[#t + 1] = string.format("%02X", emu.read(s["cpu.sp"] + i, emu.memType.snesMemory))
    end
    L.log(string.format("f%d pc=%06X %s", L.frame, pc, table.concat(t, " ")))
  end)
end
