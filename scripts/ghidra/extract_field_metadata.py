# Extract FF7 FIELD.BIN metadata to JSON files
# Run this from Ghidra's Script Manager (Window -> Script Manager)
# 
# Output files (saved to same directory as this script):
#   - field-functions.json    (all functions with addresses, sizes, callers)
#   - field-symbols.json      (all symbols/labels)
#
# @category FF7

import json
from ghidra.program.model.symbol import SymbolType

# Get the directory where this script is located
script_dir = str(sourceFile.getParentFile())
output_dir = script_dir

print("FF7 FIELD.BIN Metadata Extraction")
print("=" * 70)
print("Output directory: " + output_dir)
print("")

# --- EXTRACT FUNCTIONS ---
print("Extracting functions...")
functions_output = []
fm = currentProgram.getFunctionManager()

for func in fm.getFunctions(True):
    entry = func.getEntryPoint()
    body = func.getBody()
    
    # Get function size
    size = 0
    for addr_range in body:
        size += addr_range.getLength()
    
    # Get callers
    callers = []
    refs = func.getSymbol().getReferences()
    for ref in refs:
        if ref.getReferenceType().isCall():
            from_addr = ref.getFromAddress()
            caller_func = fm.getFunctionContaining(from_addr)
            if caller_func:
                callers.append(str(caller_func.getEntryPoint()))
    
    functions_output.append({
        "name": func.getName(),
        "address": str(entry),
        "size": size,
        "callers": callers
    })

functions_file = output_dir + "/field-functions.json"
with open(functions_file, "w") as f:
    json.dump(functions_output, f, indent=2)

print("✅ Functions extracted: " + str(len(functions_output)))
print("   Saved to: " + functions_file)
print("")

# --- EXTRACT SYMBOLS ---
print("Extracting symbols...")
symbols_output = []
symbol_table = currentProgram.getSymbolTable()

for symbol in symbol_table.getAllSymbols(True):
    # Skip default/dynamic symbols
    if symbol.getSource().toString() in ["DEFAULT", "ANALYSIS"]:
        continue
    
    sym_type = symbol.getSymbolType()
    
    symbols_output.append({
        "name": symbol.getName(),
        "address": str(symbol.getAddress()),
        "type": str(sym_type),
        "namespace": str(symbol.getParentNamespace().getName())
    })

symbols_file = output_dir + "/field-symbols.json"
with open(symbols_file, "w") as f:
    json.dump(symbols_output, f, indent=2)

print("✅ Symbols extracted: " + str(len(symbols_output)))
print("   Saved to: " + symbols_file)
print("")

# --- SUMMARY ---
print("=" * 70)
print("Extraction complete!")
print("")
print("Generated files:")
print("  - " + functions_file)
print("  - " + symbols_file)
print("")
print("File sizes:")
import os
print("  - field-functions.json: " + str(os.path.getsize(functions_file) / 1024) + " KB")
print("  - field-symbols.json: " + str(os.path.getsize(symbols_file) / 1024) + " KB")
print("")
print("Copy these files to workspace/ghidra-analysis/ in your repo, then commit!")
