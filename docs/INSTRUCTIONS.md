# INSTRUCTIONS — Extract FF7 Metadata from Ghidra

## Goal

Extract FIELD.BIN functions and symbols from Ghidra as JSON files so Agent can query game structure for modding work.

## Prerequisites (already done ✅)

- Ghidra 12.1+ installed
- Java 17+
- FF7 Ghidra project created with FIELD.BIN.dec imported and analyzed

---

## Extract Metadata from Ghidra

### Step 1: Run the extraction script in Ghidra

1. Open Ghidra GUI
2. Open your `FF7` project
3. Double-click `FIELD.BIN.dec` to open it
4. Open Script Manager: **Window → Script Manager** (or `Ctrl+Shift+S`)
5. In Script Manager, click the folder icon (top-left) and browse to:
   ```
   <your-repo-path>/Final-Fantasy-7-Modding/scripts/ghidra/
   ```
6. Double-click `ExtractFieldMetadata.java` to run it
7. Watch the Console window (bottom of Ghidra) for progress
8. Should complete in 10-30 seconds
9. Output files are saved to `scripts/ghidra/`:
   - `field-functions.json`
   - `field-symbols.json`

### Step 2: Copy files to workspace

```bash
cd ~/Final-Fantasy-7-Modding
mkdir -p workspace/ghidra-analysis
cp scripts/ghidra/field-*.json workspace/ghidra-analysis/
```

### Step 3: Commit the metadata

```bash
git add workspace/ghidra-analysis/
git commit -m "Add Ghidra metadata for FIELD.BIN"
git push
```

✅ **Done!** Agent can now query these JSON files for accurate modding work.


> Unable to load script: extract_field_metadata.py
>   detail: Ghidra was not started with PyGhidra. Python is not available
ExtractFieldMetadata.java:24: error: cannot find symbol
        String scriptDir = getScriptFile().getParent();
                           ^
  symbol:   method getScriptFile()
  location: class ExtractFieldMetadata
skipping D:\projects\Final-Fantasy-7-Modding\scripts\ghidra\ExtractFieldMetadata.java
> Unable to load script: ExtractFieldMetadata.java
>   detail: The class could not be found. It must be the public class of the .java file: ExtractFieldMetadata not found by acfab9cb [2]
