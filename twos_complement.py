"""
Two's Complement for RISC-V RV32 integer operations
"""

from bit_utils import from_decimal_string, to_decimal_string, to_hex_string, format_bits

def encode_twos_complement(value: int, width: int = 32) -> dict:
    min_val = -(2 ** (width - 1))
    max_val = (2 ** (width - 1)) - 1
    overflow_flag = 1 if value < min_val or value > max_val else 0
    
    bits = from_decimal_string(str(value), width)
    
    bin_str = format_bits(bits, 8)
    hex_str = to_hex_string(bits)
    
    return {
        'bin': bin_str,
        'hex': hex_str,
        'overflow_flag': overflow_flag
    }

def decode_twos_complement(bits_input) -> dict:
    if isinstance(bits_input, str):
        if bits_input.startswith('0x') or bits_input.startswith('0X'):
            from bit_utils import from_hex_string
            bits = from_hex_string(bits_input)
        else:
            bits = []
            for char in bits_input:
                if char in '01':
                    bits.append(int(char))
                elif char == '_':
                    continue
                else:
                    raise ValueError(f"Invalid binary character: {char}")
    elif isinstance(bits_input, list):
        bits = bits_input[:]
    else:
        raise ValueError("bits_input must be string or list")
    
    value = int(to_decimal_string(bits))
    
    return {'value': value}
