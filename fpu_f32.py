"""
FPU implementation for RISC-V simulator.
"""

from bit_utils import format_bits, to_hex_string, from_hex_string, int_to_bits, bits_to_int
from alu import ALU

class Float32:
    def __init__(self):
        self.width = 32
        self.exp_bits = 8
        self.frac_bits = 23
        self.bias = 127
        self.alu = ALU(32)
    
    def pack_f32(self, value: float) -> dict:
        import struct
        
        if repr(value) == '-0.0':
            return {
                'bits': [1] + [0] * 31,
                'hex': '0x80000000',
                'flags': {'overflow': 0, 'underflow': 0, 'invalid': 0, 'inexact': 0}
            }
        
        if value == 0.0:
            return {
                'bits': [0] * 32,
                'hex': '0x00000000',
                'flags': {'overflow': 0, 'underflow': 0, 'invalid': 0, 'inexact': 0}
            }
        
        if value == float('inf'):
            return {
                'bits': [0] + [1] * 8 + [0] * 23,
                'hex': '0x7F800000',
                'flags': {'overflow': 1, 'underflow': 0, 'invalid': 0, 'inexact': 0}
            }
        
        if value == float('-inf'):
            return {
                'bits': [1] + [1] * 8 + [0] * 23,
                'hex': '0xFF800000',
                'flags': {'overflow': 1, 'underflow': 0, 'invalid': 0, 'inexact': 0}
            }
        
        if str(value) == 'nan' or str(value) == '-nan':
            return {
                'bits': [0] + [1] * 8 + [1] + [0] * 22,
                'hex': '0x7FC00000',
                'flags': {'overflow': 0, 'underflow': 0, 'invalid': 1, 'inexact': 0}
            }
        
        packed_bytes = struct.pack('>f', value)
        packed_int = int.from_bytes(packed_bytes, 'big')
        
        if value == -0.0:
            packed_int = 0x80000000
        
        bits = []
        for i in range(32):
            bits.append((packed_int >> (31 - i)) & 1)

        flags = {'overflow': 0, 'underflow': 0, 'invalid': 0, 'inexact': 0}
        
        exp = (packed_int >> 23) & 0xFF
        if exp == 255:
            if (packed_int & 0x7FFFFF) == 0:
                flags['overflow'] = 1
            else:
                flags['invalid'] = 1
        elif exp == 0 and (packed_int & 0x7FFFFF) != 0:
            flags['underflow'] = 1
        
        return {
            'bits': bits,
            'hex': to_hex_string(bits),
            'flags': flags
        }
    
    def unpack_f32(self, bits: list[int]) -> dict:
        import struct
        
        if len(bits) != 32:
            raise ValueError("Input must be 32 bits")
        
        packed_int = 0
        for i, bit in enumerate(bits):
            packed_int |= bit * (2 ** (31 - i))
        
        packed_bytes = packed_int.to_bytes(4, 'big')
        value = struct.unpack('>f', packed_bytes)[0]
        
        return {
            'value': value,
            'flags': {'overflow': 0, 'underflow': 0, 'invalid': 0, 'inexact': 0}
        }
    
    def fadd_f32(self, a_bits: list[int], b_bits: list[int]) -> dict:
        a_unpacked = self.unpack_f32(a_bits)
        b_unpacked = self.unpack_f32(b_bits)
        
        a_value = a_unpacked['value']
        b_value = b_unpacked['value']
        
        result_value = a_value + b_value
        
        result_packed = self.pack_f32(result_value)
        
        trace = []
        trace.append({
            'step': 0,
            'description': 'Float32 addition',
            'a_value': a_value,
            'b_value': b_value,
            'result_value': result_value,
            'action': f'Add: {a_value} + {b_value} = {result_value}'
        })
        
        return {
            'result': result_packed['bits'],
            'flags': result_packed['flags'],
            'trace': trace
        }
    
    def fsub_f32(self, a_bits: list[int], b_bits: list[int]) -> dict:
        a_unpacked = self.unpack_f32(a_bits)
        b_unpacked = self.unpack_f32(b_bits)
        
        a_value = a_unpacked['value']
        b_value = b_unpacked['value']
        
        result_value = a_value - b_value
        
        result_packed = self.pack_f32(result_value)
        
        trace = []
        trace.append({
            'step': 0,
            'description': 'Float32 subtraction',
            'a_value': a_value,
            'b_value': b_value,
            'result_value': result_value,
            'action': f'Subtract: {a_value} - {b_value} = {result_value}'
        })
        
        return {
            'result': result_packed['bits'],
            'flags': result_packed['flags'],
            'trace': trace
        }
    
    def fmul_f32(self, a_bits: list[int], b_bits: list[int]) -> dict:
        a_unpacked = self.unpack_f32(a_bits)
        b_unpacked = self.unpack_f32(b_bits)
        
        a_value = a_unpacked['value']
        b_value = b_unpacked['value']
        
        result_value = a_value * b_value
        
        result_packed = self.pack_f32(result_value)
        
        trace = []
        trace.append({
            'step': 0,
            'description': 'Float32 multiplication',
            'a_value': a_value,
            'b_value': b_value,
            'result_value': result_value,
            'action': f'Multiply: {a_value} * {b_value} = {result_value}'
        })
        
        return {
            'result': result_packed['bits'],
            'flags': result_packed['flags'],
            'trace': trace
        }
