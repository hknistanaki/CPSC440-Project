"""
Unit tests for Multiply/Divide
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mdu import MultiplyDivideUnit
from bit_utils import from_hex_string, to_hex_string, bits_to_int

class TestMDU(unittest.TestCase):

    def setUp(self):
        self.mdu = MultiplyDivideUnit(32)
        self.int_min = -(2 ** 31)
        self.int_max = (2 ** 31) - 1
    
    def test_mul_operations(self):
        test_cases = [
            ("0x12345678", "0xFEDCBA87", "0xFF8CC948", 1, "Large multiplication"),
            ("0x0000000D", "0x00000007", "0x0000005B", 0, "13 * 7 = 91"),
            ("0x00000002", "0x00000003", "0x00000006", 0, "2 * 3 = 6"),
            ("0xFFFFFFFF", "0x00000002", "0xFFFFFFFE", 0, "-1 * 2 = -2"),
        ]
        
        for rs1_hex, rs2_hex, expected_result_hex, expected_overflow, description in test_cases:
            with self.subTest(description=description):
                rs1_bits = from_hex_string(rs1_hex, 32)
                rs2_bits = from_hex_string(rs2_hex, 32)
                
                result = self.mdu.mul(rs1_bits, rs2_bits)
                result_hex = to_hex_string(result['rd'])
                
                self.assertEqual(result_hex, expected_result_hex,
                               f"Pattern mismatch for {description}")
                
                self.assertEqual(result['overflow'], expected_overflow,
                               f"Overflow mismatch for {description}")
                
                expected_decimal = bits_to_int(from_hex_string(expected_result_hex, 32))
                actual_decimal = bits_to_int(result['rd'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal mismatch for {description}")
    
    def test_mulh_operations(self):
        test_cases = [
            ("0x12345678", "0xFEDCBA87", "0xFFEB4990", "Large multiplication high bits"),
            ("0x0000000D", "0x00000007", "0x00000000", "Small multiplication high bits"),
        ]
        
        for rs1_hex, rs2_hex, expected_result_hex, description in test_cases:
            with self.subTest(description=description):
                rs1_bits = from_hex_string(rs1_hex, 32)
                rs2_bits = from_hex_string(rs2_hex, 32)
                
                result = self.mdu.mulh(rs1_bits, rs2_bits)
                result_hex = to_hex_string(result['rd'])
                
                self.assertEqual(result_hex, expected_result_hex,
                               f"Hex mismatch for {description}")
                
                expected_decimal = bits_to_int(from_hex_string(expected_result_hex, 32))
                actual_decimal = bits_to_int(result['rd'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal mismatch for {description}")
    
    def test_div_operations(self):
        test_cases = [
            ("0xFFFFFFF9", "0x00000003", "0xFFFFFFFE", "-7 / 3 = -2"),
            ("0x0000000D", "0x00000003", "0x00000004", "13 / 3 = 4"),
            ("0x0000000E", "0x00000003", "0x00000004", "14 / 3 = 4"),
            ("0xFFFFFFF9", "0xFFFFFFFD", "0x00000002", "-7 / -3 = 2"),
        ]
        
        for dividend_hex, divisor_hex, expected_quotient_hex, description in test_cases:
            with self.subTest(description=description):
                dividend_bits = from_hex_string(dividend_hex, 32)
                divisor_bits = from_hex_string(divisor_hex, 32)
                
                result = self.mdu.div(dividend_bits, divisor_bits)
                quotient_hex = to_hex_string(result['rd'])
                
                self.assertEqual(quotient_hex, expected_quotient_hex,
                               f"Hex mismatch for {description}")
                
                expected_decimal = bits_to_int(from_hex_string(expected_quotient_hex, 32))
                actual_decimal = bits_to_int(result['rd'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal mismatch for {description}")
    
    def test_divu_operations(self):
        test_cases = [
            ("0x80000000", "0x00000003", "0x2AAAAAAA", "0x80000000 / 3"),
            ("0x0000000D", "0x00000003", "0x00000004", "13 / 3 = 4"),
        ]
        
        for dividend_hex, divisor_hex, expected_quotient_hex, description in test_cases:
            with self.subTest(description=description):
                dividend_bits = from_hex_string(dividend_hex, 32)
                divisor_bits = from_hex_string(divisor_hex, 32)
                
                result = self.mdu.divu(dividend_bits, divisor_bits)
                quotient_hex = to_hex_string(result['rd'])
                
                self.assertEqual(quotient_hex, expected_quotient_hex,
                               f"Hex mismatch for {description}")
    
    def test_division_by_zero(self):
        dividend_bits = from_hex_string("0xFFFFFFF9", 32)
        zero_divisor = from_hex_string("0x00000000", 32)
        
        result = self.mdu.div(dividend_bits, zero_divisor)
        quotient_hex = to_hex_string(result['rd'])
        
        self.assertEqual(quotient_hex, "0xFFFFFFFF",
                        "DIV by zero should return -1")
        
        result = self.mdu.divu(dividend_bits, zero_divisor)
        quotient_hex = to_hex_string(result['rd'])
        
        self.assertEqual(quotient_hex, "0xFFFFFFFF",
                        "DIVU by zero should return 0xFFFFFFFF")
    
    def test_int_min_div_minus_one(self):
        int_min_bits = from_hex_string("0x80000000", 32)
        minus_one_bits = from_hex_string("0xFFFFFFFF", 32)
        
        result = self.mdu.div(int_min_bits, minus_one_bits)
        quotient_hex = to_hex_string(result['rd'])
        
        self.assertEqual(quotient_hex, "0x80000000",
                        "INT_MIN / -1 should return INT_MIN")
        self.assertEqual(result['overflow'], 1,
                        "INT_MIN / -1 should set overflow flag")
    
    def test_rem_operations(self):
        test_cases = [
            ("0xFFFFFFF9", "0x00000003", "0xFFFFFFFF", "-7 % 3 = -1"),
            ("0x0000000D", "0x00000003", "0x00000001", "13 % 3 = 1"),
            ("0x0000000E", "0x00000003", "0x00000002", "14 % 3 = 2"),
        ]
        
        for dividend_hex, divisor_hex, expected_remainder_hex, description in test_cases:
            with self.subTest(description=description):
                dividend_bits = from_hex_string(dividend_hex, 32)
                divisor_bits = from_hex_string(divisor_hex, 32)
                
                result = self.mdu.rem(dividend_bits, divisor_bits)
                remainder_hex = to_hex_string(result['rd'])
                
                self.assertEqual(remainder_hex, expected_remainder_hex,
                               f"Hex mismatch for {description}")
                
                expected_decimal = bits_to_int(from_hex_string(expected_remainder_hex, 32))
                actual_decimal = bits_to_int(result['rd'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal mismatch for {description}")
    
    def test_multiplication_trace(self):
        rs1_bits = from_hex_string("0x0000000D", 32)
        rs2_bits = from_hex_string("0x00000007", 32)
        
        result = self.mdu.mul(rs1_bits, rs2_bits)
        trace = result['trace']
        
        self.assertIsInstance(trace, list, "Trace should be a list")
        self.assertGreater(len(trace), 0, "Trace should not be empty")
        
        for step in trace:
            self.assertIn('step', step, "Trace step should have 'step' field")
            self.assertIn('action', step, "Trace step should have 'action' field")
    
    def test_division_trace(self):
        dividend_bits = from_hex_string("0x0000000D", 32)
        divisor_bits = from_hex_string("0x00000003", 32)
        
        result = self.mdu.div(dividend_bits, divisor_bits)
        trace = result['trace']
        
        self.assertIsInstance(trace, list, "Trace should be a list")
        self.assertGreater(len(trace), 0, "Trace should not be empty")
        
        for step in trace:
            self.assertIn('step', step, "Trace step should have 'step' field")
            self.assertIn('action', step, "Trace step should have 'action' field")
    
    def test_edge_case_values(self):
        edge_cases = [
            (1, 1, 1, 1, "1 * 1, 1 / 1"),
            (0, 1, 0, 0, "0 * 1, 0 / 1"),
            (1, 0, 0, None, "1 * 0, 1 / 0 (division by zero)"),
            (-1, -1, 1, 1, "-1 * -1, -1 / -1"),
        ]
        
        for a, b, mul_expected, div_expected, description in edge_cases:
            with self.subTest(description=description):
                a_bits = from_hex_string(f"0x{a & 0xFFFFFFFF:08X}", 32)
                b_bits = from_hex_string(f"0x{b & 0xFFFFFFFF:08X}", 32)
                
                mul_result = self.mdu.mul(a_bits, b_bits)
                mul_decimal = bits_to_int(mul_result['rd'])
                self.assertEqual(mul_decimal, mul_expected,
                               f"Multiplication edge case failed: {description}")
                
                if div_expected is not None:
                    div_result = self.mdu.div(a_bits, b_bits)
                    div_decimal = bits_to_int(div_result['rd'])
                    self.assertEqual(div_decimal, div_expected,
                                   f"Division edge case failed: {description}")

if __name__ == '__main__':
    unittest.main()

