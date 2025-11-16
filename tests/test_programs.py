"""
Test program generator and runner for RISC-V CPU
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cpu import CPU
from hex_loader import load_hex_file
from bit_utils import bits_to_int, to_hex_string, int_to_bits

def run_test_program(hex_file: str, expected_regs: dict = None, expected_mem: dict = None, verbose: bool = False):
    print(f"\n{'='*60}")
    print(f"Running test program: {hex_file}")
    print(f"{'='*60}")
    
    instructions = load_hex_file(hex_file)
    print(f"Loaded {len(instructions)} instructions")
    
    cpu = CPU()
    cpu.load_program(instructions)
    
    stats = cpu.run(max_cycles=1000, verbose=verbose)
    
    print(f"\nExecution Statistics:")
    print(f"  Cycles: {stats['cycles']}")
    print(f"  Instructions: {stats['instructions']}")
    print(f"  Halted: {stats['halted']}")
    print(f"  Final PC: {hex(stats['final_pc'])}")
    
    state = cpu.get_state()
    
    print(f"\nFinal Register State:")
    regs = state['registers']
    for reg_name in sorted(regs.keys()):
        reg_val = bits_to_int(regs[reg_name])
        reg_hex = to_hex_string(regs[reg_name])
        if reg_val != 0 or reg_name == 'x0':
            print(f"  {reg_name}: {reg_hex} ({reg_val})")
    
    print(f"\nData Memory (non-zero):")
    mem = state['data_memory']
    if mem:
        for addr in sorted(mem.keys()):
            print(f"  {addr}: {mem[addr]}")
    else:
        print("  (empty)")
    
    all_passed = True
    if expected_regs:
        print(f"\nVerifying Register Values:")
        for reg_name, expected_val in expected_regs.items():
            actual_val = bits_to_int(regs[reg_name])
            if isinstance(expected_val, int):
                passed = (actual_val == expected_val)
            else:
                expected_int = int(expected_val, 16)
                passed = (actual_val == expected_int)
            
            status = "PASS" if passed else "FAIL"
            print(f"  {reg_name}: Expected {expected_val}, Got {actual_val} - {status}")
            if not passed:
                all_passed = False
    
    if expected_mem:
        print(f"\nVerifying Memory Values:")
        for addr, expected_val in expected_mem.items():
            if addr in mem:
                actual_val = mem[addr]
                if isinstance(expected_val, str):
                    passed = (actual_val.upper() == expected_val.upper())
                else:
                    passed = (actual_val == expected_val)
                
                status = "PASS" if passed else "FAIL"
                print(f"  {addr}: Expected {expected_val}, Got {actual_val} - {status}")
                if not passed:
                    all_passed = False
            else:
                print(f"  {addr}: Expected {expected_val}, Got (empty) - FAIL")
                all_passed = False
    
    if expected_regs or expected_mem:
        print(f"\n{'='*60}")
        if all_passed:
            print("TEST PASSED")
        else:
            print("TEST FAILED")
        print(f"{'='*60}")
    
    return all_passed, state

def test_base_program():
    prog_hex_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prog.hex')
    
    expected = {
        'x1': 5,
        'x2': 10,
        'x3': 15,
        'x4': 15,
        'x5': 0x00010000,
        'x6': 2
    }
    
    expected_mem = {
        '0x00010000': '0x0000000F'
    }
    
    return run_test_program(prog_hex_path, expected, expected_mem)

if __name__ == "__main__":
    test_base_program()

