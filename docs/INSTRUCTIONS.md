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
ExtractFieldMetadata.java:25: error: cannot find symbol
        String scriptDir = sourceFile.getParent();
                                     ^
  symbol:   method getParent()
  location: variable sourceFile of type generic.jar.ResourceFile
skipping D:\projects\Final-Fantasy-7-Modding\scripts\ghidra\ExtractFieldMetadata.java
> Unable to load script: ExtractFieldMetadata.java
>   detail: The class could not be found. It must be the public class of the .java file: ExtractFieldMetadata not found by acfab9cb [3]



.bat file to run ghidra

:: ###
:: IP: GHIDRA
::
:: Licensed under the Apache License, Version 2.0 (the "License");
:: you may not use this file except in compliance with the License.
:: You may obtain a copy of the License at
::
::      http://www.apache.org/licenses/LICENSE-2.0
::
:: Unless required by applicable law or agreed to in writing, software
:: distributed under the License is distributed on an "AS IS" BASIS,
:: WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
:: See the License for the specific language governing permissions and
:: limitations under the License.
:: ##
:: Ghidra launch

@echo off
setlocal

:: Optionally override the default Java heap memory, which is typically 1/4 of system RAM.
:: Supported values are of the regular expression form "\d+[gGmMkK]", allowing the value to be 
:: specified in gigabytes, megabytes, or kilobytes (for example: 8G, 4096m, etc).
set MAXMEM_DEFAULT=

:: Allow the above MAXMEM_DEFAULT to be overridden by externally set environment variables
:: - GHIDRA_MAXMEM: Desired maximum heap memory for all Ghidra instances
:: - GHIDRA_GUI_MAXMEM: Desired maximum heap memory only for Ghidra GUI instances
if not defined GHIDRA_MAXMEM set "GHIDRA_MAXMEM=%MAXMEM_DEFAULT%"
if not defined GHIDRA_GUI_MAXMEM set "GHIDRA_GUI_MAXMEM=%GHIDRA_MAXMEM%"

:: Apply Java options from externally set environment variables
set VMARG_LIST=%GHIDRA_JAVA_OPTIONS% %GHIDRA_GUI_JAVA_OPTIONS%

call "%~dp0support\launch.bat" bg jdk Ghidra "%GHIDRA_GUI_MAXMEM%" "%VMARG_LIST%" ghidra.GhidraRun %*


