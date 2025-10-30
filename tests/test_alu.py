"""
Unit tests for ALU operations RV32I Add/Sub
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from alu import ALU
from bit_utils import from_hex_string, to_hex_string, bits_to_int

class TestALU(unittest.TestCase):
    
    def setUp(self):
        self.alu = ALU(32)
    
    def test_add_overflow_cases(self):
        test_cases = [
            ("0x7FFFFFFF", "0x00000001", "0x80000000", 
             {'N': 1, 'Z': 0, 'C': 0, 'V': 1}, "INT_MAX + 1"),
            ("0xFFFFFFFF", "0xFFFFFFFF", "0xFFFFFFFE", 
             {'N': 1, 'Z': 0, 'C': 1, 'V': 0}, "-1 + -1"),
            ("0x0000000D", "0xFFFFFFF3", "0x00000000", 
             {'N': 0, 'Z': 1, 'C': 1, 'V': 0}, "13 + -13"),
        ]
        
        for a_hex, b_hex, expected_result_hex, expected_flags, description in test_cases:
            with self.subTest(description=description):
                a_bits = from_hex_string(a_hex, 32)
                b_bits = from_hex_string(b_hex, 32)
                
                result = self.alu.add(a_bits, b_bits)
                
                result_hex = to_hex_string(result['result'])
                
                from bit_utils import bits_to_int
                expected_decimal = bits_to_int(from_hex_string(expected_result_hex, 32))
                actual_decimal = bits_to_int(result['result'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal result mismatch for {description}")
                
                self.assertEqual(result_hex, expected_result_hex,
                               f"Hex pattern mismatch for {description}")
                
                for flag_name, expected_value in expected_flags.items():
                    self.assertEqual(result[flag_name], expected_value,
                                   f"Flag {flag_name} mismatch for {description}")
    
    def test_sub_overflow_cases(self):
        test_cases = [
            ("0x80000000", "0x00000001", "0x7FFFFFFF", 
             {'N': 0, 'Z': 0, 'C': 1, 'V': 1}, "INT_MIN - 1"),
            ("0x0000000D", "0x00000007", "0x00000006", 
             {'N': 0, 'Z': 0, 'C': 1, 'V': 0}, "13 - 7"),
            ("0x00000000", "0x00000001", "0xFFFFFFFF", 
             {'N': 1, 'Z': 0, 'C': 0, 'V': 0}, "0 - 1"),
        ]
        
        for a_hex, b_hex, expected_result_hex, expected_flags, description in test_cases:
            with self.subTest(description=description):
                a_bits = from_hex_string(a_hex, 32)
                b_bits = from_hex_string(b_hex, 32)
                
                result = self.alu.sub(a_bits, b_bits)
                
                result_hex = to_hex_string(result['result'])
                
                from bit_utils import bits_to_int
                expected_decimal = bits_to_int(from_hex_string(expected_result_hex, 32))
                actual_decimal = bits_to_int(result['result'])
                self.assertEqual(actual_decimal, expected_decimal,
                               f"Decimal result mismatch for {description}")
                
                self.assertEqual(result_hex, expected_result_hex,
                               f"Hex pattern mismatch for {description}")
                
                for flag_name, expected_value in expected_flags.items():
                    self.assertEqual(result[flag_name], expected_value,
                                   f"Flag {flag_name} mismatch for {description}")
    
    def test_flag_meanings(self):
        result = self.alu.add(from_hex_string("0x00000001", 32), 
                            from_hex_string("0x00000000", 32))
        self.assertEqual(result['N'], 0, "N flag should be 0 for positive result")
        
        result = self.alu.add(from_hex_string("0xFFFFFFFF", 32), 
                            from_hex_string("0xFFFFFFFF", 32))
        self.assertEqual(result['N'], 1, "N flag should be 1 for negative result")
        
        result = self.alu.add(from_hex_string("0x0000000D", 32), 
                            from_hex_string("0xFFFFFFF3", 32))
        self.assertEqual(result['Z'], 1, "Z flag should be 1 for zero result")
        
        result = self.alu.add(from_hex_string("0x00000001", 32), 
                            from_hex_string("0x00000001", 32))
        self.assertEqual(result['Z'], 0, "Z flag should be 0 for non-zero result")
        
        result = self.alu.add(from_hex_string("0xFFFFFFFF", 32), 
                            from_hex_string("0x00000001", 32))
        self.assertEqual(result['C'], 1, "C flag should be 1 when carry out occurs")
        
        result = self.alu.add(from_hex_string("0x00000001", 32), 
                            from_hex_string("0x00000001", 32))
        self.assertEqual(result['C'], 0, "C flag should be 0 when no carry out")
        
        result = self.alu.add(from_hex_string("0x7FFFFFFF", 32), 
                            from_hex_string("0x00000001", 32))
        self.assertEqual(result['V'], 1, "V flag should be 1 for signed overflow")
        
        result = self.alu.add(from_hex_string("0x00000001", 32), 
                            from_hex_string("0x00000001", 32))
        self.assertEqual(result['V'], 0, "V flag should be 0 when no overflow")
    
    def test_execute_method(self):
        a_bits = from_hex_string("0x0000000D", 32)  # 13
        b_bits = from_hex_string("0x00000007", 32)  # 7
        
        result = self.alu.execute(a_bits, b_bits, "ADD")
        expected_decimal = 20  # 13 + 7
        actual_decimal = bits_to_int(result['result'])
        self.assertEqual(actual_decimal, expected_decimal, "ADD execute failed")
        
        result = self.alu.execute(a_bits, b_bits, "SUB")
        expected_decimal = 6  # 13 - 7
        actual_decimal = bits_to_int(result['result'])
        self.assertEqual(actual_decimal, expected_decimal, "SUB execute failed")
        
        with self.assertRaises(ValueError):
            self.alu.execute(a_bits, b_bits, "INVALID")
    
    def test_edge_case_values(self):
        edge_cases = [
            (0, 0, "ADD", 0, "Zero + Zero"),
            (0, 1, "ADD", 1, "Zero + One"),
            (1, 0, "ADD", 1, "One + Zero"),
            (0, 0, "SUB", 0, "Zero - Zero"),
            (1, 0, "SUB", 1, "One - Zero"),
            (0, 1, "SUB", -1, "Zero - One"),
        ]
        
        for a, b, operation, expected_result, description in edge_cases:
            with self.subTest(description=description):
                a_bits = from_hex_string(f"0x{a:08X}", 32)
                b_bits = from_hex_string(f"0x{b:08X}", 32)
                
                if operation == "ADD":
                    result = self.alu.add(a_bits, b_bits)
                else:
                    result = self.alu.sub(a_bits, b_bits)
                
                actual_result = bits_to_int(result['result'])
                self.assertEqual(actual_result, expected_result,
                               f"Edge case failed: {description}")

if __name__ == '__main__':
    unittest.main()
