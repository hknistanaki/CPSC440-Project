"""
Unit tests Float32 operations
"""

import unittest
import sys
import os
import struct

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fpu_f32 import Float32
from bit_utils import to_hex_string

class TestFloat32(unittest.TestCase):
    def setUp(self):
        self.fpu = Float32()
    
    def test_pack_unpack_known_values(self):
        test_cases = [
            (3.75, "0x40700000", "3.75"),
            (1.5, "0x3FC00000", "1.5"),
            (2.25, "0x40100000", "2.25"),
            (0.0, "0x00000000", "Zero"),
            (-0.0, "0x80000000", "Negative zero"),
            (1.0, "0x3F800000", "One"),
            (-1.0, "0xBF800000", "Negative one"),
        ]
        
        for value, expected_hex, description in test_cases:
            with self.subTest(description=description):
                packed = self.fpu.pack_f32(value)
                packed_hex = packed['hex']
                
                self.assertEqual(packed_hex, expected_hex,
                               f"Pack hex mismatch {description}")
                
                unpacked = self.fpu.unpack_f32(packed['bits'])
                unpacked_value = unpacked['value']
                
                if value in [0.0, -0.0] or abs(value) == float('inf'):
                    self.assertEqual(unpacked_value, value,
                                   f"Unpack value mismatch {description}")
                else:
                    self.assertAlmostEqual(unpacked_value, value, places=6,
                                          msg=f"Unpack value mismatch {description}")
    
    def test_rounding_edge_cases(self):
        a = self.fpu.pack_f32(0.1)
        b = self.fpu.pack_f32(0.2)
        result = self.fpu.fadd_f32(a['bits'], b['bits'])
        result_hex = to_hex_string(result['result'])
        
        self.assertEqual(result_hex, "0x3E99999A",
                        "0.1 + 0.2 should = 0x3E99999A")
        
        unpacked = self.fpu.unpack_f32(result['result'])
        expected_value = 0.30000001192092896
        self.assertAlmostEqual(unpacked['value'], expected_value, places=10,
                              msg="0.1 + 0.2 decimal value mismatch")
    
    def test_overflow_cases(self):
        inf_bits = [0] + [1] * 8 + [0] * 23
        neg_inf_bits = [1] + [1] * 8 + [0] * 23
        
        result = self.fpu.fmul_f32(inf_bits, inf_bits)
        result_hex = to_hex_string(result['result'])
        
        self.assertIn(result_hex, ["0x7F800000", "0x7FC00000"],
                     "infinity * infinity should result in infinity or NaN")
        
        if result_hex == "0x7F800000":
            self.assertEqual(result['flags']['overflow'], 1,
                           "Overflow flag should be set for infinity result")
        elif result_hex == "0x7FC00000":
            self.assertEqual(result['flags']['invalid'], 1,
                           "Invalid flag should be set for NaN result")
    
    def test_underflow_cases(self):
        small_value = 1e-45
        packed = self.fpu.pack_f32(small_value)
        
        unpacked = self.fpu.unpack_f32(packed['bits'])
        
        self.assertLess(unpacked['value'], 1e-40,
                       "Underflow should result in a small number")
    
    def test_nan_infinity_propagation(self):
        nan_bits = [0] + [1] * 8 + [1] + [0] * 22
        
        normal_bits = self.fpu.pack_f32(1.0)['bits']
        result = self.fpu.fadd_f32(nan_bits, normal_bits)
        
        result_hex = to_hex_string(result['result'])
        self.assertEqual(result_hex, "0x7FC00000",
                        "NaN + normal should result in NaN")
        self.assertEqual(result['flags']['invalid'], 1,
                        "Invalid flag should be set for NaN")
        
        inf_bits = [0] + [1] * 8 + [0] * 23
        result = self.fpu.fadd_f32(inf_bits, inf_bits)
        
        result_hex = to_hex_string(result['result'])
        self.assertIn(result_hex, ["0x7FC00000", "0x7F800000"],
                     "infinity + infinity should result in NaN or infinity")
        
        if result_hex == "0x7FC00000":
            self.assertEqual(result['flags']['invalid'], 1,
                            "Invalid flag should be set for NaN")
        elif result_hex == "0x7F800000":
            self.assertEqual(result['flags']['overflow'], 1,
                            "Overflow flag should be set for infinity")
    
    def test_sign_of_zero(self):
        pos_zero = self.fpu.pack_f32(0.0)
        self.assertEqual(pos_zero['hex'], "0x00000000",
                        "Positive zero should be 0x00000000")
        
        neg_zero = self.fpu.pack_f32(-0.0)
        self.assertEqual(neg_zero['hex'], "0x80000000",
                        "Negative zero should be 0x80000000")
        
        pos_unpacked = self.fpu.unpack_f32(pos_zero['bits'])
        neg_unpacked = self.fpu.unpack_f32(neg_zero['bits'])
        
        self.assertEqual(pos_unpacked['value'], 0.0,
                        "Positive zero unpack should be 0.0")
        self.assertEqual(neg_unpacked['value'], -0.0,
                        "Negative zero unpack should be -0.0")
    
    def test_arithmetic_operations(self):
        a = self.fpu.pack_f32(1.5)
        b = self.fpu.pack_f32(2.25)
        add_result = self.fpu.fadd_f32(a['bits'], b['bits'])
        add_hex = to_hex_string(add_result['result'])
        
        self.assertEqual(add_hex, "0x40700000",
                        "1.5 + 2.25 should equal 0x40700000")
        
        unpacked = self.fpu.unpack_f32(add_result['result'])
        self.assertAlmostEqual(unpacked['value'], 3.75, places=6,
                              msg="Addition decimal result mismatch")
        
        sub_result = self.fpu.fsub_f32(b['bits'], a['bits'])
        sub_hex = to_hex_string(sub_result['result'])
        
        unpacked_sub = self.fpu.unpack_f32(sub_result['result'])
        self.assertAlmostEqual(unpacked_sub['value'], 0.75, places=6,
                              msg="Subtraction decimal result mismatch")
        
        mul_result = self.fpu.fmul_f32(a['bits'], b['bits'])
        mul_hex = to_hex_string(mul_result['result'])
        
        unpacked_mul = self.fpu.unpack_f32(mul_result['result'])
        self.assertAlmostEqual(unpacked_mul['value'], 3.375, places=6,
                              msg="Multiplication decimal result mismatch")
    
    def test_special_value_handling(self):
        inf_value = float('inf')
        packed_inf = self.fpu.pack_f32(inf_value)
        self.assertEqual(packed_inf['hex'], "0x7F800000",
                        "Positive infinity should be 0x7F800000")
        
        neg_inf_value = float('-inf')
        packed_neg_inf = self.fpu.pack_f32(neg_inf_value)
        self.assertEqual(packed_neg_inf['hex'], "0xFF800000",
                        "Negative infinity should be 0xFF800000")
        
        nan_value = float('nan')
        packed_nan = self.fpu.pack_f32(nan_value)
        self.assertEqual(packed_nan['flags']['invalid'], 1,
                        "NaN should set invalid flag")
    
    def test_flag_generation(self):
        large_value = 3.4e38
        packed_large = self.fpu.pack_f32(large_value)
        
        small_value = 1e-45
        packed_small = self.fpu.pack_f32(small_value)
        
        nan_bits = [0] + [1] * 8 + [1] + [0] * 22
        normal_bits = self.fpu.pack_f32(1.0)['bits']
        result = self.fpu.fadd_f32(nan_bits, normal_bits)
        
        self.assertEqual(result['flags']['invalid'], 1,
                        "NaN operation")
    
    def test_ieee754_compliance(self):
        test_values = [1.0, -1.0, 0.5, -0.5, 3.14159, -3.14159]
        
        for value in test_values:
            with self.subTest(value=value):
                our_packed = self.fpu.pack_f32(value)
                our_hex = our_packed['hex']
                
                struct_packed = struct.pack('>f', value)
                struct_hex = '0x' + struct_packed.hex().upper()
                
                self.assertEqual(our_hex, struct_hex,
                               f"IEEE-754 compliance failed for {value}")
    
    def test_edge_case_precision(self):
        test_cases = [
            (1.0, "0x3F800000"),
            (2.0, "0x40000000"),
            (0.5, "0x3F000000"),
            (0.25, "0x3E800000"),
        ]
        
        for value, expected_hex in test_cases:
            with self.subTest(value=value):
                packed = self.fpu.pack_f32(value)
                self.assertEqual(packed['hex'], expected_hex,
                               f"Precision failed for {value}")

if __name__ == '__main__':
    unittest.main()
