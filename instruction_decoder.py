"""
Instruction Decoder for RISC-V RV32I ISA
"""

from bit_utils import bits_to_int, int_to_bits, sign_extend, zero_extend

class InstructionDecoder:
    def __init__(self):
        pass
    
    def decode(self, instruction: list[int]) -> dict:
        if len(instruction) != 32:
            raise ValueError(f"Instruction must be 32 bits, got {len(instruction)}")
        
        opcode = instruction[25:32]
        opcode_int = bits_to_int(opcode)
        
        rd = bits_to_int(instruction[20:25])
        rs1 = bits_to_int(instruction[12:17])
        rs2 = bits_to_int(instruction[7:12])
        
        funct3 = bits_to_int(instruction[17:20])
        
        funct7 = bits_to_int(instruction[0:7])
        
        imm_i = instruction[20:32]
        
        imm_s = instruction[0:7] + instruction[20:25]
        
        imm_b = [instruction[31]] + instruction[25:31] + instruction[8:12] + [instruction[7]] + [0]
        
        imm_u = instruction[0:20] + [0] * 12
        
        imm_j = [instruction[31]] + instruction[21:31] + [instruction[20]] + instruction[12:20] + [0]
        
        imm_i_sext = sign_extend(imm_i, 32)
        imm_s_sext = sign_extend(imm_s, 32)
        imm_b_sext = sign_extend(imm_b, 32)
        imm_j_sext = sign_extend(imm_j, 32)
        imm_u_sext = imm_u
        
        return {
            'opcode': opcode,
            'opcode_int': opcode_int,
            'rd': rd,
            'rs1': rs1,
            'rs2': rs2,
            'funct3': funct3,
            'funct7': funct7,
            'imm_i': imm_i,
            'imm_i_sext': imm_i_sext,
            'imm_s': imm_s,
            'imm_s_sext': imm_s_sext,
            'imm_b': imm_b,
            'imm_b_sext': imm_b_sext,
            'imm_u': imm_u,
            'imm_u_sext': imm_u_sext,
            'imm_j': imm_j,
            'imm_j_sext': imm_j_sext,
            'instruction': instruction
        }
    
    def get_instruction_type(self, decoded: dict) -> str:
        opcode = decoded['opcode_int']
        
        if opcode == 0x33:
            return 'R'
        
        if opcode in [0x03, 0x13, 0x67]:
            return 'I'
        
        if opcode == 0x23:
            return 'S'
        
        if opcode == 0x63:
            return 'B'
        
        if opcode in [0x37, 0x17]:
            return 'U'
        
        if opcode == 0x6F:
            return 'J'
        
        return 'UNKNOWN'
    
    def get_instruction_name(self, decoded: dict) -> str:
        opcode = decoded['opcode_int']
        funct3 = decoded['funct3']
        funct7 = decoded['funct7']
        
        if opcode == 0x33:
            if funct3 == 0x0:
                if funct7 == 0x00:
                    return 'ADD'
                elif funct7 == 0x20:
                    return 'SUB'
            elif funct3 == 0x7:
                return 'AND'
            elif funct3 == 0x6:
                return 'OR'
            elif funct3 == 0x4:
                return 'XOR'
            elif funct3 == 0x1:
                return 'SLL'
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    return 'SRL'
                elif funct7 == 0x20:
                    return 'SRA'
        
        elif opcode == 0x13:
            if funct3 == 0x0:
                return 'ADDI'
            elif funct3 == 0x7:
                return 'ANDI'
            elif funct3 == 0x6:
                return 'ORI'
            elif funct3 == 0x4:
                return 'XORI'
            elif funct3 == 0x1:
                return 'SLLI'
            elif funct3 == 0x5:
                if funct7 == 0x00:
                    return 'SRLI'
                elif funct7 == 0x20:
                    return 'SRAI'
        
        elif opcode == 0x03:
            if funct3 == 0x0:
                return 'LB'
            elif funct3 == 0x1:
                return 'LH'
            elif funct3 == 0x2:
                return 'LW'
        
        elif opcode == 0x23:
            if funct3 == 0x0:
                return 'SB'
            elif funct3 == 0x1:
                return 'SH'
            elif funct3 == 0x2:
                return 'SW'
        
        elif opcode == 0x63:
            if funct3 == 0x0:
                return 'BEQ'
            elif funct3 == 0x1:
                return 'BNE'
            elif funct3 == 0x4:
                return 'BLT'
            elif funct3 == 0x5:
                return 'BGE'
            elif funct3 == 0x6:
                return 'BLTU'
            elif funct3 == 0x7:
                return 'BGEU'
        
        elif opcode == 0x37:
            return 'LUI'
        
        elif opcode == 0x17:
            return 'AUIPC'
        
        elif opcode == 0x6F:
            return 'JAL'
        
        elif opcode == 0x67:
            return 'JALR'
        
        return 'UNKNOWN'

