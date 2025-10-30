"""
Unit tests for Two's Complement
"""

import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twos_complement import encode_twos_complement, decode_twos_complement

class TestTwosComplement(unittest.TestCase):
    def setUp(self):
        self.width = 32
        self.min_val = -(2 ** (self.width - 1))
        self.max_val = (2 ** (self.width - 1)) - 1
    
    def test_boundary_cases(self):
        test_cases = [
            (self.min_val, "0x80000000", 0),
            (-1, "0xFFFFFFFF", 0),
            (-13, "0xFFFFFFF3", 0),
            (-7, "0xFFFFFFF9", 0),
            (0, "0x00000000", 0),
            (13, "0x0000000D", 0),
            (self.max_val, "0x7FFFFFFF", 0),
        ]
        
        for value, expected_hex, expected_overflow in test_cases:
            with self.subTest(value=value):
                result = encode_twos_complement(value)
                
                self.assertEqual(result['hex'], expected_hex, 
                               f"Hex mismatch for value {value}")
                
                self.assertEqual(result['overflow_flag'], expected_overflow,
                               f"Overflow mismatch for value {value}")
                
                decoded = decode_twos_complement(result['hex'])
                self.assertEqual(decoded['value'], value,
                               f"Round trip failed for value {value}")
    
    def test_overflow_cases(self):
        overflow_cases = [
            self.min_val - 1,
            self.max_val + 1,
            2 ** self.width,
            -(2 ** self.width),
        ]
        
        for value in overflow_cases:
            with self.subTest(value=value):
                result = encode_twos_complement(value)
                
                self.assertEqual(result['overflow_flag'], 1,
                               f"Overflow flag not set for out of range {value}")
    
    def test_specific_hex_patterns(self):
        test_cases = [
            (13, "0x0000000D", "00000000_00000000_00000000_00001101"),
            (-13, "0xFFFFFFF3", "11111111_11111111_11111111_11110011"),
        ]
        
        for value, expected_hex, expected_bin in test_cases:
            with self.subTest(value=value):
                result = encode_twos_complement(value)
                
                self.assertEqual(result['hex'], expected_hex,
                               f"Hex mismatch for {value}")
                
                self.assertEqual(result['bin'], expected_bin,
                               f"Binary mismatch for {value}")
    
    def test_decode_edge_cases(self):
        test_cases = [
            ("0x00000000", 0),
            ("0x80000000", self.min_val),
            ("0x7FFFFFFF", self.max_val),
            ("0xFFFFFFFF", -1),
        ]
        
        for hex_pattern, expected_value in test_cases:
            with self.subTest(hex_pattern=hex_pattern):
                result = decode_twos_complement(hex_pattern)
                
                self.assertEqual(result['value'], expected_value,
                               f"Decode for {hex_pattern}")
    
    def test_round_trip_consistency(self):
        test_values = [
            -1000, -100, -10, -1, 0, 1, 10, 100, 1000,
            self.min_val // 2, self.max_val // 2,
        ]
        
        for value in test_values:
            with self.subTest(value=value):
                if value < self.min_val or value > self.max_val:
                    continue
                
                encoded = encode_twos_complement(value)
                decoded = decode_twos_complement(encoded['hex'])
                
                self.assertEqual(decoded['value'], value,
                               f"Round trip failed for {value}")
    
    def test_bit_pattern_consistency(self):
        test_cases = [
            ("0x00000000", 0, "Zero"),
            ("0x00000001", 1, "Positive one"),
            ("0x7FFFFFFF", 2147483647, "Maximum positive"),
            ("0x80000000", -2147483648, "Minimum negative"),
            ("0xFFFFFFFF", -1, "Negative one"),
            ("0x0000000D", 13, "Positive thirteen"),
            ("0xFFFFFFF3", -13, "Negative thirteen"),
        ]
        
        for hex_pattern, expected_decimal, description in test_cases:
            with self.subTest(description=description):
                result = decode_twos_complement(hex_pattern)
                
                self.assertEqual(result['value'], expected_decimal,
                               f"Decimal mismatch for {description}: {hex_pattern}")

if __name__ == '__main__':
    unittest.main()

