"""
Test for the base program
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cpu import CPU
from hex_loader import load_hex_file
from bit_utils import bits_to_int, to_hex_string

def test_base():
    print("Testing base program (prog.hex)...")
    print("=" * 60)
    
    try:
        prog_hex_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'prog.hex')
        
        instructions = load_hex_file(prog_hex_path)
        print(f"Loaded {len(instructions)} instructions")
        
        cpu = CPU()
        cpu.load_program(instructions)
        
        print(f"Starting execution...")
        stats = cpu.run(max_cycles=1000)
        
        print(f"\nStatistics:")
        print(f"  Cycles: {stats['cycles']}")
        print(f"  Instructions: {stats['instructions']}")
        print(f"  Halted: {stats['halted']}")
        
        state = cpu.get_state()
        regs = state['registers']
        
        print(f"\nRegister Values:")
        for reg_name in ['x1', 'x2', 'x3', 'x4', 'x5', 'x6']:
            val = bits_to_int(regs[reg_name])
            hex_val = to_hex_string(regs[reg_name])
            print(f"  {reg_name}: {hex_val} ({val})")
        
        print(f"\nMemory:")
        mem = state['data_memory']
        for addr in sorted(mem.keys()):
            print(f"  {addr}: {mem[addr]}")
        
        expected = {
            'x1': 5,
            'x2': 10,
            'x3': 15,
            'x4': 15,
            'x5': 0x00010000,
            'x6': 2
        }
        
        print(f"\nVerification:")
        all_passed = True
        for reg_name, expected_val in expected.items():
            actual_val = bits_to_int(regs[reg_name])
            status = "PASS" if actual_val == expected_val else "FAIL"
            print(f"  {status} {reg_name}: Expected {expected_val} but got {actual_val}")
            if actual_val != expected_val:
                all_passed = False
        
        if all_passed:
            print("\nAll checks passed")
        else:
            print("\nSome checks failed")
        
        return all_passed
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_base()

