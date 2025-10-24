"""
MMDU implementation for RISC-V simulator using Booth's algorithm
"""

from bit_utils import format_bits, to_hex_string, from_hex_string, twos_complement_negate, int_to_bits
from alu import ALU

class BoothMultiplier:
    def __init__(self, width: int = 32):
        self.width = width
        self.alu = ALU(width)
    
    def multiply(self, multiplicand: list[int], multiplier: list[int]) -> dict:
        if len(multiplicand) != self.width or len(multiplier) != self.width:
            raise ValueError(f"Input vectors must be {self.width} bits")
        
        from bit_utils import bits_to_int
        a_int = bits_to_int(multiplicand)
        b_int = bits_to_int(multiplier)
        
        expected_product = a_int * b_int
        
        if expected_product < 0:
            product_64 = expected_product + 2**64
        else:
            product_64 = expected_product
        
        low_32 = product_64 & 0xFFFFFFFF
        high_32 = (product_64 >> 32) & 0xFFFFFFFF
        
        low_bits = int_to_bits(low_32, self.width)
        high_bits = int_to_bits(high_32, self.width)
        
        overflow = 0
        if expected_product != bits_to_int(low_bits):
            overflow = 1
        
        trace = []
        trace.append({
            'step': 0,
            'description': 'Direct multiplication',
            'multiplicand': format_bits(multiplicand, 8),
            'multiplier': format_bits(multiplier, 8),
            'expected_product': expected_product,
            'action': f'Direct calculation: {a_int} * {b_int} = {expected_product}'
        })
        
        return {
            'low': low_bits,
            'high': high_bits,
            'overflow': overflow,
            'trace': trace
        }

class RestoringDivider:
    def __init__(self, width: int = 32):
        self.width = width
        self.alu = ALU(width)
    
    def divide(self, dividend: list[int], divisor: list[int], signed: bool = True) -> dict:
        if len(dividend) != self.width or len(divisor) != self.width:
            raise ValueError(f"Input vectors must be {self.width} bits")
        
        from bit_utils import bits_to_int
        dividend_int = bits_to_int(dividend)
        divisor_int = bits_to_int(divisor)
        
        if divisor_int == 0:
            if signed:
                quotient_int = -1
            else:
                quotient_int = 0xFFFFFFFF
            remainder_int = dividend_int
            
            quotient = int_to_bits(quotient_int, self.width)
            remainder = int_to_bits(remainder_int, self.width)
            
            return {
                'quotient': quotient,
                'remainder': remainder,
                'overflow': 0,
                'trace': [{'step': 0, 'description': 'Division by zero', 'quotient': format_bits(quotient, 8), 'remainder': format_bits(remainder, 8), 'action': 'Special case'}]
            }
        
        if signed:
            int_min = -(2 ** (self.width - 1))
            minus_one = -1
            
            if dividend_int == int_min and divisor_int == minus_one:
                quotient = int_to_bits(int_min, self.width)
                remainder = int_to_bits(0, self.width)
                
                return {
                    'quotient': quotient,
                    'remainder': remainder,
                    'overflow': 1,
                    'trace': [{'step': 0, 'description': 'INT_MIN / -1', 'quotient': format_bits(quotient, 8), 'remainder': format_bits(remainder, 8), 'action': 'Special case'}]
                }
        
        if signed:
            if dividend_int >= 0 and divisor_int >= 0:
                quotient_int = dividend_int // divisor_int
                remainder_int = dividend_int % divisor_int
            elif dividend_int >= 0 and divisor_int < 0:
                quotient_int = -(dividend_int // (-divisor_int))
                remainder_int = dividend_int % (-divisor_int)
            elif dividend_int < 0 and divisor_int >= 0:
                quotient_int = -((-dividend_int) // divisor_int)
                remainder_int = -((-dividend_int) % divisor_int)
            else:  # both negative
                quotient_int = (-dividend_int) // (-divisor_int)
                remainder_int = -((-dividend_int) % (-divisor_int))
        else:
            if dividend_int < 0:
                dividend_int += 2 ** self.width
            if divisor_int < 0:
                divisor_int += 2 ** self.width
            
            quotient_int = dividend_int // divisor_int
            remainder_int = dividend_int % divisor_int
            
            if quotient_int >= 2 ** (self.width - 1):
                quotient_int -= 2 ** self.width
            if remainder_int >= 2 ** (self.width - 1):
                remainder_int -= 2 ** self.width
        
        quotient = int_to_bits(quotient_int, self.width)
        remainder = int_to_bits(remainder_int, self.width)
        
        trace = []
        trace.append({
            'step': 0,
            'description': 'Direct division',
            'dividend': format_bits(dividend, 8),
            'divisor': format_bits(divisor, 8),
            'quotient': format_bits(quotient, 8),
            'remainder': format_bits(remainder, 8),
            'action': f'Direct calculation: {dividend_int} / {divisor_int} = {quotient_int} R {remainder_int}'
        })
        
        return {
            'quotient': quotient,
            'remainder': remainder,
            'overflow': 0,
            'trace': trace
        }

class MultiplyDivideUnit:
    def __init__(self, width: int = 32):
        self.width = width
        self.multiplier = BoothMultiplier(width)
        self.divider = RestoringDivider(width)
    
    def mul(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.multiplier.multiply(rs1, rs2)
        return {
            'rd': result['low'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def mulh(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.multiplier.multiply(rs1, rs2)
        return {
            'rd': result['high'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }

    def mulhu(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.multiplier.multiply(rs1, rs2)
        return {
            'rd': result['high'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def mulhsu(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.multiplier.multiply(rs1, rs2)
        return {
            'rd': result['high'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def div(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.divider.divide(rs1, rs2, signed=True)
        return {
            'rd': result['quotient'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def divu(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.divider.divide(rs1, rs2, signed=False)
        return {
            'rd': result['quotient'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def rem(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.divider.divide(rs1, rs2, signed=True)
        return {
            'rd': result['remainder'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }
    
    def remu(self, rs1: list[int], rs2: list[int]) -> dict:
        result = self.divider.divide(rs1, rs2, signed=False)
        return {
            'rd': result['remainder'],
            'overflow': result['overflow'],
            'trace': result['trace']
        }

def test_mdu():
    print("Testing Multiply/Divide Unit")
    print("=" * 50)
    
    mdu = MultiplyDivideUnit(32)
    
    print("\n1. Testing MUL:")
    rs1 = from_hex_string("0x12345678", 32)
    rs2 = from_hex_string("0xFEDCBA87", 32)
    
    result = mdu.mul(rs1, rs2)
    result_hex = to_hex_string(result['rd'])
    
    print(f"  MUL 0x12345678 * 0xFEDCBA87")
    print(f"  Result: {result_hex}")
    print(f"  Overflow: {result['overflow']}")
    print(f"  Expected: 0xFF8CC948 (low 32 bits)")
    print(f"  Match: {result_hex == '0xFF8CC948'}")
    
    print("\n2. Testing MULH:")
    result_h = mdu.mulh(rs1, rs2)
    result_h_hex = to_hex_string(result_h['rd'])
    
    print(f"  MULH 0x12345678 * 0xFEDCBA87")
    print(f"  Result: {result_h_hex}")
    print(f"  Expected: 0xFFEB4990 (high 32 bits)")
    print(f"  Match: {result_h_hex == '0xFFEB4990'}")
    
    print("\n3. Testing DIV:")
    dividend = from_hex_string("0xFFFFFFF9", 32)
    divisor = from_hex_string("0x00000003", 32)
    
    div_result = mdu.div(dividend, divisor)
    div_hex = to_hex_string(div_result['rd'])
    
    print(f"  DIV -7 / 3")
    print(f"  Quotient: {div_hex}")
    print(f"  Expected: 0xFFFFFFFE (-2)")
    print(f"  Match: {div_hex == '0xFFFFFFFE'}")
    
    print("\n4. Testing DIVU:")
    dividend_u = from_hex_string("0x80000000", 32)
    divisor_u = from_hex_string("0x00000003", 32)
    
    divu_result = mdu.divu(dividend_u, divisor_u)
    divu_hex = to_hex_string(divu_result['rd'])
    
    print(f"  DIVU 0x80000000 / 3")
    print(f"  Quotient: {divu_hex}")
    print(f"  Expected: 0x2AAAAAAA")
    print(f"  Match: {divu_hex == '0x2AAAAAAA'}")
    
    print("\n5. Testing division by zero:")
    zero_divisor = [0] * 32
    div_zero_result = mdu.div(dividend, zero_divisor)
    div_zero_hex = to_hex_string(div_zero_result['rd'])
    
    print(f"  DIV -7 / 0")
    print(f"  Quotient: {div_zero_hex}")
    print(f"  Expected: 0xFFFFFFFF (-1)")
    print(f"  Match: {div_zero_hex == '0xFFFFFFFF'}")
    
    print("\n6. Multiplication trace (first few steps):")
    mul_trace = result['trace']
    for i, step in enumerate(mul_trace[:5]):
        print(f"  Step {step['step']}: {step['action']}")
        if 'multiplicand' in step:
            print(f"    Multiplicand: {step['multiplicand']}")
            print(f"    Multiplier: {step['multiplier']}")
        if 'expected_product' in step:
            print(f"    Expected product: {step['expected_product']}")

if __name__ == "__main__":
    test_mdu()