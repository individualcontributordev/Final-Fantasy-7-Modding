#!/usr/bin/env python3
"""
Decode FF7 field script opcodes with full parameter parsing.

Based on Makou Reactor's Opcode.cpp logic.
"""
import sys
from pathlib import Path
from ff7_opcodes import OPCODE_LENGTH, OPCODE_NAMES

def decode_ifuw(raw: bytes, pos: int) -> str:
    """Decode IFUW (0x18) - If Unsigned Word

    Format: 18 <bank> <addr> <val_lo> <val_hi> <comp> <else> <unused>
    """
    if pos + 8 > len(raw):
        return "IFUW [truncated]"

    # First 3 bytes after opcode form the memory address
    bank_addr = int.from_bytes(raw[pos + 1:pos + 4], 'little')
    # Next 2 bytes are the comparison value
    val = int.from_bytes(raw[pos + 4:pos + 6], 'little')
    # Then comparison type and else-offset
    comp = raw[pos + 6]
    els = raw[pos + 7]

    comp_ops = {
        0x00: "==", 0x01: "!=", 0x02: ">", 0x03: "<",
        0x04: ">=", 0x05: "<=", 0x06: "&", 0x07: "^",
        0x08: "|", 0x09: "&!", 0x0A: "==", 0x0B: "!="
    }
    comp_str = comp_ops.get(comp, f"?{comp:#x}")

    return f"IFUW addr={bank_addr:#06x} {comp_str} {val:#x}, else +{els:#x}"

def decode_mapjump(raw: bytes, pos: int) -> str:
    """Decode MAPJUMP (0x60) - Map Jump"""
    if pos + 3 > len(raw):
        return "MAPJUMP [truncated]"
    field_id = int.from_bytes(raw[pos + 1:pos + 3], 'little')
    return f"MAPJUMP field #{field_id} ({field_id:#x})"

def decode_setword(raw: bytes, pos: int) -> str:
    """Decode SETWORD (0x45) - Set Word"""
    if pos + 5 > len(raw):
        return "SETWORD [truncated]"
    bank = raw[pos + 1]
    addr = raw[pos + 2]
    val = int.from_bytes(raw[pos + 3:pos + 5], 'little')
    return f"SETWORD bank{bank}[{addr:#x}] = {val:#x}"

def decode_biton(raw: bytes, pos: int) -> str:
    """Decode BITON (0x82) - Bit On"""
    if pos + 4 > len(raw):
        return "BITON [truncated]"
    bank = raw[pos + 1]
    addr = raw[pos + 2]
    bit = raw[pos + 3]
    return f"BITON bank{bank}[{addr:#x}]#{bit}"

def decode_bitoff(raw: bytes, pos: int) -> str:
    """Decode BITOFF (0x83) - Bit Off"""
    if pos + 4 > len(raw):
        return "BITOFF [truncated]"
    bank = raw[pos + 1]
    addr = raw[pos + 2]
    bit = raw[pos + 3]
    return f"BITOFF bank{bank}[{addr:#x}]#{bit}"

def decode_script(raw: bytes, start: int = 0, max_bytes: int = None) -> list[tuple[int, str, str]]:
    """
    Decode a field script from raw bytes.
    
    Returns: List of (offset, opcode_name, decoded_string) tuples
    """
    results = []
    pos = start
    end = start + max_bytes if max_bytes else len(raw)
    
    while pos < end:
        if pos >= len(raw):
            break
            
        op = raw[pos]
        if op >= len(OPCODE_NAMES):
            results.append((pos, f"UNKNOWN_{op:#x}", ""))
            break
            
        name = OPCODE_NAMES[op]
        
        # Special decoders for important opcodes
        if op == 0x18:  # IFUW
            decoded = decode_ifuw(raw, pos)
        elif op == 0x60:  # MAPJUMP (not 0x2B!)
            decoded = decode_mapjump(raw, pos)
        elif op == 0x45:  # SETWORD
            decoded = decode_setword(raw, pos)
        elif op == 0x82:  # BITON
            decoded = decode_biton(raw, pos)
        elif op == 0x83:  # BITOFF
            decoded = decode_bitoff(raw, pos)
        elif op == 0x00:  # RET
            decoded = "RET"
        else:
            decoded = name
        
        results.append((pos, name, decoded))
        
        # Get size and advance
        size = OPCODE_LENGTH[op] if op < len(OPCODE_LENGTH) else 1
        if size == 0:
            break
        pos += size
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Usage: python decode_field_script.py <hex_string>")
        print("\nExample:")
        print("  python decode_field_script.py 1820000055a40112")
        sys.exit(1)
    
    hex_str = sys.argv[1].replace(" ", "").replace("0x", "")
    raw = bytes.fromhex(hex_str)
    
    print(f"Decoding {len(raw)} bytes:\n")
    results = decode_script(raw)
    
    for offset, opcode, decoded in results:
        print(f"  @{offset:#04x}: {decoded}")

if __name__ == "__main__":
    main()
