"""
Main runner for RISC-V CPU simulator
"""

from cpu import CPU
from hex_loader import load_hex_file
from bit_utils import bits_to_int, to_hex_string

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python run_cpu.py <hex_file> [verbose]")
        print("Example: python run_cpu.py prog.hex")
        return
    
    hex_file = sys.argv[1]
    verbose = len(sys.argv) > 2 and sys.argv[2].lower() == 'verbose'
    
    try:
        print(f"Loading program from {hex_file}...")
        instructions = load_hex_file(hex_file)
        print(f"Loaded {len(instructions)} instructions")
        
        cpu = CPU()
        cpu.load_program(instructions)
        
        print(f"\nStarting execution...")
        print(f"Initial PC: {hex(cpu.pc)}")
        
        stats = cpu.run(max_cycles=1000, verbose=verbose)
        
        print(f"\n{'='*60}")
        print("Execution Complete")
        print(f"{'='*60}")
        print(f"Cycles executed: {stats['cycles']}")
        print(f"Instructions executed: {stats['instructions']}")
        print(f"Halted: {stats['halted']}")
        print(f"Final PC: {hex(stats['final_pc'])}")
        
        state = cpu.get_state()
        regs = state['registers']
        
        print(f"\n{'='*60}")
        print("Final Register State (non-zero registers)")
        print(f"{'='*60}")
        for reg_name in sorted(regs.keys()):
            reg_val = bits_to_int(regs[reg_name])
            reg_hex = to_hex_string(regs[reg_name])
            if reg_val != 0 or reg_name == 'x0':
                print(f"  {reg_name}: {reg_hex} ({reg_val})")
        
        mem = state['data_memory']
        if mem:
            print(f"\n{'='*60}")
            print("Data Memory (non-zero words)")
            print(f"{'='*60}")
            for addr in sorted(mem.keys()):
                print(f"  {addr}: {mem[addr]}")
        
    except FileNotFoundError:
        print(f"Error: File '{hex_file}' not found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

