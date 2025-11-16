"""
Hex file loader for RISC-V program images
"""

from bit_utils import from_hex_string

def load_hex_file(filename: str) -> list[list[int]]:
    instructions = []
    
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line:
                    continue
                
                if '#' in line:
                    line = line.split('#')[0].strip()
                
                if line.startswith('0x') or line.startswith('0X'):
                    line = line[2:]
                
                if len(line) != 8:
                    raise ValueError(f"Line {line_num}: Expected 8 hex digits, got {len(line)}: {line}")
                
                try:
                    instruction = from_hex_string('0x' + line, 32)
                    instructions.append(instruction)
                except ValueError as e:
                    raise ValueError(f"Line {line_num}: Invalid hex: {line} - {e}")
    
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error loading hex file {filename}: {e}")
    
    return instructions

def save_hex_file(filename: str, instructions: list[list[int]]):
    from bit_utils import to_hex_string
    
    with open(filename, 'w') as f:
        for instr in instructions:
            hex_str = to_hex_string(instr)
            hex_str = hex_str[2:].upper()
            if len(hex_str) < 8:
                hex_str = '0' * (8 - len(hex_str)) + hex_str
            f.write(hex_str + '\n')

