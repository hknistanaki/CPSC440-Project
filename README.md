# RISC-V Single-Cycle CPU Simulator

This project implements a complete 32bit RISC-V single cycle CPU simulator with RV32I instruction set. The simulator is a fully functional CPU with instruction decoding, control unit, ALU operations, memory access, and register file management.

## Usage Instructions

### Running a Program

To execute a program from a hex file:

```bash
python run_cpu.py prog.hex
```

For verbose output showing each cycle:

```bash
python run_cpu.py prog.hex verbose
```

### Running Tests

Run the test suite:

```bash
python tests/test_cpu.py
```

Run the base program test:

```bash
python tests/test_base_simple.py
```

### Hex File Format

Programs are stored in `.hex` files with the following format:
- One 32bit instruction per line
- Exactly 8 hexadecimal digits (no 0x prefix)
- Uppercase or lowercase both acceptable
- Blank lines are allowed and ignored
- No comments in .hex file

Example:
```
00500093
00A00113
002081B3
```

## Project Structure

### Core Components

- **`cpu.py`**: Main CPU that integrates all components and performs instruction execution
- **`instruction_decoder.py`**: Decode RISC-V instructions, extracts opcodes, registers, and immediates
- **`control_unit.py`**: Control signals for instruction execution
- **`memory.py`**: Instruction and data memory units with separate address spaces
- **`alu.py`**: Arithmetic Logic Unit supporting ADD, SUB, AND, OR, XOR operations
- **`shifter.py`**: Barrel shifter for shift operations
- **`registers.py`**: 32 register file implementation with read/write operations
- **`bit_utils.py`**: Bit manipulation utilities
- **`hex_loader.py`**: Loads programs from .hex files into instruction memory

### Test Files

- **`prog.hex`**: Base test program from specification
- **`tests/test_cpu.py`**: Full test suite covering all instruction types
- **`tests/test_base_simple.py`**: Simple test for base program
- **`run_cpu.py`**: Main program runner
- **`tests/test_programs.py`**: Test program utilities and helpers

### Additional Components

- **`fpu_f32.py`**: Floating Point Unit (32 bit) implementation
- **`mdu.py`**: Multiply/Divide Unit implementation
- **`twos_complement.py`**: Two's complement utilities
- **`test_suite.py`**: Additional test suite for testing

## Supported Instruction Set

### Arithmetic Instructions
- **`ADD`**: Add two registers (rd = rs1 + rs2)
- **`SUB`**: Subtract two registers (rd = rs1 - rs2)
- **`ADDI`**: Add immediate to register (rd = rs1 + imm)

### Logical Instructions
- **`AND`**: Bitwise AND (rd = rs1 & rs2)
- **`OR`**: Bitwise OR (rd = rs1 | rs2)
- **`XOR`**: Bitwise XOR (rd = rs1 ^ rs2)
- **`ANDI`**: AND immediate (rd = rs1 & imm)
- **`ORI`**: OR immediate (rd = rs1 | imm)
- **`XORI`**: XOR immediate (rd = rs1 ^ imm)

### Shift Instructions
- **`SLL`**: Shift left logical (rd = rs1 << rs2[4:0])
- **`SRL`**: Shift right logical (rd = rs1 >> rs2[4:0])
- **`SRA`**: Shift right arithmetic (rd = rs1 >>> rs2[4:0])
- **`SLLI`**: Shift left logical immediate (rd = rs1 << imm[4:0])
- **`SRLI`**: Shift right logical immediate (rd = rs1 >> imm[4:0])
- **`SRAI`**: Shift right arithmetic immediate (rd = rs1 >>> imm[4:0])

### Memory Instructions
- **`LW`**: Load word (rd = mem[rs1 + imm])
- **`SW`**: Store word (mem[rs1 + imm] = rs2)

### Control Flow Instructions
- **`BEQ`**: Branch if equal (if rs1 == rs2, PC = PC + imm)
- **`BNE`**: Branch if not equal (if rs1 != rs2, PC = PC + imm)
- **`JAL`**: Jump and link (rd = PC + 4, PC = PC + imm)
- **`JALR`**: Jump and link register (rd = PC + 4, PC = (rs1 + imm) & 0xFFFFFFFE)

### Immediate/Utility Instructions
- **`LUI`**: Load upper immediate (rd = imm << 12)
- **`AUIPC`**: Add upper immediate to PC (rd = PC + (imm << 12))

## Datapath and Control Description

### Single-Cycle Datapath

The CPU implements a single cycle RISC-V datapath with the following stages:

1. **Instruction Fetch**
   - Program Counter points to current instruction
   - Instruction Memory reads 32 bit instruction at PC address
   - PC increments by 4 for next instruction (unless branch/jump)

2. **Instruction Decode**
   - Instruction Decoder extracts:
     - Opcode (bits 0-6)
     - Register fields: rd (bits 7-11), rs1 (bits 12-16), rs2 (bits 17-21)
     - Function codes: funct3 (bits 12-14), funct7 (bits 25-31)
     - Immediate values: I-type, S-type, B-type, U-type, J-type
   - All immediates are sign-extended to 32 bits

3. **Register Read**
   - Register File reads two source registers (rs1, rs2)
   - Register x0 is hard-wired to zero (always returns 0)

4. **Control Unit**
   - Generates control signals based on instruction type:
     - **RegWrite**: Enable register writeback
     - **MemRead**: Enable memory read
     - **MemWrite**: Enable memory write
     - **MemToReg**: Select memory data vs ALU result for writeback
     - **ALUSrc**: Select immediate vs rs2 for ALU input B
     - **Branch**: Enable branch condition checking
     - **Jump**: Enable jump instruction
     - **ALUOp**: ALU operation (ADD, SUB, AND, OR, XOR, LUI)
     - **ImmType**: Immediate type (I, S, B, U, J, R)
     - **UseShift**: Use shifter instead of ALU
     - **ShiftOp**: Shift operation (SLL, SRL, SRA)

5. **Execute**
   - **ALU Operations**: ADD, SUB, AND, OR, XOR performed by ALU
   - **Shift Operations**: SLL, SRL, SRA performed by barrel shifter
   - **Address Calculation**: For load/store, ALU computes rs1 + imm
   - **LUI**: Directly uses sign-extended immediate (no ALU operation)

6. **Memory Access**
   - **Load (LW)**: Data Memory reads word at computed address
   - **Store (SW)**: Data Memory writes rs2 to computed address
   - All memory accesses must be word-aligned (4-byte boundaries)

7. **Writeback**
   - Result selection:
     - **MemToReg = 1**: Memory data (for load instructions)
     - **MemToReg = 0**: ALU/shifter result (for arithmetic/logical)
     - **Jump instructions**: PC + 4 (return address)
   - Write to register file if RegWrite = 1 and rd ≠ 0

8. **PC Update**
   - **Normal**: PC = PC + 4
   - **Branch taken**: PC = PC + sign-extended immediate
   - **JAL**: PC = PC + sign-extended immediate
   - **JALR**: PC = (rs1 + sign-extended immediate) & 0xFFFFFFFE

### Control Flow

The Control Unit contains a combinational logic that generates control signals based on:
- Instruction opcode
- Function codes (funct3, funct7)
- Instruction name (decoded from opcode and function codes)

Control signals are generated for each instruction type:
- **R-type** (ADD, SUB, AND, OR, XOR, shifts): RegWrite=1, ALUSrc=0
- **I-type** (ADDI, ANDI, ORI, XORI, shifts, LW, JALR): RegWrite=1 (except stores), ALUSrc=1
- **S-type** (SW): MemWrite=1, ALUSrc=1
- **B-type** (BEQ, BNE): Branch=1, ALUSrc=0
- **U-type** (LUI, AUIPC): RegWrite=1, ALUSrc=1
- **J-type** (JAL): RegWrite=1, Jump=1

### Memory Layout

- **Instruction Memory**: Base address `0x00000000`
  - Stores program instructions
  - Read-only during execution
  - Size: 1024 words (4KB)

- **Data Memory**: Base address `0x00010000`
  - Stores data for load/store operations
  - Read/write during execution
  - Size: 1024 words (4KB)

## Additional Features

### Halt Detection
- CPU halts on `JAL x0, 0` instruction (infinite loop)
- CPU halts on invalid memory access
- CPU halts on reaching maximum cycle limit (default: 1000)

### Register x0
- Register x0 is hardwired to zero
- Writes to x0 are ignored
- Always reads as zero regardless of write attempts

### Sign Extension
- All immediate values are sign-extended to 32 bits
- Supports negative immediate values correctly
- B-type and J-type immediates have special encoding (LSB is always 0)

### Error Handling
- Memory access errors are caught and reported
- Invalid instruction addresses halt execution
- Maximum cycle limit prevents infinite loops

### State Inspection
- `get_state()` method provides complete CPU state:
  - Program counter
  - Register file contents
  - Data memory contents
  - Cycle and instruction counts
  - Halt status

## AI Usage Notice

AI was used to help write the Project Structure, Supported Instruction Set, Datapath and Control Descriptions, and Additional Features parts of this README.md, along with helping write some parts of run_tests.py, test_alu.py, and test_fpu_f32.py. Calculated AI percentage is 4% of whole project.

## Test Output Showing Behavior

### Base Program Test (prog.hex)

The base program implements the following assembly:

```assembly
addi x1, x0, 5      # x1 = 5
addi x2, x0, 10     # x2 = 10
add x3, x1, x2      # x3 = 15
sub x4, x2, x1      # x4 = 5
lui x5, 0x00010     # x5 = 0x00010000 (data base)
sw x3, 0(x5)        # mem[0x00010000] = 15
lw x4, 0(x5)        # x4 = 15
beq x3, x4, label1  # branch forward by 8 bytes
addi x6, x0, 1      # skipped if branch taken
label1:
addi x6, x0, 2      # x6 = 2
jal x0, 0           # halt: infinite loop
```

**Expected Output:**

```
Loading program from prog.hex...
Loaded 11 instructions

Starting execution...
Initial PC: 0x0

============================================================
Execution Complete
============================================================
Cycles executed: 11
Instructions executed: 11
Halted: True
Final PC: 0x2c

============================================================
Final Register State (non-zero registers)
============================================================
  x0: 0x00000000 (0)
  x1: 0x00000005 (5)
  x2: 0x0000000a (10)
  x3: 0x0000000f (15)
  x4: 0x0000000f (15)
  x5: 0x00010000 (65536)
  x6: 0x00000002 (2)

============================================================
Data Memory (non-zero words)
============================================================
  0x00010000: 0x0000000f
```

**Verification:**
- x1 = 5 (ADDI instruction)
- x2 = 10 (ADDI instruction)
- x3 = 15 (ADD: 5 + 10)
- x4 = 15 (loaded from memory, overwriting previous value of 5)
- x5 = 0x00010000 (LUI instruction)
- x6 = 2 (branch taken, skipped the x6 = 1 instruction)
- Memory[0x00010000] = 15 (SW instruction stored value)
- CPU halted correctly on JAL x0, 0

### Test Suite Results

The comprehensive test suite (`test_cpu.py`) validates:

1. **Arithmetic Operations**: ADD, SUB, ADDI with various operands
2. **Logical Operations**: AND, OR, XOR and immediate variants
3. **Shift Operations**: SLL, SRL, SRA and immediate variants
4. **Memory Operations**: LW and SW with address calculation
5. **Branch Operations**: BEQ, BNE with forward and backward branches
6. **Jump Operations**: JAL, JALR with return address handling
7. **Immediate Instructions**: LUI, AUIPC
8. **Edge Cases**: Maximum/minimum values, zero operations, register x0 behavior

All tests pass, confirming correct CPU behavior across the entire instruction set.

## Notes

- Register x0 is hard-wired to zero and cannot be modified
- All memory accesses must be word-aligned (addresses divisible by 4)
- The CPU halts on `JAL x0, 0` instruction (used as halt mechanism)
- Maximum cycle limit (1000) prevents infinite loops from hanging the simulator
- Instruction and data memories have separate address spaces
- All operations use 32-bit two's complement arithmetic

