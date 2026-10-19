// Seeds Cortex-M vector tables as Thumb functions, re-analyzes, and dumps functions, strings with xrefs, and decompiled C.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.data.*;
import java.io.*;
import java.math.BigInteger;
import java.util.*;

public class DumpFw extends GhidraScript {
    void seed(long vt, int n, String tag) throws Exception {
        Register tmode = currentProgram.getRegister("TMode");
        for (int i = 1; i < n; i++) {
            Address a = toAddr(vt + 4L * i);
            long v = getInt(a) & 0xffffffffL;
            if ((v & 1) == 0 || v < 0x08000000L || v >= 0x08040000L) continue;
            Address f = toAddr(v & ~1L);
            if (getInstructionAt(f) == null) {
                try { currentProgram.getProgramContext().setValue(tmode, f, f, BigInteger.ONE); } catch (Exception e) { println("ctx skip " + f); }
            }
            disassemble(f);
            if (getFunctionAt(f) == null) createFunction(f, tag + "_vec" + i);
        }
        createLabel(toAddr(vt), tag + "_vector_table", true);
    }
    public void run() throws Exception {
        seed(0x08000000L, 100, "boot");
        seed(0x0800C000L, 100, "app");
        analyzeAll(currentProgram);
        String out = getScriptArgs()[0];
        try (PrintWriter w = new PrintWriter(new FileWriter(out + "/functions.txt"))) {
            for (Function f : currentProgram.getFunctionManager().getFunctions(true))
                w.println(f.getEntryPoint() + " " + f.getName() + " size=" + f.getBody().getNumAddresses());
        }
        try (PrintWriter w = new PrintWriter(new FileWriter(out + "/strings.txt"))) {
            for (Data d : currentProgram.getListing().getDefinedData(true)) {
                if (!d.hasStringValue()) continue;
                StringBuilder refs = new StringBuilder();
                for (Reference r : getReferencesTo(d.getAddress())) {
                    Function f = getFunctionContaining(r.getFromAddress());
                    refs.append(" ").append(f == null ? r.getFromAddress().toString() : f.getName());
                }
                w.println(d.getAddress() + " " + d.getDefaultValueRepresentation() + " <-" + refs);
            }
        }
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        try (PrintWriter w = new PrintWriter(new FileWriter(out + "/decomp.c"))) {
            for (Function f : currentProgram.getFunctionManager().getFunctions(true)) {
                DecompileResults r = di.decompileFunction(f, 60, monitor);
                w.println("// ===== " + f.getEntryPoint() + " " + f.getName());
                w.println(r.decompileCompleted() ? r.getDecompiledFunction().getC() : "// decompile failed: " + r.getErrorMessage());
            }
        }
        println("DONE functions=" + currentProgram.getFunctionManager().getFunctionCount());
    }
}
