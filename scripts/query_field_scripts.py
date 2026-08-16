#!/usr/bin/env python3
"""Query field script database for FF7 modding analysis.

Usage:
    python scripts/query_field_scripts.py --field BLACKBGB
    python scripts/query_field_scripts.py --opcode MAPJUMP
    python scripts/query_field_scripts.py --field LOST2 --source pristine
"""
import argparse
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "docs/reference/field-scripts.db"


def query_field(field_name: str, disc: Optional[int] = None, source: Optional[str] = None):
    """Show all opcodes for a specific field."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT f.field_name, f.disc, f.source, o.entity, o.script_slot, 
               o.offset, o.opcode_name, o.param_text
        FROM fields f
        JOIN opcodes o ON f.id = o.field_id
        WHERE f.field_name = ?
    '''
    params = [field_name]
    
    if disc:
        query += ' AND f.disc = ?'
        params.append(disc)
    
    if source:
        query += ' AND f.source = ?'
        params.append(source)
    
    query += ' ORDER BY f.disc, f.source, o.entity, o.script_slot, o.offset'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    if not results:
        print(f"No data found for field: {field_name}")
        return
    
    current_key = None
    for field, disc, src, entity, slot, offset, opcode, param in results:
        key = (field, disc, src, entity, slot)
        if key != current_key:
            print(f"\n{field} (D{disc}, {src}) - {entity}/script{slot}:")
            current_key = key
        
        param_str = f" {param}" if param else ""
        print(f"  @{offset:04X}: {opcode}{param_str}")
    
    conn.close()


def query_opcode(opcode_name: str, field_name: Optional[str] = None):
    """Show all instances of a specific opcode."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = '''
        SELECT f.field_name, f.disc, f.source, o.entity, o.script_slot, 
               o.offset, o.param_text
        FROM fields f
        JOIN opcodes o ON f.id = o.field_id
        WHERE o.opcode_name = ?
    '''
    params = [opcode_name]
    
    if field_name:
        query += ' AND f.field_name = ?'
        params.append(field_name)
    
    query += ' ORDER BY f.field_name, f.disc, f.source, o.entity, o.script_slot, o.offset'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    if not results:
        print(f"No {opcode_name} opcodes found")
        return
    
    print(f"\n{opcode_name} opcodes ({len(results)} found):\n")
    for field, disc, src, entity, slot, offset, param in results:
        param_str = f" → {param}" if param else ""
        print(f"  {field} (D{disc}, {src}) {entity}/script{slot} @{offset:04X}{param_str}")
    
    conn.close()


def list_fields(source: Optional[str] = None):
    """List all fields in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = 'SELECT field_name, disc, source, num_scripts FROM fields'
    params = []
    
    if source:
        query += ' WHERE source = ?'
        params.append(source)
    
    query += ' ORDER BY field_name, disc, source'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    print(f"\nFields in database ({len(results)} entries):\n")
    for field, disc, src, num_scripts in results:
        print(f"  {field:12} D{disc} {src:12} ({num_scripts} scripts)")
    
    conn.close()


def main():
    parser = argparse.ArgumentParser(description='Query FF7 field script database')
    parser.add_argument('--field', help='Field name to query')
    parser.add_argument('--opcode', help='Opcode name to search for (MAPJUMP, MUSIC, etc.)')
    parser.add_argument('--disc', type=int, choices=[1, 2, 3], help='Filter by disc number')
    parser.add_argument('--source', help='Filter by source (pristine, csr-d1, csr-d2, single-disc)')
    parser.add_argument('--list', action='store_true', help='List all fields in database')
    
    args = parser.parse_args()
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("Run scripts/build_field_db.py first to create it")
        return 1
    
    if args.list:
        list_fields(args.source)
    elif args.field:
        query_field(args.field, args.disc, args.source)
    elif args.opcode:
        query_opcode(args.opcode, args.field)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
