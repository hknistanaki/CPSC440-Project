"""
Register and Register File implementation for RISC-V simulator.
"""

from bit_utils import int_to_bits, bits_to_int, format_bits

class Reg:
    
    def __init__(self, width: int = 32):
        self.width = width
        self.data = [0] * width
        self.load_enable = False
        self.clear_enable = False
    
    def load(self, data: list[int], enable: bool = True):
        self.load_enable = enable
        if enable and len(data) == self.width:
            self.data = data[:]
        elif enable:
            if len(data) < self.width:
                self.data = [0] * (self.width - len(data)) + data
            else:
                self.data = data[-self.width:]
    
    def clear(self, enable: bool = True):
        self.clear_enable = enable
        if enable:
            self.data = [0] * self.width
    
    def read(self) -> list[int]:
        return self.data[:]
    
    def clock_edge(self):
        if self.clear_enable:
            self.data = [0] * self.width
            self.clear_enable = False
        elif self.load_enable:
            self.load_enable = False
    
    def __str__(self) -> str:
        return f"Reg({self.width}): {format_bits(self.data)}"

class RegisterFile:
    def __init__(self, num_regs: int = 32, width: int = 32):
        self.num_regs = num_regs
        self.width = width
        self.registers = [Reg(width) for _ in range(num_regs)]
        
        for reg in self.registers:
            reg.data = [0] * width
    
    def read(self, addr: int) -> list[int]:
        if 0 <= addr < self.num_regs:
            return self.registers[addr].read()
        else:
            raise ValueError(f"Invalid register address: {addr}")
    
    def write(self, addr: int, data: list[int], enable: bool = True):
        if addr == 0:
            return
        
        if 0 <= addr < self.num_regs:
            self.registers[addr].load(data, enable)
        else:
            raise ValueError(f"Invalid register address: {addr}")
    
    def clock_edge(self):
        for reg in self.registers:
            reg.clock_edge()
    
    def get_register_names(self) -> list[str]:
        return [f"x{i}" for i in range(self.num_regs)]
    
    def dump_registers(self) -> dict:
        dump = {}
        for i, reg in enumerate(self.registers):
            dump[f"x{i}"] = reg.read()
        return dump
    
    def __str__(self) -> str:
        lines = ["Register File:"]
        for i, reg in enumerate(self.registers):
            lines.append(f"  x{i:2d}: {format_bits(reg.data)}")
        return "\n".join(lines)

class FPRegisterFile:
    def __init__(self, num_regs: int = 32, width: int = 32):
        self.num_regs = num_regs
        self.width = width
        self.registers = [Reg(width) for _ in range(num_regs)]
        
        for reg in self.registers:
            reg.data = [0] * width

    def read(self, addr: int) -> list[int]:
        if 0 <= addr < self.num_regs:
            return self.registers[addr].read()
        else:
            raise ValueError(f"Invalid FP register address: {addr}")
    
    def write(self, addr: int, data: list[int], enable: bool = True):
        if 0 <= addr < self.num_regs:
            self.registers[addr].load(data, enable)
        else:
            raise ValueError(f"Invalid FP register address: {addr}")
    
    def clock_edge(self):
        for reg in self.registers:
            reg.clock_edge()
    
    def get_register_names(self) -> list[str]:
        return [f"f{i}" for i in range(self.num_regs)]
    
    def dump_registers(self) -> dict:
        dump = {}
        for i, reg in enumerate(self.registers):
            dump[f"f{i}"] = reg.read()
        return dump
    
    def __str__(self) -> str:
        lines = ["FP Register File:"]
        for i, reg in enumerate(self.registers):
            lines.append(f"  f{i:2d}: {format_bits(reg.data)}")
        return "\n".join(lines)

def test_registers():
    print("Testing Register Components")
    print("=" * 50)
    
    print("\n1. Testing single register:")
    reg = Reg(8)
    print(f"Initial: {reg}")
    
    reg.load([1, 0, 1, 1, 0, 0, 1, 0])
    reg.clock_edge()
    print(f"After load: {reg}")
    
    reg.clear()
    reg.clock_edge()
    print(f"After clear: {reg}")
    
    print("\n2. Testing register file:")
    rf = RegisterFile(4, 8)  # 4 registers, 8 bits each
    print(f"Initial RF:\n{rf}")
    
    rf.write(1, [1, 1, 0, 0, 1, 1, 0, 0])
    rf.write(2, [0, 1, 1, 0, 0, 1, 1, 0])
    rf.write(3, [1, 0, 0, 1, 1, 0, 0, 1])
    rf.clock_edge()
    print(f"After writes:\n{rf}")
    
    print("\n3. Testing x0 hard-wired behavior:")
    rf.write(0, [1, 1, 1, 1, 1, 1, 1, 1])
    rf.clock_edge()
    print(f"After writing to x0:\n{rf}")
    print(f"x0 should still be zero: {rf.read(0) == [0, 0, 0, 0, 0, 0, 0, 0]}")
    
    print("\n4. Testing FP register file:")
    fprf = FPRegisterFile(4, 8)
    fprf.write(0, [1, 0, 1, 0, 1, 0, 1, 0])
    fprf.write(1, [0, 1, 0, 1, 0, 1, 0, 1])
    fprf.clock_edge()
    print(f"FP Register File:\n{fprf}")

if __name__ == "__main__":
    test_registers()

