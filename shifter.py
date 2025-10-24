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

def test_shifter():

    print("Testing Shifter Implementation")
    print("=" * 50)
    
    shifter = Shifter(8)
    
    test_cases = [
        ("0x81", 1, "SLL", "0x02", "Left shift 0x81 by 1"),
        ("0x81", 2, "SLL", "0x04", "Left shift 0x81 by 2"),
        ("0x81", 7, "SLL", "0x80", "Left shift 0x81 by 7"),
        ("0x81", 8, "SLL", "0x00", "Left shift 0x81 by 8 (overflow)"),
        ("0x81", 1, "SRL", "0x40", "Right logical shift 0x81 by 1"),
        ("0x81", 2, "SRL", "0x20", "Right logical shift 0x81 by 2"),
        ("0x81", 7, "SRL", "0x01", "Right logical shift 0x81 by 7"),
        ("0x81", 8, "SRL", "0x00", "Right logical shift 0x81 by 8 (overflow)"),
        ("0x81", 1, "SRA", "0xC0", "Right arithmetic shift 0x81 by 1"),
        ("0x81", 2, "SRA", "0xE0", "Right arithmetic shift 0x81 by 2"),
        ("0x81", 7, "SRA", "0xFF", "Right arithmetic shift 0x81 by 7"),
        ("0x81", 8, "SRA", "0xFF", "Right arithmetic shift 0x81 by 8 (sign extend)"),
        ("0x7F", 1, "SRA", "0x3F", "Right arithmetic shift positive 0x7F by 1"),
    ]
    
    for data_hex, shift_amount, operation, expected_result_hex, description in test_cases:
        print(f"\n{description}")
        
        from bit_utils import from_hex_string, to_hex_string
        data_bits = from_hex_string(data_hex, 8)
        shift_amount_bits = [int(bit) for bit in format(shift_amount, '05b')]
        
        result = shifter.execute(data_bits, shift_amount_bits, operation)
        result_hex = to_hex_string(result)
        
        print(f"  Input:     {format_bits(data_bits, 4)} ({data_hex})")
        print(f"  Shift:     {shift_amount} positions {operation}")
        print(f"  Result:    {format_bits(result, 4)} ({result_hex})")
        print(f"  Expected:  {expected_result_hex}")
        print(f"  Match:     {result_hex == expected_result_hex}")
    
    print(f"\n{'='*50}")
    print("Testing 32-bit Shifter")
    print("=" * 50)
    
    shifter_32 = Shifter(32)
    
    data_32 = from_hex_string("0x12345678", 32)
    shift_amount_5 = [0, 0, 0, 0, 1]
    result_32 = shifter_32.execute(data_32, shift_amount_5, "SLL")
    result_32_hex = to_hex_string(result_32)
    
    print(f"32-bit SLL test:")
    print(f"  Input:     {format_bits(data_32, 8)} (0x12345678)")
    print(f"  Shift:     1 position SLL")
    print(f"  Result:    {format_bits(result_32, 8)} ({result_32_hex})")
    print(f"  Expected:  0x2468ACF0")
    print(f"  Match:     {result_32_hex == '0x2468ACF0'}")

if __name__ == "__main__":
    test_shifter()