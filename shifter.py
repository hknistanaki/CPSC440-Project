"""
Barrel Shifter implementation for RISC-V simulator
"""

from bit_utils import format_bits

class BarrelShifter:
    def __init__(self, width: int = 32):
        self.width = width
    
    def shift_left_logical(self, data: list[int], shift_amount: int) -> list[int]:
        if len(data) != self.width:
            raise ValueError(f"Input vector must be {self.width} bits")
        
        if shift_amount >= self.width:
            return [0] * self.width
        
        if shift_amount <= 0:
            return data[:]
        
        result = data[shift_amount:] + [0] * shift_amount
        return result
    
    def shift_right_logical(self, data: list[int], shift_amount: int) -> list[int]:
        if len(data) != self.width:
            raise ValueError(f"Input vector must be {self.width} bits")
        
        if shift_amount >= self.width:
            return [0] * self.width
        
        if shift_amount <= 0:
            return data[:]
        
        result = [0] * shift_amount + data[:-shift_amount]
        return result
    
    def shift_right_arithmetic(self, data: list[int], shift_amount: int) -> list[int]:
        if len(data) != self.width:
            raise ValueError(f"Input vector must be {self.width} bits")
        
        if shift_amount >= self.width:
            sign_bit = data[0]
            return [sign_bit] * self.width
        
        if shift_amount <= 0:
            return data[:]
        
        sign_bit = data[0]
        result = [sign_bit] * shift_amount + data[:-shift_amount]
        return result
    
    def shift(self, data: list[int], shift_amount: int, operation: str) -> list[int]:
        if operation == 'SLL':
            return self.shift_left_logical(data, shift_amount)
        elif operation == 'SRL':
            return self.shift_right_logical(data, shift_amount)
        elif operation == 'SRA':
            return self.shift_right_arithmetic(data, shift_amount)
        else:
            raise ValueError(f"Unsupported shift operation: {operation}")

class Shifter:
    def __init__(self, width: int = 32):
        self.width = width
        self.barrel_shifter = BarrelShifter(width)
    
    def execute(self, data: list[int], shift_amount_bits: list[int], operation: str) -> list[int]:
        shift_amount = 0
        for i, bit in enumerate(shift_amount_bits):
            shift_amount += bit * (2 ** (len(shift_amount_bits) - 1 - i))
        
        shift_amount = shift_amount & 0x1F
        
        return self.barrel_shifter.shift(data, shift_amount, operation)