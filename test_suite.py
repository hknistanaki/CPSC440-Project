"""
Unit test suite, tests all components with traces and edge cases
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twos_complement import encode_twos_complement, decode_twos_complement
from bit_utils import format_bits, to_hex_string, from_hex_string, bits_to_int, int_to_bits
from registers import RegisterFile, FPRegisterFile
from alu import ALU
from shifter import Shifter
from mdu import MultiplyDivideUnit
from fpu_f32 import Float32

class TestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def run_test(self, test_name: str, test_func):
        print(f"\n{'='*60}")
        print(f"Running Test: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            if result:
                print(f"PASSED: {test_name}")
                self.passed += 1
            else:
                print(f"FAILED: {test_name}")
                self.failed += 1
        except Exception as e:
            print(f"ERROR in {test_name}: {e}")
            self.failed += 1
        
        self.tests.append((test_name, result if 'result' in locals() else False))
    
    def test_twos_complement(self):
        print("Testing Two's Complement Toolkit")
        print("-" * 40)
        
        test_cases = [
            (+13, "00000000_00000000_00000000_00001101", "0x0000000D", 0),
            (-13, "11111111_11111111_11111111_11110011", "0xFFFFFFF3", 0),
            (2**31, None, None, 1),
        ]
        
        all_passed = True
        for value, expected_bin, expected_hex, expected_overflow in test_cases:
            print(f"\nTesting value: {value}")
            
            result = encode_twos_complement(value)
            print(f"  Encoded:")
            print(f"    Binary: {result['bin']}")
            print(f"    Hex:    {result['hex']}")
            print(f"    Overflow: {result['overflow_flag']}")
            
            if expected_bin:
                print(f"  Expected binary: {expected_bin}")
                print(f"  Expected hex:    {expected_hex}")
                bin_match = result['bin'] == expected_bin
                hex_match = result['hex'] == expected_hex
                overflow_match = result['overflow_flag'] == expected_overflow
                
                print(f"  Binary match: {bin_match}")
                print(f"  Hex match: {hex_match}")
                print(f"  Overflow match: {overflow_match}")
                
                if not (bin_match and hex_match and overflow_match):
                    all_passed = False
                
                if not result['overflow_flag']:
                    decoded = decode_twos_complement(result['hex'])
                    print(f"  Decoded back: {decoded['value']}")
                    print(f"  Round-trip match: {decoded['value'] == value}")
                    if decoded['value'] != value:
                        all_passed = False
        
        return all_passed
    
    def test_alu(self):
        print("Testing ALU")
        print("-" * 40)
        
        alu = ALU(32)
        
        test_cases = [
            ("0x7FFFFFFF", "0x00000001", "ADD", "0x80000000", {'N': 1, 'Z': 0, 'C': 0, 'V': 1}),
            ("0x80000000", "0x00000001", "SUB", "0x7FFFFFFF", {'N': 0, 'Z': 0, 'C': 1, 'V': 1}),
            ("0xFFFFFFFF", "0xFFFFFFFF", "ADD", "0xFFFFFFFE", {'N': 1, 'Z': 0, 'C': 1, 'V': 0}),
        ]
        
        all_passed = True
        for a_hex, b_hex, op, expected_result_hex, expected_flags in test_cases:
            print(f"\nTesting {op}: {a_hex} {op} {b_hex}")
            
            a_bits = from_hex_string(a_hex, 32)
            b_bits = from_hex_string(b_hex, 32)
            
            result = alu.execute(a_bits, b_bits, op)
            
            result_hex = to_hex_string(result['result'])
            
            print(f"  Operand A: {format_bits(a_bits, 8)} ({a_hex})")
            print(f"  Operand B: {format_bits(b_bits, 8)} ({b_hex})")
            print(f"  Result:    {format_bits(result['result'], 8)} ({result_hex})")
            print(f"  Flags: N={result['N']}, Z={result['Z']}, C={result['C']}, V={result['V']}")
            
            result_match = result_hex == expected_result_hex
            flags_match = all(result[k] == expected_flags[k] for k in expected_flags)
            
            print(f"  Result match: {result_match}")
            print(f"  Flags match: {flags_match}")
            
            if not (result_match and flags_match):
                all_passed = False
        
        return all_passed
    
    def test_shifter(self):
        print("Testing Shifter")
        print("-" * 40)
        
        shifter = Shifter(8)
        
        test_cases = [
            ("0x81", 1, "SLL", "0x02", "Left shift 0x81 by 1"),
            ("0x81", 1, "SRL", "0x40", "Right logical shift 0x81 by 1"),
            ("0x81", 1, "SRA", "0xC0", "Right arithmetic shift 0x81 by 1"),
            ("0x7F", 1, "SRA", "0x3F", "Right arithmetic shift positive 0x7F by 1"),
        ]
        
        all_passed = True
        for data_hex, shift_amount, operation, expected_result_hex, description in test_cases:
            print(f"\n{description}")
            
            data_bits = from_hex_string(data_hex, 8)
            shift_amount_bits = [int(bit) for bit in format(shift_amount, '05b')]
            
            result = shifter.execute(data_bits, shift_amount_bits, operation)
            result_hex = to_hex_string(result)
            
            print(f"  Input:     {format_bits(data_bits, 4)} ({data_hex})")
            print(f"  Shift:     {shift_amount} positions {operation}")
            print(f"  Result:    {format_bits(result, 4)} ({result_hex})")
            print(f"  Expected:  {expected_result_hex}")
            print(f"  Match:     {result_hex == expected_result_hex}")
            
            if result_hex != expected_result_hex:
                all_passed = False
        
        return all_passed
    
    def test_mdu(self):
        print("Testing Multiply/Divide")
        print("-" * 40)
        
        mdu = MultiplyDivideUnit(32)
        
        print("\nTesting MUL:")
        rs1 = from_hex_string("0x12345678", 32)
        rs2 = from_hex_string("0xFEDCBA87", 32)
        
        result = mdu.mul(rs1, rs2)
        result_hex = to_hex_string(result['rd'])
        
        print(f"  MUL 0x12345678 * 0xFEDCBA87")
        print(f"  Result: {result_hex}")
        print(f"  Overflow: {result['overflow']}")
        print(f"  Expected: 0xFF8CC948 (low 32 bits)")
        
        mul_passed = result_hex == '0xFF8CC948'
        print(f"  Match: {mul_passed}")
        
        print("\nTesting DIV:")
        dividend = from_hex_string("0xFFFFFFF9", 32)
        divisor = from_hex_string("0x00000003", 32)
        
        div_result = mdu.div(dividend, divisor)
        div_hex = to_hex_string(div_result['rd'])
        
        print(f"  DIV -7 / 3")
        print(f"  Quotient: {div_hex}")
        print(f"  Expected: 0xFFFFFFFE (-2)")
        
        div_passed = div_hex == '0xFFFFFFFE'
        print(f"  Match: {div_passed}")
        
        return mul_passed and div_passed
    
    def test_fpu_f32(self):
        print("Testing IEEE-754 Float32")
        print("-" * 40)
        
        fpu = Float32()
        
        print("\nTesting addition:")
        a = fpu.pack_f32(1.5)
        b = fpu.pack_f32(2.25)
        add_result = fpu.fadd_f32(a['bits'], b['bits'])
        add_hex = to_hex_string(add_result['result'])
        
        print(f"  1.5 + 2.25 = {add_hex}")
        print(f"  Expected: 0x40700000 (3.75)")
        
        add_passed = add_hex == '0x40700000'
        print(f"  Match: {add_passed}")
        
        print("\nTesting 0.1 + 0.2:")
        a = fpu.pack_f32(0.1)
        b = fpu.pack_f32(0.2)
        add_result = fpu.fadd_f32(a['bits'], b['bits'])
        add_hex = to_hex_string(add_result['result'])
        
        print(f"  0.1 + 0.2 = {add_hex}")
        print(f"  Expected: 0x3E99999A (≈0.3000000119)")
        
        precision_passed = add_hex == '0x3E99999A'
        print(f"  Match: {precision_passed}")
        
        return add_passed and precision_passed
    
    def test_register_file(self):
        print("Testing Register File")
        print("-" * 40)
        
        rf = RegisterFile(4, 8)
        
        print("\nTesting writes:")
        rf.write(1, [1, 1, 0, 0, 1, 1, 0, 0])
        rf.write(2, [0, 1, 1, 0, 0, 1, 1, 0])
        rf.write(3, [1, 0, 0, 1, 1, 0, 0, 1])
        rf.clock_edge()
        
        print(f"After writes:")
        print(f"  x1: {format_bits(rf.read(1), 4)}")
        print(f"  x2: {format_bits(rf.read(2), 4)}")
        print(f"  x3: {format_bits(rf.read(3), 4)}")
        
        print("\nTesting x0 hard wired behavior:")
        rf.write(0, [1, 1, 1, 1, 1, 1, 1, 1])
        rf.clock_edge()
        
        x0_zero = rf.read(0) == [0, 0, 0, 0, 0, 0, 0, 0]
        print(f"  x0 should still be zero: {x0_zero}")
        
        return x0_zero
    
    def test_integration(self):
        print("Testing Component")
        print("-" * 40)
        
        rf = RegisterFile(32, 32)
        alu = ALU(32)
        shifter = Shifter(32)
        mdu = MultiplyDivideUnit(32)
        fpu = Float32()
        
        print("\nTesting ALU + Register:")
        
        operand_a = int_to_bits(13, 32)
        operand_b = int_to_bits(7, 32)
        
        rf.write(1, operand_a)
        rf.write(2, operand_b)
        rf.clock_edge()
        
        a = rf.read(1)
        b = rf.read(2)
        
        result = alu.add(a, b)
        
        rf.write(3, result['result'])
        rf.clock_edge()
        
        stored_result = rf.read(3)
        expected_result = int_to_bits(20, 32)
        
        print(f"  x1 (13): {format_bits(a, 8)}")
        print(f"  x2 (7):  {format_bits(b, 8)}")
        print(f"  x3 (20): {format_bits(stored_result, 8)}")
        print(f"  Expected: {format_bits(expected_result, 8)}")
        
        integration_passed = stored_result == expected_result
        print(f"  Match: {integration_passed}")
        
        return integration_passed
    
    def run_all_tests(self):
        print("RISC-V Test Suite")
        print("=" * 80)
        
        self.run_test("Two's Complement Toolkit", self.test_twos_complement)
        self.run_test("ALU Operations", self.test_alu)
        self.run_test("Shifter Operations", self.test_shifter)
        self.run_test("Multiply/Divide Unit", self.test_mdu)
        self.run_test("IEEE-754 Float32", self.test_fpu_f32)
        self.run_test("Register File", self.test_register_file)
        self.run_test("Component Integration", self.test_integration)
        
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed)) * 100:.1f}%")
        
        if self.failed == 0:
            print("\nAll tests passed! The simulator is working correctly.")
        else:
            print(f"\n{self.failed} test(s) failed. Please review the output above.")
        
        return self.failed == 0

def main():
    test_suite = TestSuite()
    success = test_suite.run_all_tests()
    
    if success:
        print("\nAll components are working correctly")
    else:
        print("\nSome tests failed")
    
    return success

if __name__ == "__main__":
    main()

