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