#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""反汇编 receive_manager 分派链与各指令 handler, 找响应回包(buffer/len来源)"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from elftools.elf.elffile import ELFFile
from elftools.elf.relocation import RelocationSection
from capstone import *

elf = ELFFile(open("btgatt-server.go2.elf", 'rb'))
plt_names = {}
for sec in elf.iter_sections():
    if isinstance(sec, RelocationSection) and '.plt' in sec.name:
        symtab = elf.get_section(sec['sh_link'])
        for rel in sec.iter_relocations():
            plt_names[rel['r_offset']] = symtab.get_symbol(rel['r_info'] >> 32).name
md = Cs(CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN); md.detail = True
stub_name = {}
plt_sec = elf.get_section_by_name('.plt')
insns = list(md.disasm(plt_sec.data(), plt_sec['sh_addr']))
for i in range(len(insns)-3):
    a, b, d = insns[i], insns[i+1], insns[i+3]
    if a.mnemonic=='adrp' and b.mnemonic=='ldr' and d.mnemonic=='br':
        nm = plt_names.get(a.operands[1].imm + b.operands[1].mem.disp)
        if nm: stub_name[a.address] = nm
syms = {}
for s in elf.iter_sections():
    if s.name == '.symtab':
        for sym in s.iter_symbols():
            if sym.name and sym['st_value']:
                syms.setdefault(sym['st_value'], sym.name)
def nm(a):
    return stub_name.get(a) or syms.get(a) or ''

texts = [(s['sh_addr'], s.data()) for s in elf.iter_sections()
         if s['sh_flags'] & 0x4 and s['sh_type'] == 'SHT_PROGBITS']
def dis(lo, hi):
    out = []
    for base, data in texts:
        if base <= lo < base+len(data):
            off = lo - base
            for ins in md.disasm(data[off:off+(hi-lo)], lo):
                ann = ''
                if ins.mnemonic in ('bl','b') and ins.operands:
                    n = nm(ins.operands[0].imm)
                    if n: ann = f'  ; {n}'
                out.append(f"  {ins.address:6x}: {ins.mnemonic:8s} {ins.op_str}{ann}")
            break
    return out

print("=== handler 0x06 @0xeb18 / 0x07 @0xed3c ===")
print('\n'.join(dis(0xeb18, 0xee00)))
print("\n=== 0x04 完成路径 @0xeee0 / 0x05 完成 @0xef20 / 其他尾段 ===")
print('\n'.join(dis(0xee00, 0xf100)))
