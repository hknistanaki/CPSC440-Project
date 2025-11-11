"""
Control Unit for RISC-V single-cycle CPU
"""

class ControlUnit:
    def __init__(self):
        pass
    
    def generate_control_signals(self, decoded: dict, instruction_name: str) -> dict:
        opcode = decoded['opcode_int']
        funct3 = decoded['funct3']

        signals = {
            'RegWrite': 0,
            'MemRead': 0,
            'MemWrite': 0,
            'MemToReg': 0,
            'ALUSrc': 0,
            'Branch': 0,
            'Jump': 0,
            'ALUOp': 'ADD',
            'ImmType': 'I',
            'ShiftOp': None,
            'UseShift': 0,
        }
        
        if instruction_name in ['ADD', 'SUB', 'AND', 'OR', 'XOR']:
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 0
            signals['ALUOp'] = instruction_name
            signals['ImmType'] = 'R'
        
        elif instruction_name in ['ADDI', 'ANDI', 'ORI', 'XORI']:
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 1
            signals['ALUOp'] = instruction_name.replace('I', '')
            signals['ImmType'] = 'I'
        
        elif instruction_name in ['SLL', 'SRL', 'SRA']:
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 0
            signals['UseShift'] = 1
            signals['ShiftOp'] = instruction_name
            signals['ImmType'] = 'R'
        
        elif instruction_name in ['SLLI', 'SRLI', 'SRAI']:
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 1
            signals['UseShift'] = 1
            signals['ShiftOp'] = instruction_name.replace('I', '')
            signals['ImmType'] = 'I'
        
        elif instruction_name == 'LW':
            signals['RegWrite'] = 1
            signals['MemRead'] = 1
            signals['MemToReg'] = 1
            signals['ALUSrc'] = 1
            signals['ALUOp'] = 'ADD'
            signals['ImmType'] = 'I'
        
        elif instruction_name == 'SW':
            signals['MemWrite'] = 1
            signals['ALUSrc'] = 1
            signals['ALUOp'] = 'ADD'
            signals['ImmType'] = 'S'
        
        elif instruction_name in ['BEQ', 'BNE']:
            signals['Branch'] = 1
            signals['ALUSrc'] = 0
            signals['ALUOp'] = 'SUB'
            signals['ImmType'] = 'B'
        
        elif instruction_name == 'JAL':
            signals['RegWrite'] = 1
            signals['Jump'] = 1
            signals['ImmType'] = 'J'
        
        elif instruction_name == 'JALR':
            signals['RegWrite'] = 1
            signals['Jump'] = 1
            signals['ALUSrc'] = 1
            signals['ALUOp'] = 'ADD'
            signals['ImmType'] = 'I'
        
        elif instruction_name == 'LUI':
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 1
            signals['ALUOp'] = 'LUI'
            signals['ImmType'] = 'U'
        
        elif instruction_name == 'AUIPC':
            signals['RegWrite'] = 1
            signals['MemToReg'] = 0
            signals['ALUSrc'] = 1
            signals['ALUOp'] = 'ADD'
            signals['ImmType'] = 'U'
        
        return signals

