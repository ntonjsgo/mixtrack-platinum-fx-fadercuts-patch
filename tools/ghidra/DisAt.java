// Disassembles (Thumb) and decompiles the functions at the given addresses; writes listing and C to a file.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.io.*;
import java.math.BigInteger;

public class DisAt extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        try (PrintWriter w = new PrintWriter(new FileWriter(a[0]))) {
            for (int i = 1; i < a.length; i++) {
                Address f = toAddr(Long.decode(a[i]));
                if (getInstructionAt(f) == null) {
                    clearListing(f, f.add(1));
                    currentProgram.getProgramContext().setValue(currentProgram.getRegister("TMode"), f, f, BigInteger.ONE);
                    disassemble(f);
                }
                Function fn = getFunctionAt(f);
                if (fn == null) fn = createFunction(f, null);
                w.println("// ===== " + f);
                if (fn == null) { w.println("// no function"); continue; }
                for (Instruction ins : currentProgram.getListing().getInstructions(fn.getBody(), true))
                    w.println("//   " + ins.getAddress() + "  " + ins);
                DecompileResults r = di.decompileFunction(fn, 60, monitor);
                w.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed");
            }
        }
    }
}
