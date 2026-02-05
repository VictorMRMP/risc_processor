# Risc Processor (Verilog)

This project is the implementation of a simple RISC processor in Verilog. The design includes all the essential components of a CPU, such as an Arithmetic Logic Unit (ALU), a Control Unit (FSM), registers, and memory.

## Architecture Overview

The processor is built from the following Verilog modules which are instantiated in a top module risc:

* **`controller`**: The Control Unit. This is the processor's brain, implemented as a Finite State Machine (FSM). It receives the instruction `opcode`, the current `phase` (clock cycle state), and the `zero` flag from the ALU. Based on these inputs, it generates all necessary control signals for the datapath, such as `rd` (read), `wr` (write), `ld_pc` (load PC), `ld_ac` (load accumulator), and `halt`.
* **`alu`**: The Arithmetic Logic Unit. This unit performs mathematical and logical operations. It implements `ADD`, `AND`, and `XOR`. It also outputs a `a_is_zero` flag, which is used by the controller for conditional instructions.
* **`memory`**: A synchronous RAM module. It is used to store both the program instructions and the data it manipulates.
* **`counter`**: A generic counter module. This is used as the **Program Counter (PC)**, responsible for pointing to the address of the next instruction to be executed. It supports `load` (for jumps), `enab` (for incrementing), and `rst` (reset).
* **`multiplexor`**: A standard 2-to-1 multiplexer, used for selecting data sources within the datapath.
* **`driver`**: A tri-state driver. This is essential for managing the shared `data` bus, allowing multiple components (like the ALU and memory) to write to the bus without conflict.
* **`register`**: A generic, synchronous register module with a parameterizable width (defaulting to 8 bits). It features a load enable signal and a synchronous rst.

## Implemented Instruction Set

Based on the controller logic and test programs, the processor implements the following 8 instructions:

| Instruction | Opcode (bin) | Description |
| :--- | :--- | :--- |
| **HLT** | `000` | Halts the processor's execution. |
| **SKZ** | `001` | Skips the next instruction if the accumulator is zero. |
| **ADD** | `010` | Adds the value from memory to the accumulator. |
| **AND** | `011` | Performs a bitwise AND between the accumulator and a value from memory. |
| **XOR** | `100` | Performs a bitwise XOR between the accumulator and a value from memory. |
| **LDA** | `101` | Loads a value from memory into the accumulator. |
| **STO** | `110` | Stores the value from the accumulator into memory. |
| **JMP** | `111` | Jumps to a specific memory address. |

## Evaluating Results

The prompt used was: 
""Implement a structural 8-bit RISC processor (top module risc) with AWIDTH=5 and DWIDTH=8 by instantiating the following modules using an inst suffix: a 3-bit phase counter , a controller , a 5-bit counter as the PC , an address multiplexor , a 32x8-bit memory which array is called mem_array, an instruction register , an alu , an accumulator register , and a tri-state driver. The architecture utilizes an 8-bit instruction split into a 3-bit opcode and 5-bit address , driven by an 8-phase control cycle (phases 0-7) to support operations including HLT, SKZ, JMP, LDA, STO, ADD, AND, and XOR. The system must feature a bidirectional data bus , a zero flag feedback loop from the ALU to the controller , and parameterizable widths for all hardware components.The instruction opcode mapping must be strictly: HLT=0, SKZ=1, ADD=2, AND=3, XOR=4, LDA=5, STO=6, JMP=7. The RISC controller prioritize cycle-accuracy over performance.Crucially, the controller must strictly adhere to the following cycle-accurate timing to match the verification model: Instruction Fetch occurs in Phase 0; Latch IR and Increment PC occur in Phase 1. Execution must be delayed as follows: The 'halt' signal (HLT) and conditional skips (SKZ) must assert specifically in Phase 4. ALU results must latch into the Accumulator (LDA, ADD, AND, XOR) in Phase 5. Memory writes (STO) must occur in Phase 6."

![Evaluation test cases](img/ResultsRiscProcessor.png) 

[Evaluation link](https://www.hud.ai/jobs/c62c1afd-39cf-437c-bdca-0e67a824c2dc)

## Agent Failure Analysis
[Trace described](https://www.hud.ai/trace/08fb00b3-02f5-43fa-8a87-efe7deb3239e)

**A. Symptoms:** The HLT Instruction test failed with the error "Halted too early" verified in the testbench. The processor asserted the halt signal at the end of cycle 2, but the testbench expected the signal to remain low until cycle 4.

**B. Root cause:** The model's controller executed instructions immediately upon decoding, in contrast with the legacy RISC developed for the golden model. In the generated code, the HLT operation triggers in Phase 2 (the first execution phase). However, the the golden model uses a fixed control matrix that explicitly delays the halt signal assertion until Phase 4. This cycle mismatch caused the cycle-accurate assertion to fail. The cases that passed the test designed a RISC that prioritized cycle-accuracy over performance, such as described in the prompt.

**C. QA:** The agent generated a valid, but failed because didn't prioritized cycle-accuracy over performance specified in the prompt.

**D. Faulty assumptions / missed insights:** Flawed reasoning: The model assumed a standard, efficient FSM implementation where instructions execute as soon as operands are available. It missed the insight that this specific architecture requires "dummy cycles" or fixed-phase micro-operations, delaying execution to match a rigid control table rather than optimizing for speed.

