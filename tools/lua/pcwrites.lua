-- Log writes made by code in a PC range (default the VWF, 84:F000-84:FFFF) to addresses in [LO, HI], one line per
-- distinct (pc, address) up to LIMIT lines: finds stray writes from patched code.
--   emu.py ... --script tools/lua/pcwrites.lua [--var PC_LO=0x84F000 --var PC_HI=0x84FFFF] [--var LO=0x7E3000]
--              [--var HI=0x7FFFFF] [--var LIMIT=200] [--var VALUES=1 (one line per distinct value too)]
local pclo, pchi = PC_LO or 0x84F000, PC_HI or 0x84FFFF
local lo, hi, limit = LO or 0x7E3000, HI or 0x7FFFFF, LIMIT or 200
local seen, n = {}, 0
L.on_write(lo, hi, function(addr, value)
  local pc = L.pc()
  if pc < pclo or pc > pchi or n >= limit then return end
  local key = pc * 0x1000000 + addr + (VALUES and (tonumber(value) or 0) * 2 ^ 48 or 0)
  if seen[key] then return end
  seen[key] = true
  n = n + 1
  L.log(string.format("f%d pc=%06X addr=%06X val=%s", L.frame, pc, addr, tostring(value)))
end)
