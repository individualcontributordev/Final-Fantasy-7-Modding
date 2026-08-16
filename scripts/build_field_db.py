#!/usr/bin/env python3
"""Build field script database for FF7 modding analysis.

Extracts and analyzes field scripts from pristine and CSR disc images,
storing opcode data in SQLite for quick querying.

Usage:
    python scripts/build_field_db.py
    python scripts/build_field_db.py --fields BLACKBGB LOST2 COS_BTM2
"""
import argparse
import sqlite3
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from psx_mode2_iso import extract_file
from lzs import decompress_all_with_header
from field_dat import load_field_dat, op_size

DB_PATH = ROOT / "docs/reference/field-scripts.db"
OPCODE_NAMES = {
    0x00: 'RET', 0x2B: 'MAPJUMP', 0x2C: 'SETBYTE', 0x31: 'MUSIC',
    0x33: 'IFUW', 0x34: 'IFSW', 0x35: 'IFUB', 0x36: 'IFUBL',
}


def init_db():
    """Create database schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY,
            field_name TEXT NOT NULL,
            disc INTEGER NOT NULL,
            source TEXT NOT NULL,
            num_scripts INTEGER,
            file_size INTEGER,
            UNIQUE(field_name, disc, source)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opcodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id INTEGER,
            entity TEXT,
            script_slot INTEGER,
            offset INTEGER,
            opcode INTEGER,
            opcode_name TEXT,
            param1 INTEGER,
            param2 INTEGER,
            param_text TEXT,
            FOREIGN KEY(field_id) REFERENCES fields(id)
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_opcodes_field ON opcodes(field_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_opcodes_name ON opcodes(opcode_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_opcodes_type ON opcodes(opcode)')
    
    conn.commit()
    return conn


def analyze_field(conn, img_bytes, field_path, disc, source):
    """Analyze a field and store opcodes in database."""
    cursor = conn.cursor()
    field_name = field_path.split('/')[-1].replace('.DAT', '')
    
    try:
        compressed = extract_file(img_bytes, field_path)
        field_data = decompress_all_with_header(compressed)
        dat = load_field_dat(field_data)
        
        # Insert/update field record
        cursor.execute('''
            INSERT OR REPLACE INTO fields (field_name, disc, source, num_scripts, file_size)
            VALUES (?, ?, ?, ?, ?)
        ''', (field_name, disc, source, len(dat.scripts), len(compressed)))
        
        field_id = cursor.lastrowid
        
        # Delete old opcodes
        cursor.execute('DELETE FROM opcodes WHERE field_id = ?', (field_id,))
        
        # Parse scripts and store important opcodes
        for script in dat.scripts:
            pos = 0
            while pos < len(script.raw):
                op = script.raw[pos]
                
                # Store these opcodes: MAPJUMP, MUSIC, SETBYTE, IFUW, IFSW, IFUB, IFUBL, RET
                if op in OPCODE_NAMES:
                    param1 = param2 = None
                    param_text = None
                    
                    if op == 0x2B:  # MAPJUMP
                        if pos+2 < len(script.raw):
                            param1 = struct.unpack("<H", script.raw[pos+1:pos+3])[0]
                            param_text = f"field #{param1}"
                    elif op == 0x31:  # MUSIC
                        if pos+1 < len(script.raw):
                            param1 = script.raw[pos+1]
                            param_text = f"id {param1}"
                    elif op == 0x2C:  # SETBYTE
                        if pos+3 < len(script.raw):
                            param1 = script.raw[pos+1]
                            param2 = script.raw[pos+2]
                            param_text = f"bank={param1} val={param2}"
                    elif op in [0x33, 0x34, 0x35, 0x36]:  # IF opcodes
                        if pos+5 < len(script.raw):
                            param1 = struct.unpack("<H", script.raw[pos+1:pos+3])[0]
                            param2 = script.raw[pos+5]  # E byte (else offset)
                            param_text = f"var={param1} else_offset={param2}"
                    
                    cursor.execute('''
                        INSERT INTO opcodes (field_id, entity, script_slot, offset, opcode, opcode_name, param1, param2, param_text)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (field_id, script.entity, script.slot, pos, op, OPCODE_NAMES[op],
                          param1, param2, param_text))
                
                size = op_size(script.raw, pos)
                if size == 0:
                    break
                pos += size
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"  ❌ {field_name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Build FF7 field script database')
    parser.add_argument('--fields', nargs='+', help='Specific fields to analyze (default: key transition fields)')
    parser.add_argument('--sources', nargs='+', default=['pristine'], 
                       help='Sources to analyze: pristine, csr (default: pristine)')
    
    args = parser.parse_args()
    
    # Default to key disc transition fields
    fields = args.fields or ['BLACKBGB', 'LOSIN2', 'LOST2', 'COS_BTM2']
    
    print(f"🔧 Building field script database: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = init_db()
    
    # Analyze pristine discs
    if 'pristine' in args.sources:
        print("\n📊 Analyzing pristine discs...")
        pristine_d1 = ROOT / "workspace/pristine/FINALFANTASY7_D1.bin"
        pristine_d2 = ROOT / "workspace/pristine/FINALFANTASY7_D2.bin"
        
        if pristine_d1.exists() and pristine_d2.exists():
            d1_img = pristine_d1.read_bytes()
            d2_img = pristine_d2.read_bytes()
            
            for field in fields:
                print(f"  {field}...", end=' ')
                ok1 = analyze_field(conn, d1_img, f"FIELD/{field}.DAT", 1, "pristine")
                ok2 = analyze_field(conn, d2_img, f"FIELD/{field}.DAT", 2, "pristine")
                print("✅" if ok1 and ok2 else "")
        else:
            print(f"  ⚠️  Pristine discs not found in workspace/pristine/")
    
    conn.close()
    print(f"\n✅ Database saved: {DB_PATH}")
    print(f"\n📖 Query with: python scripts/query_field_scripts.py --help")


if __name__ == '__main__':
    main()
