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
        
        flags = self._generate_flags(a, b, result, carry_out, is_subtraction=True)
        
        return {
            'result': result,
            'N': flags['N'],
            'Z': flags['Z'],
            'C': flags['C'],
            'V': flags['V']
        }

def _generate_flags(self, a: list[int], b: list[int], result: list[int], 
                       carry_out: int, is_subtraction: bool) -> dict:
        N = result[0]
        
        Z = 1 if all(bit == 0 for bit in result) else 0
        
        C = carry_out
        
        if is_subtraction:
            V = 1 if (a[0] != b[0]) and (result[0] != a[0]) else 0
        else:
            V = 1 if (a[0] == b[0]) and (result[0] != a[0]) else 0
        
        return {'N': N, 'Z': Z, 'C': C, 'V': V}
    
def execute(self, a: list[int], b: list[int], op: str) -> dict:
    if op == 'ADD':
        return self.add(a, b)
    elif op == 'SUB':
        return self.sub(a, b)
    else:
        raise ValueError(f"Unsupported ALU operation: {op}")

def test_alu():
    print("Testing ALU Implementation")
    print("=" * 50)
    
    alu = ALU(32)
    
    test_cases = [
        ("0x7FFFFFFF", "0x00000001", "ADD", "0x80000000", {'N': 1, 'Z': 0, 'C': 0, 'V': 1}),
        ("0x80000000", "0x00000001", "SUB", "0x7FFFFFFF", {'N': 0, 'Z': 0, 'C': 1, 'V': 1}),
        ("0xFFFFFFFF", "0xFFFFFFFF", "ADD", "0xFFFFFFFE", {'N': 1, 'Z': 0, 'C': 1, 'V': 0}),
    ]
    
    for a_hex, b_hex, op, expected_result_hex, expected_flags in test_cases:
        print(f"\nTesting {op}: {a_hex} {op} {b_hex}")
        
        from bit_utils import from_hex_string
        a_bits = from_hex_string(a_hex, 32)
        b_bits = from_hex_string(b_hex, 32)
        
        result = alu.execute(a_bits, b_bits, op)
        
        from bit_utils import to_hex_string
        result_hex = to_hex_string(result['result'])
        
        print(f"  Operand A: {format_bits(a_bits, 8)} ({a_hex})")
        print(f"  Operand B: {format_bits(b_bits, 8)} ({b_hex})")
        print(f"  Result:    {format_bits(result['result'], 8)} ({result_hex})")
        print(f"  Flags: N={result['N']}, Z={result['Z']}, C={result['C']}, V={result['V']}")
        
        print(f"  Result match: {result_hex == expected_result_hex}")
        print(f"  Flags match: {all(result[k] == expected_flags[k] for k in expected_flags)}")
        
        print(f"  Flag meanings:")
        print(f"    N (Negative): {result['N']} - Result is negative")
        print(f"    Z (Zero): {result['Z']} - Result is zero")
        print(f"    C (Carry): {result['C']} - Carry out from MSB")
        print(f"    V (Overflow): {result['V']} - Signed overflow occurred")

if __name__ == "__main__":
    test_alu()

