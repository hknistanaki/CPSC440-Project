"""
Test all instructions and corner cases for RISC-V CPU
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cpu import CPU
from hex_loader import load_hex_file
from bit_utils import bits_to_int, to_hex_string, int_to_bits, from_hex_string
from instruction_decoder import InstructionDecoder

class CPUTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        self.decoder = InstructionDecoder()
        self.prog_hex_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prog.hex')
    
    def run_test(self, test_name: str, test_func):
        print(f"\n{'='*60}")
        print(f"Test: {test_name}")
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
            import traceback
            traceback.print_exc()
            self.failed += 1
        
        self.tests.append((test_name, result if 'result' in locals() else False))
    
    def test_base_program(self):
        instructions = load_hex_file(self.prog_hex_path)
        cpu = CPU()
        cpu.load_program(instructions)
        stats = cpu.run(max_cycles=1000)
        
        state = cpu.get_state()
        regs = state['registers']
        
        expected = {
            'x1': 5,
            'x2': 10,
            'x3': 15,
            'x4': 15,
            'x5': 0x00010000,
            'x6': 2
        }
        
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            if actual_val != expected_val:
                print(f"  {reg_name}: Expected {expected_val}, Got {actual_val}")
                all_passed = False
        
        mem = state['data_memory']
        if '0x00010000' in mem:
            mem_val = int(mem['0x00010000'], 16)
            if mem_val != 15:
                print(f"  Memory[0x00010000]: Expected 15 but got {mem_val}")
                all_passed = False
        else:
            print(f"  Memory[0x00010000]: Expected 15 but got (empty)")
            all_passed = False
        
        return all_passed
    
    def test_arithmetic_operations(self):
        instructions = [
            from_hex_string('0x00A00093', 32),
            from_hex_string('0x00500113', 32),
            from_hex_string('0x002081B3', 32),
            from_hex_string('0x40210233', 32),
            from_hex_string('0x01408293', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        expected = {
            'x1': 10,
            'x2': 5,
            'x3': 15,
            'x4': -5,
            'x5': 30
        }
        
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            if actual_val != expected_val:
                print(f"  {reg_name}: Expected {expected_val} but got {actual_val}")
                all_passed = False
        
        return all_passed
    
    def test_logical_operations(self):
        instructions = [
            from_hex_string('0x00F00093', 32),
            from_hex_string('0x00300113', 32),
            from_hex_string('0x0020F1B3', 32),
            from_hex_string('0x0020E233', 32),
            from_hex_string('0x0020C2B3', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        expected = {
            'x1': 15,
            'x2': 3,
            'x3': 3,
            'x4': 15,
            'x5': 12
        }
        
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            if actual_val != expected_val:
                print(f"  {reg_name}: Expected {expected_val} but got {actual_val}")
                all_passed = False
        
        return all_passed
    
    def test_shift_operations(self):
        instructions = [
            from_hex_string('0x00800093', 32),
            from_hex_string('0x00209113', 32),
            from_hex_string('0x0010D193', 32),
            from_hex_string('0xFF800213', 32),
            from_hex_string('0x40225293', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        expected = {
            'x1': 8,
            'x2': 32,
            'x3': 4,
            'x4': -8,
            'x5': -2
        }
        
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            if actual_val != expected_val:
                print(f"  {reg_name}: Expected {expected_val} but got {actual_val}")
                all_passed = False
        
        return all_passed
    
    def test_branch_operations(self):
        instructions = [
            from_hex_string('0x00500093', 32),
            from_hex_string('0x00500113', 32),
            from_hex_string('0x00A00193', 32),
            from_hex_string('0x00208463', 32),
            from_hex_string('0x00100213', 32),
            from_hex_string('0x00200213', 32),
            from_hex_string('0x00318463', 32),
            from_hex_string('0x00100293', 32),
            from_hex_string('0x00200293', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        expected = {
            'x1': 5,
            'x2': 5,
            'x3': 10,
            'x4': 2,
            'x5': 2
        }
        
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            if actual_val != expected_val:
                print(f"  {reg_name}: Expected {expected_val} but got {actual_val}")
                all_passed = False
        
        return all_passed
    
    def test_jump_operations(self):
        instructions = [
            from_hex_string('0x10000093', 32),
            from_hex_string('0x0080016F', 32),
            from_hex_string('0x00100193', 32),
            from_hex_string('0x00200193', 32),
            from_hex_string('0x000080E7', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        all_passed = True
        if bits_to_int(regs['x1']) != 0x100:
            print(f"  x1: Expected 0x100 but got {hex(bits_to_int(regs['x1']))}")
            all_passed = False
        
        if bits_to_int(regs['x3']) != 2:
            print(f"  x3: Expected 2 but got {bits_to_int(regs['x3'])}")
            all_passed = False
        
        return all_passed
    
    def test_memory_operations(self):
        instructions = [
            from_hex_string('0x000100B7', 32),
            from_hex_string('0x02A00113', 32),
            from_hex_string('0x0020A023', 32),
            from_hex_string('0x0000A183', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        mem = state['data_memory']
        
        all_passed = True
        
        if bits_to_int(regs['x1']) != 0x00010000:
            print(f"  x1: Expected 0x00010000 but got {hex(bits_to_int(regs['x1']))}")
            all_passed = False
        
        if bits_to_int(regs['x2']) != 42:
            print(f"  x2: Expected 42 but got {bits_to_int(regs['x2'])}")
            all_passed = False
        
        if bits_to_int(regs['x3']) != 42:
            print(f"  x3: Expected 42 but got {bits_to_int(regs['x3'])}")
            all_passed = False
        
        if '0x00010000' not in mem:
            print(f"  Memory[0x00010000]: Expected 42 but got (empty)")
            all_passed = False
        else:
            mem_val = int(mem['0x00010000'], 16)
            if mem_val != 42:
                print(f"  Memory[0x00010000]: Expected 42 but got {mem_val}")
                all_passed = False
        
        return all_passed
    
    def test_max_min_values(self):
        instructions = [
            from_hex_string('0xFFF00093', 32),
            from_hex_string('0x80000237', 32),
            from_hex_string('0x0000006F', 32),
        ]
        
        cpu = CPU()
        cpu.load_program(instructions)
        cpu.run(max_cycles=100)
        
        state = cpu.get_state()
        regs = state['registers']
        
        all_passed = True
        
        if bits_to_int(regs['x1']) != -1:
            print(f"  x1: Expected -1 but got {bits_to_int(regs['x1'])}")
            all_passed = False
        
        return all_passed
    
    def run_all_tests(self):
        print("RISC-V CPU Test Suite")
        print("=" * 80)
        
        self.run_test("Base Program", self.test_base_program)
        self.run_test("Arithmetic Operations", self.test_arithmetic_operations)
        self.run_test("Logical Operations", self.test_logical_operations)
        self.run_test("Shift Operations", self.test_shift_operations)
        self.run_test("Branch Operations", self.test_branch_operations)
        self.run_test("Jump Operations", self.test_jump_operations)
        self.run_test("Memory Operations", self.test_memory_operations)
        self.run_test("Max/Min Values", self.test_max_min_values)
        
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        if self.passed + self.failed > 0:
            print(f"Success Rate: {(self.passed / (self.passed + self.failed)) * 100:.1f}%")
        
        if self.failed == 0:
            print("\nAll tests passed")
        else:
            print(f"\n{self.failed} tests failed.")
        
        return self.failed == 0

if __name__ == "__main__":
    suite = CPUTestSuite()
    suite.run_all_tests()

