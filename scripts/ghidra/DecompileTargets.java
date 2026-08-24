// Headless post-script: decompile a fixed list of function addresses and
// their direct callers, writing plain-text C output to a file.
//
// Run via analyzeHeadless -postScript DecompileTargets.java <outputPath> <addr1> <addr2> ...
// Addresses are hex without 0x, e.g. 800bf908
//
// @category FF7

import java.io.FileWriter;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.util.task.ConsoleTaskMonitor;

public class DecompileTargets extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            println("Usage: <outputPath> <addr1> [addr2 ...]");
            return;
        }
        String outputPath = args[0];

        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        FunctionManager fm = currentProgram.getFunctionManager();

        StringBuilder sb = new StringBuilder();

        for (int i = 1; i < args.length; i++) {
            String hex = args[i].replace("0x", "");
            Address addr = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress("0x" + hex);
            Function func = fm.getFunctionContaining(addr);
            if (func == null) {
                try {
                    func = createFunction(addr, null);
                } catch (Exception e) {
                    // ignore, handled below
                }
            }
            if (func == null) {
                sb.append("=== ").append(hex).append(": NO FUNCTION FOUND ===\n\n");
                continue;
            }

            sb.append("=== ").append(func.getName()).append(" @ ")
              .append(func.getEntryPoint()).append(" ===\n");

            // Callers
            sb.append("-- callers --\n");
            for (Reference ref : func.getSymbol().getReferences()) {
                if (ref.getReferenceType().isCall()) {
                    Address from = ref.getFromAddress();
                    Function callerFunc = fm.getFunctionContaining(from);
                    String callerName = callerFunc != null ? callerFunc.getName() : "?";
                    sb.append("  ").append(from).append(" (in ").append(callerName).append(")\n");
                }
            }

            // All references (including data/table refs, not just calls)
            sb.append("-- all references to entry point --\n");
            for (Reference ref : currentProgram.getReferenceManager().getReferencesTo(func.getEntryPoint())) {
                Address from = ref.getFromAddress();
                Function fromFunc = fm.getFunctionContaining(from);
                String fromName = fromFunc != null ? fromFunc.getName() : "?";
                sb.append("  ").append(from).append(" type=").append(ref.getReferenceType())
                  .append(" (in ").append(fromName).append(")\n");
            }

            sb.append("-- decompile --\n");
            DecompileResults res = decomp.decompileFunction(func, 60, new ConsoleTaskMonitor());
            if (res != null && res.decompileCompleted()) {
                sb.append(res.getDecompiledFunction().getC());
            } else {
                sb.append("DECOMPILE FAILED: ")
                  .append(res != null ? res.getErrorMessage() : "null result").append("\n");
            }
            sb.append("\n\n");
        }

        try (FileWriter w = new FileWriter(outputPath)) {
            w.write(sb.toString());
        }
        println("Wrote output to " + outputPath);
    }
}
