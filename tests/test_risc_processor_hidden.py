import os
from pathlib import Path
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer # [Adicionado Timer]
from cocotb_tools.runner import get_runner

# ==============================================================================
# 1. CONSTANTS & OPCODES
# ==============================================================================
HLT = 0
SKZ = 1
ADD = 2
AND = 3
XOR = 4
LDA = 5
STO = 6
JMP = 7

# ==============================================================================
# 2. TEST DATA DEFINITIONS
# ==============================================================================
# (Mantido igual ao original)
MANUAL_TESTS = [
    {
        "name": "HLT Instruction",
        "cycles": 2,
        "mem": {0: (HLT << 5)}
    },
    {
        "name": "JMP Instruction",
        "cycles": 10,
        "mem": {
            0: (JMP << 5) | 2,
            1: (JMP << 5) | 2,
            2: (HLT << 5)
        }
    },
    {
        "name": "SKZ Instruction",
        "cycles": 10,
        "mem": {
            0: (SKZ << 5),
            1: (JMP << 5) | 2,
            2: (HLT << 5)
        }
    },
    {
        "name": "LDA Instruction",
        "cycles": 18,
        "mem": {
            0: (LDA << 5) | 5,
            1: (SKZ << 5),
            2: (HLT << 5),
            3: (JMP << 5) | 4,
            4: (HLT << 5),
            5: 1
        }
    },
    {
        "name": "STO Instruction",
        "cycles": 34,
        "mem": {
            0: (LDA << 5) | 7,
            1: (STO << 5) | 8,
            2: (LDA << 5) | 8,
            3: (SKZ << 5),
            4: (HLT << 5),
            5: (JMP << 5) | 6,
            6: (HLT << 5),
            7: 1,
            8: 0  # Destination
        }
    },
    {
        "name": "AND Instruction",
        "cycles": 58,
        "mem": {
            0: (LDA << 5) | 10,
            1: (AND << 5) | 11,
            2: (SKZ << 5),
            3: (JMP << 5) | 5,
            4: (HLT << 5),
            5: (AND << 5) | 12,
            6: (SKZ << 5),
            7: (HLT << 5),
            8: (JMP << 5) | 9,
            9: (HLT << 5),
            10: 0xFF,
            11: 0x01,
            12: 0xFE
        }
    },
    {
        "name": "XOR Instruction",
        "cycles": 58,
        "mem": {
            0: (LDA << 5) | 10,
            1: (XOR << 5) | 11,
            2: (SKZ << 5),
            3: (JMP << 5) | 5,
            4: (HLT << 5),
            5: (XOR << 5) | 12,
            6: (SKZ << 5),
            7: (HLT << 5),
            8: (JMP << 5) | 9,
            9: (HLT << 5),
            10: 0x55,
            11: 0x54,
            12: 0x01
        }
    },
    {
        "name": "ADD Instruction",
        "cycles": 42,
        "mem": {
            0: (LDA << 5) | 9,
            1: (ADD << 5) | 11,
            2: (SKZ << 5),
            3: (HLT << 5),
            4: (ADD << 5) | 11,
            5: (SKZ << 5),
            6: (HLT << 5),
            7: (JMP << 5) | 9,
            8: (HLT << 5),
            9: 0xFF,
            11: 0x01
        }
    }
]

PROGRAM_FILES = {
    "CPUtest1": {
        "cycles": 138,
        "content": """
@00 111_11110     // JMP TST_JMP
    000_00000     // HLT
    000_00000     // HLT
    101_11010     // JMP_OK: LDA DATA_1
    001_00000     // SKZ
    000_00000     // HLT
    101_11011     // LDA DATA_2
    001_00000     // SKZ
    111_01010     // JMP SKZ_OK
    000_00000     // HLT
    110_11100     // SKZ_OK: STO TEMP
    101_11010     // LDA DATA_1
    110_11100     // STO TEMP
    101_11100     // LDA TEMP
    001_00000     // SKZ
    000_00000     // HLT
    100_11011     // XOR DATA_2
    001_00000     // SKZ
    111_10100     // JMP XOR_OK
    000_00000     // HLT
    100_11011     // XOR_OK: XOR DATA_2
    001_00000     // SKZ
    000_00000     // HLT
    000_00000     // END: HLT
    111_00000     // JMP BEGIN
@1A 00000000      // DATA_1
    11111111      // DATA_2
    10101010      // TEMP
@1E 111_00011     // TST_JMP: JMP JMP_OK
    000_00000     // HLT
"""
    },
    "CPUtest2": {
        "cycles": 106,
        "content": """
@00 101_11011     // BEGIN: LDA DATA_2
    011_11100     // AND DATA_3
    100_11011     // XOR DATA_2
    001_00000     // SKZ
    000_00000     // HLT
    010_11010     // ADD DATA_1
    001_00000     // SKZ
    111_01001     // JMP ADD_OK
    000_00000     // HLT
    100_11100     // XOR DATA_3
    010_11010     // ADD DATA_1
    110_11101     // STO TEMP
    101_11010     // LDA DATA_1
    010_11101     // ADD TEMP
    001_00000     // SKZ
    000_00000     // HLT
    000_00000     // END: HLT
    111_00000     // JMP BEGIN
@1A 00000001      // DATA_1
    10101010      // DATA_2
    11111111      // DATA_3
    00000000      // TEMP
"""
    },
    "CPUtest3": {
        "cycles": 938,
        "content": """
    111_00011     // JMP LOOP
@03 101_11011     // LOOP: LDA FN2
    110_11100     // STO TEMP
    010_11010     // ADD FN1
    110_11011     // STO FN2
    101_11100     // LDA TEMP
    110_11010     // STO FN1
    100_11101     // XOR LIMIT
    001_00000     // SKZ
    111_00011     // JMP LOOP
    000_00000     // DONE: HLT
    101_11111     // AGAIN: LDA ONE
    110_11010     // STO FN1
    101_11110     // LDA ZERO
    110_11011     // STO FN2
    111_00011     // JMP LOOP
@1A 00000001      // FN1
    00000000      // FN2
    00000000      // TEMP
    10010000      // LIMIT
    00000000      // ZERO
    00000001      // ONE
"""
    }
}

# ==============================================================================
# 3. HELPER FUNCTIONS
# ==============================================================================

def clear_memory(dut):
    """
    Clears the DUT memory.
    """
    for i in range(32):
        # CORREÇÃO: Usar 'mem_array' em vez de 'mem_array' conforme risc_test.v
        dut.memory_inst.mem_array[i].value = 0

def load_manual_test(dut, mem_map):
    """Loads a specific dictionary of address->value into memory."""
    clear_memory(dut)
    for addr, val in mem_map.items():
        if addr < 32:
            # CORREÇÃO: Usar 'mem_array' em vez de 'mem_array'
            dut.memory_inst.mem_array[addr].value = val
        else:
            dut._log.error(f"Attempted to write to invalid address {addr}")

def load_program_string(dut, content):
    """Parses the simplified text content and loads it into memory."""
    clear_memory(dut)
    
    address = 0
    lines = content.strip().splitlines()
    
    for line in lines:
        clean_line = line.split('//')[0].strip()
        if not clean_line:
            continue
            
        if '@' in clean_line:
            parts = clean_line.split()
            for part in parts:
                if part.startswith('@'):
                    address = int(part.replace('@', ''), 16)
                    clean_line = clean_line.replace(part, '').strip()
                    break
        
        if not clean_line:
            continue

        bin_token = clean_line.split()[0]
        bin_clean = bin_token.replace('_', '')
        
        try:
            val = int(bin_clean, 2)
            if address < 32:
                # CORREÇÃO: Usar 'mem_array' em vez de 'mem_array'
                dut.memory_inst.mem_array[address].value = val
                address += 1
            else:
                raise IndexError(f"Program exceeded memory limit at address {address}")
        except ValueError:
            pass 

# ==============================================================================
# 4. MAIN TESTBENCH
# ==============================================================================

@cocotb.test()
async def risc_verification_suite(dut):
    """
    Complete RISC Processor Verification.
    Matches the logic of 'risc_test.v'.
    """
    
    clock = Clock(dut.clk, 2, unit="ns")
    cocotb.start_soon(clock.start())

    async def run_reset():
        dut.rst.value = 1
        await RisingEdge(dut.clk) 
        dut.rst.value = 0
        await RisingEdge(dut.clk)

    dut._log.info("-------------------------------------------")
    dut._log.info("STARTING MANUAL INSTRUCTION TESTS")
    dut._log.info("-------------------------------------------")

    for test in MANUAL_TESTS:
        name = test['name']
        cycles = test['cycles']
        
        dut._log.info(f"TEST: {name} | Duration: {cycles} cycles")
        
        load_manual_test(dut, test['mem'])
        
        await run_reset()
        
        # C. Run Simulation for 'cycles' count
        for _ in range(cycles):
            await RisingEdge(dut.clk)
            
        # D. Check Expect(0)
        # CORREÇÃO: Esperar um delta time (1ns) após a borda para ler o sinal estabilizado
        # Isso imita o #1 do Verilog antes do expect
        await Timer(1, units="ns")
        assert dut.halt.value == 0, f"{name} Failed: Halted too early (at cycle {cycles})"
        
        # E. Run 1 more cycle
        await RisingEdge(dut.clk)
        
        # F. Check Expect(1)
        await Timer(1, units="ns")
        assert dut.halt.value == 1, f"{name} Failed: Did not halt after {cycles}+1 cycles"
        
        dut._log.info(f"PASS: {name}")

    dut._log.info("-------------------------------------------")
    dut._log.info("STARTING FILE-BASED TESTS")
    dut._log.info("-------------------------------------------")

    file_order = ["CPUtest1", "CPUtest2", "CPUtest3"]
    
    for test_name in file_order:
        test_data = PROGRAM_FILES[test_name]
        cycles = test_data['cycles']
        content = test_data['content']
        
        dut._log.info(f"TEST: {test_name} | Duration: {cycles} cycles")
        
        load_program_string(dut, content)
        
        await run_reset()
        
        for _ in range(cycles):
            await RisingEdge(dut.clk)
            
        # Expect(0)
        await Timer(1, units="ns")
        assert dut.halt.value == 0, f"{test_name} Failed: Halted too early"
        
        # Expect(1)
        await RisingEdge(dut.clk)
        await Timer(1, units="ns")
        assert dut.halt.value == 1, f"{test_name} Failed: Did not halt on time"
        
        dut._log.info(f"PASS: {test_name}")

    dut._log.info("ALL TESTS PASSED SUCCESSFULLY.")

# ==============================================================================
# 5. RUNNER CONFIGURATION (MANTIDO INALTERADO)
# ==============================================================================

def test_risc_runner():
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent

    sources = [proj_path/"golden/risc_processor.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="risc",
        always=True,
        timescale=("1ns", "1ps")
    )

    runner.test(hdl_toplevel="risc", test_module="test_risc_processor_hidden")

if __name__ == "__main__":
    test_risc_runner()
