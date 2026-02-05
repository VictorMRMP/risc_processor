# Risc Processor (Verilog)

This project is the implementation of a simple RISC processor in Verilog, developed as part of the "Verilog Language and Application" (VLA) academic course from Cadence. The design includes all the essential components of a CPU, such as an Arithmetic Logic Unit (ALU), a Control Unit (FSM), registers, and memory.

The repository also contains three diagnostic programs used to verify the processor's functionality. These tests range from basic instruction validation to running a complete algorithm to calculate the Fibonacci sequence.

## Architecture Overview

The processor is built from the following Verilog modules:

* **`controller.v`**: The Control Unit. This is the processor's brain, implemented as a Finite State Machine (FSM). It receives the instruction `opcode`, the current `phase` (clock cycle state), and the `zero` flag from the ALU. Based on these inputs, it generates all necessary control signals for the datapath, such as `rd` (read), `wr` (write), `ld_pc` (load PC), `ld_ac` (load accumulator), and `halt`.
* **`alu.v`**: The Arithmetic Logic Unit. This unit performs mathematical and logical operations. It implements `ADD`, `AND`, and `XOR`. It also outputs a `a_is_zero` flag, which is used by the controller for conditional instructions.
* **`memory.v`**: A synchronous RAM module. It is used to store both the program instructions and the data it manipulates.
* **`counter.v`**: A generic counter module. This is used as the **Program Counter (PC)**, responsible for pointing to the address of the next instruction to be executed. It supports `load` (for jumps), `enab` (for incrementing), and `rst` (reset).
* **`multiplexor.v`**: A standard 2-to-1 multiplexer, used for selecting data sources within the datapath.
* **`driver.v`**: A tri-state driver. This is essential for managing the shared `data` bus, allowing multiple components (like the ALU and memory) to write to the bus without conflict.

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
![Evaluation test cases](img/Results.png) 
## Agent Failure Analysis
**A. Symptoms:** The HLT Instruction test failed with the error "Halted too early" verified in the testbench. The processor asserted the halt signal at the end of cycle 2, but the testbench expected the signal to remain low until cycle 4.

**B. Root cause:** The model's controller executed instructions immediately upon decoding, in contrast with the legacy RISC developed for the golden model. In the generated code, the HLT operation triggers in Phase 2 (the first execution phase). However, the the golden model uses a fixed control matrix that explicitly delays the halt signal assertion until Phase 4. This cycle mismatch caused the cycle-accurate assertion to fail. The cases that passed the test designed a RISC that prioritized cycle-accuracy over performance, such as the golden model.

**C. QA:** The agent generated a valid, but failed because didn't prioritized cycle-accuracy over performance specified in the prompt.

**D. Faulty assumptions / missed insights:** Flawed reasoning: The model assumed a standard, efficient FSM implementation where instructions execute as soon as operands are available. It missed the insight that this specific architecture requires "dummy cycles" or fixed-phase micro-operations, delaying execution to match a rigid control table rather than optimizing for speed.

