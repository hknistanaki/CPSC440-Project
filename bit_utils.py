"""
Bit manipulation utilities
"""

def from_decimal_string(s: str, width: int = 32) -> list[int]:
    if s.startswith('-'):
        value = int(s[1:])
        bits = from_decimal_string(str(value), width)
        return twos_complement_negate(bits)
    
    value = int(s)
    if value == 0:
        return [0] * width
    
    bits = []
    while value > 0:
        bits.append(value & 1)
        value >>= 1
    
    while len(bits) < width:
        bits.append(0)
    
    bits = bits[::-1]
    return bits[:width]

def to_decimal_string(bits: list[int]) -> str:
    if not bits:
        return "0"
    
    if bits[0] == 1:
        negated = twos_complement_negate(bits)
        value = 0
        for i, bit in enumerate(negated):
            value += bit * (2 ** (len(negated) - 1 - i))
        return f"-{value}"
    else:
        value = 0
        for i, bit in enumerate(bits):
            value += bit * (2 ** (len(bits) - 1 - i))
        return str(value)

def from_hex_string(s: str, width: int = 32) -> list[int]:
    if s.startswith('0x') or s.startswith('0X'):
        s = s[2:]
    
    hex_to_bits = {
        '0': [0, 0, 0, 0], '1': [0, 0, 0, 1], '2': [0, 0, 1, 0], '3': [0, 0, 1, 1],
        '4': [0, 1, 0, 0], '5': [0, 1, 0, 1], '6': [0, 1, 1, 0], '7': [0, 1, 1, 1],
        '8': [1, 0, 0, 0], '9': [1, 0, 0, 1], 'A': [1, 0, 1, 0], 'B': [1, 0, 1, 1],
        'C': [1, 1, 0, 0], 'D': [1, 1, 0, 1], 'E': [1, 1, 1, 0], 'F': [1, 1, 1, 1],
        'a': [1, 0, 1, 0], 'b': [1, 0, 1, 1], 'c': [1, 1, 0, 0], 'd': [1, 1, 0, 1],
        'e': [1, 1, 1, 0], 'f': [1, 1, 1, 1]
    }
    
    bits = []
    for char in s:
        if char in hex_to_bits:
            bits.extend(hex_to_bits[char])
        else:
            raise ValueError(f"Invalid hex character: {char}")
    
    if len(bits) < width:
        bits = [0] * (width - len(bits)) + bits
    else:
        bits = bits[-width:]
    
    return bits

def to_hex_string(bits: list[int]) -> str:
    if not bits:
        return "0x0"
    
    padded_bits = bits[:]
    while len(padded_bits) % 4 != 0:
        padded_bits = [0] + padded_bits
    
    bits_to_hex = {
        (0, 0, 0, 0): '0', (0, 0, 0, 1): '1', (0, 0, 1, 0): '2', (0, 0, 1, 1): '3',
        (0, 1, 0, 0): '4', (0, 1, 0, 1): '5', (0, 1, 1, 0): '6', (0, 1, 1, 1): '7',
        (1, 0, 0, 0): '8', (1, 0, 0, 1): '9', (1, 0, 1, 0): 'A', (1, 0, 1, 1): 'B',
        (1, 1, 0, 0): 'C', (1, 1, 0, 1): 'D', (1, 1, 1, 0): 'E', (1, 1, 1, 1): 'F'
    }
    
    hex_chars = []
    for i in range(0, len(padded_bits), 4):
        nibble = tuple(padded_bits[i:i+4])
        hex_chars.append(bits_to_hex[nibble])
    
    return "0x" + "".join(hex_chars)

def sign_extend(bits: list[int], new_width: int) -> list[int]:
    if len(bits) >= new_width:
        return bits[-new_width:]
    
    sign_bit = bits[0] if bits else 0
    extension = [sign_bit] * (new_width - len(bits))
    return extension + bits

def zero_extend(bits: list[int], new_width: int) -> list[int]:
    if len(bits) >= new_width:
        return bits[-new_width:]
    
    extension = [0] * (new_width - len(bits))
    return extension + bits

def twos_complement_negate(bits: list[int]) -> list[int]:
    inverted = [1 - bit for bit in bits]
    
    result = inverted[:]
    carry = 1
    for i in range(len(result) - 1, -1, -1):
        sum_bits = result[i] + carry
        result[i] = sum_bits % 2
        carry = sum_bits // 2
        if carry == 0:
            break
    
    return result

def bits_to_int(bits: list[int]) -> int:
    if not bits:
        return 0
    
    if bits[0] == 1:
        negated = twos_complement_negate(bits)
        value = 0
        for i, bit in enumerate(negated):
            value += bit * (2 ** (len(negated) - 1 - i))
        return -value
    else:
        value = 0
        for i, bit in enumerate(bits):
            value += bit * (2 ** (len(bits) - 1 - i))
        return value

def int_to_bits(value: int, width: int = 32) -> list[int]:
    if value < 0:
        abs_value = -value
        bits = []
        while abs_value > 0:
            bits.append(abs_value & 1)
            abs_value >>= 1
        
        while len(bits) < width:
            bits.append(0)
        
        bits = bits[::-1]
        bits = bits[:width]
        return twos_complement_negate(bits)
    
    bits = []
    if value == 0:
        return [0] * width
    
    while value > 0:
        bits.append(value & 1)
        value >>= 1
    
    while len(bits) < width:
        bits.append(0)
    
    bits = bits[::-1]
    return bits[:width]

def format_bits(bits: list[int], group_size: int = 8) -> str:
    if not bits:
        return "0"
    
    bit_str = "".join(str(bit) for bit in bits)
    
    if group_size > 0 and len(bit_str) > group_size:
        groups = []
        for i in range(0, len(bit_str), group_size):
            groups.append(bit_str[i:i+group_size])
        return "_".join(groups)
    
    return bit_str
