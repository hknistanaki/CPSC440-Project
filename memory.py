"""
Memory units for RISC-V CPU simulator
"""

from bit_utils import bits_to_int, int_to_bits, to_hex_string, from_hex_string

class InstructionMemory:
    def __init__(self, size: int = 1024, base_address: int = 0x00000000):
        self.size = size
        self.base_address = base_address
        self.memory = {}
    
    def load_program(self, instructions: list[list[int]], start_address: int = None):
        if start_address is None:
            start_address = self.base_address
        
        for i, instr in enumerate(instructions):
            addr = start_address + (i * 4)
            if addr < self.base_address or addr >= self.base_address + self.size:
                raise ValueError(f"Address {hex(addr)} out of bounds")
            self.memory[addr] = instr
    
    def read(self, address: int) -> list[int]:
        if address % 4 != 0:
            raise ValueError(f"Unaligned instruction fetch at address {hex(address)}")
        
        if address in self.memory:
            return self.memory[address][:]
        else:
            return [0] * 32
    
    def get_size(self) -> int:
        return self.size
    
    def get_base_address(self) -> int:
        return self.base_address

class DataMemory:
    def __init__(self, size: int = 1024, base_address: int = 0x00010000):
        self.size = size
        self.base_address = base_address
        self.memory = {}
    
    def read_word(self, address: int) -> list[int]:
        if address % 4 != 0:
            raise ValueError(f"Unaligned word read at address {hex(address)}")
        
        if address < self.base_address or address >= self.base_address + self.size:
            raise ValueError(f"Address {hex(address)} out of bounds")
        
        if address in self.memory:
            return self.memory[address][:]
        else:
            return [0] * 32
    
    def write_word(self, address: int, data: list[int]):
        if len(data) != 32:
            raise ValueError(f"Data must be 32 bits, got {len(data)}")
        
        if address % 4 != 0:
            raise ValueError(f"Unaligned word write at address {hex(address)}")
        
        if address < self.base_address or address >= self.base_address + self.size:
            raise ValueError(f"Address {hex(address)} out of bounds")
        
        self.memory[address] = data[:]
    
    def read_byte(self, address: int) -> list[int]:
        word_addr = (address // 4) * 4
        byte_offset = address % 4
        
        word = self.read_word(word_addr)
        byte_bits = word[24 - byte_offset * 8:32 - byte_offset * 8]
        
        return [0] * 24 + byte_bits
    
    def write_byte(self, address: int, data: list[int]):
        if len(data) != 8:
            raise ValueError(f"Data must be 8 bits, got {len(data)}")
        
        word_addr = (address // 4) * 4
        byte_offset = address % 4
        
        word = self.read_word(word_addr)
        word[24 - byte_offset * 8:32 - byte_offset * 8] = data
        
        self.write_word(word_addr, word)
    
    def get_size(self) -> int:
        return self.size
    
    def get_base_address(self) -> int:
        return self.base_address
    
    def dump_memory(self, start_addr: int = None, end_addr: int = None) -> dict:
        if start_addr is None:
            start_addr = self.base_address
        if end_addr is None:
            end_addr = self.base_address + self.size
        
        dump = {}
        for addr in range(start_addr, end_addr, 4):
            if addr in self.memory:
                dump[hex(addr)] = to_hex_string(self.memory[addr])
        
        return dump

