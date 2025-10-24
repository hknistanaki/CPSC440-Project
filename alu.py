"""
ALU implementation for RISC-V simulator.
"""

from bit_utils import format_bits, bits_to_int, int_to_bits

class FullAdder:
    @staticmethod
    def add(a: int, b: int, carry_in: int) -> tuple[int, int]:
        sum_bit = a ^ b ^ carry_in
        carry_out = (a & b) | (carry_in & (a ^ b))
        
        return sum_bit, carry_out

class RippleCarryAdder:
    def __init__(self, width: int = 32):
        self.width = width
    
    def add(self, a: list[int], b: list[int], carry_in: int = 0) -> tuple[list[int], int]:
        if len(a) != self.width or len(b) != self.width:
            raise ValueError(f"Input vectors must be {self.width} bits")
        
        sum_bits = []
        carry = carry_in
        
        for i in range(self.width - 1, -1, -1):
            sum_bit, carry = FullAdder.add(a[i], b[i], carry)
            sum_bits.insert(0, sum_bit)
        
        return sum_bits, carry
    
    def subtract(self, a: list[int], b: list[int]) -> tuple[list[int], int]:
        b_neg = [1 - bit for bit in b]
        
        carry = 1
        for i in range(self.width - 1, -1, -1):
            sum_bit, carry = FullAdder.add(b_neg[i], 0, carry)
            b_neg[i] = sum_bit
            if carry == 0:
                break
        
        return self.add(a, b_neg, 0)

class ALU:
    def __init__(self, width: int = 32):
        self.width = width
        self.adder = RippleCarryAdder(width)
    
    def add(self, a: list[int], b: list[int]) -> dict:
        if len(a) != self.width or len(b) != self.width:
            raise ValueError(f"Input vectors must be {self.width} bits")
        
        result, carry_out = self.adder.add(a, b, 0)
        
        flags = self._generate_flags(a, b, result, carry_out, is_subtraction=False)
        
        return {
            'result': result,
            'N': flags['N'],
            'Z': flags['Z'],
            'C': flags['C'],
            'V': flags['V']
        }
    
    def sub(self, a: list[int], b: list[int]) -> dict:
        if len(a) != self.width or len(b) != self.width:
            raise ValueError(f"Input vectors must be {self.width} bits")
        
        result, carry_out = self.adder.subtract(a, b)
        
        # Generate flags
        flags = self._generate_flags(a, b, result, carry_out, is_subtraction=True)
        
        return {
            'result': result,
            'N': flags['N'],
            'Z': flags['Z'],
            'C': flags['C'],
            'V': flags['V']
        }
