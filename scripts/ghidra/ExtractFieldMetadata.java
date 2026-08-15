// Extract FF7 FIELD.BIN metadata to JSON files
// Run this from Ghidra's Script Manager (Window -> Script Manager)
// 
// Output files (saved to same directory as this script):
//   - field-functions.json    (all functions with addresses, sizes, callers)
//   - field-symbols.json      (all symbols/labels)
//
// @category FF7

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class ExtractFieldMetadata extends GhidraScript {

    @Override
    public void run() throws Exception {
        // Get script directory - use ResourceFile API
        String scriptDir = sourceFile.getParentFile().getAbsolutePath();

        // Get current program name and derive output prefix
        String programName = currentProgram.getName();
        String prefix = programName.toLowerCase()
            .replace(".bin.dec", "")
            .replace(".x.dec", "")
            .replace(".dec", "")
            .replace("_", "-")
            .replace(".", "-");

        println("FF7 Metadata Extraction: " + programName);
        println("======================================================================");
        println("Output directory: " + scriptDir);
        println("Output prefix: " + prefix);
        println("");

        // Extract functions
        extractFunctions(scriptDir, prefix);

        // Extract symbols
        extractSymbols(scriptDir, prefix);

        println("======================================================================");
        println("Extraction complete!");
        println("");
        println("Files created:");
        println("  " + prefix + "-functions.json");
        println("  " + prefix + "-symbols.json");
        println("");
        println("Copy these to workspace/ghidra-analysis/ in your repo, then commit!");
    }
    
    private void extractFunctions(String outputDir, String prefix) throws IOException {
        println("Extracting functions...");

        List<String> lines = new ArrayList<>();
        lines.add("[");

        FunctionManager fm = currentProgram.getFunctionManager();
        FunctionIterator iter = fm.getFunctions(true);

        boolean first = true;
        int count = 0;

        while (iter.hasNext() && !monitor.isCancelled()) {
            Function func = iter.next();
            Address entry = func.getEntryPoint();

            // Get function size
            long size = 0;
            for (var range : func.getBody()) {
                size += range.getLength();
            }

            // Get callers
            List<String> callers = new ArrayList<>();
            for (Reference ref : func.getSymbol().getReferences()) {
                if (ref.getReferenceType().isCall()) {
                    Address fromAddr = ref.getFromAddress();
                    Function callerFunc = fm.getFunctionContaining(fromAddr);
                    if (callerFunc != null) {
                        callers.add("\"" + callerFunc.getEntryPoint().toString() + "\"");
                    }
                }
            }

            // Build JSON object
            if (!first) {
                lines.add(",");
            }
            first = false;

            lines.add("  {");
            lines.add("    \"name\": \"" + escapeJson(func.getName()) + "\",");
            lines.add("    \"address\": \"" + entry.toString() + "\",");
            lines.add("    \"size\": " + size + ",");
            lines.add("    \"callers\": [" + String.join(", ", callers) + "]");
            lines.add("  }");

            count++;
        }

        lines.add("]");

        // Write file
        String outputFile = outputDir + "/" + prefix + "-functions.json";
        writeFile(outputFile, lines);

        println("✅ Functions extracted: " + count);
        println("   Saved to: " + outputFile);
        println("");
    }
    
    private void extractSymbols(String outputDir, String prefix) throws IOException {
        println("Extracting symbols...");

        List<String> lines = new ArrayList<>();
        lines.add("[");

        SymbolTable symbolTable = currentProgram.getSymbolTable();
        SymbolIterator iter = symbolTable.getAllSymbols(true);

        boolean first = true;
        int count = 0;

        while (iter.hasNext() && !monitor.isCancelled()) {
            Symbol symbol = iter.next();

            // Skip default/analysis symbols
            SourceType source = symbol.getSource();
            if (source == SourceType.DEFAULT || source == SourceType.ANALYSIS) {
                continue;
            }

            // Build JSON object
            if (!first) {
                lines.add(",");
            }
            first = false;

            lines.add("  {");
            lines.add("    \"name\": \"" + escapeJson(symbol.getName()) + "\",");
            lines.add("    \"address\": \"" + symbol.getAddress().toString() + "\",");
            lines.add("    \"type\": \"" + symbol.getSymbolType().toString() + "\",");
            lines.add("    \"namespace\": \"" + escapeJson(symbol.getParentNamespace().getName()) + "\"");
            lines.add("  }");

            count++;
        }

        lines.add("]");

        // Write file
        String outputFile = outputDir + "/" + prefix + "-symbols.json";
        writeFile(outputFile, lines);

        println("✅ Symbols extracted: " + count);
        println("   Saved to: " + outputFile);
        println("");
    }
    
    private void writeFile(String path, List<String> lines) throws IOException {
        try (FileWriter writer = new FileWriter(path)) {
            for (String line : lines) {
                writer.write(line + "\n");
            }
        }
    }
    
    private String escapeJson(String str) {
        return str.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
