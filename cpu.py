"""
Single-cycle RISC-V CPU implementation
"""

from bit_utils import bits_to_int, int_to_bits, to_hex_string, from_hex_string
from registers import RegisterFile
from alu import ALU
from shifter import Shifter
from instruction_decoder import InstructionDecoder
from control_unit import ControlUnit
from memory import InstructionMemory, DataMemory

class CPU:
    def __init__(self, imem_size: int = 1024, dmem_size: int = 1024):
        self.reg_file = RegisterFile(32, 32)
        self.alu = ALU(32)
        self.shifter = Shifter(32)
        self.decoder = InstructionDecoder()
        self.control = ControlUnit()
        
        self.imem = InstructionMemory(imem_size, 0x00000000)
        self.dmem = DataMemory(dmem_size, 0x00010000)
        
        self.pc = 0x00000000
        
        self.halted = False
        self.cycle_count = 0
        self.instruction_count = 0
    
    def load_program(self, instructions: list[list[int]], start_address: int = 0x00000000):
        self.imem.load_program(instructions, start_address)
        self.pc = start_address
    
    def execute_cycle(self) -> bool:
        if self.halted:
            return False
        
        try:
            instruction = self.imem.read(self.pc)
        except ValueError:
            self.halted = True
            return False
        
        if all(bit == 0 for bit in instruction):
            if bits_to_int(instruction) == 0:
                self.halted = True
                return False
        
        decoded = self.decoder.decode(instruction)
        instr_name = self.decoder.get_instruction_name(decoded)
        
        if instr_name == 'JAL' and decoded['rd'] == 0:
            imm_j = bits_to_int(decoded['imm_j_sext'])
            if imm_j == 0:
                self.halted = True
                return False
        
        ctrl = self.control.generate_control_signals(decoded, instr_name)
        
        rs1_data = self.reg_file.read(decoded['rs1'])
        rs2_data = self.reg_file.read(decoded['rs2'])
        
        if ctrl['ALUSrc'] == 1:
            if ctrl['ImmType'] == 'I':
                alu_b = decoded['imm_i_sext']
            elif ctrl['ImmType'] == 'S':
                alu_b = decoded['imm_s_sext']
            elif ctrl['ImmType'] == 'U':
                alu_b = decoded['imm_u_sext']
            elif ctrl['ImmType'] == 'J':
                alu_b = decoded['imm_j_sext']
            else:
                alu_b = rs2_data
        else:
            alu_b = rs2_data
        
        if ctrl['UseShift'] == 1:
            if ctrl['ALUSrc'] == 1:
                if ctrl['ImmType'] == 'I':
                    shift_amount = decoded['imm_i'][7:12]
                else:
                    shift_amount = alu_b[27:32]
            else:
                shift_amount = rs2_data[27:32]
            result = self.shifter.execute(rs1_data, shift_amount, ctrl['ShiftOp'])
            alu_result = result
            alu_zero = all(bit == 0 for bit in result)
        elif ctrl['ALUOp'] == 'LUI':
            result = decoded['imm_u_sext']
            alu_result = result
            alu_zero = all(bit == 0 for bit in result)
        else:
            alu_result_dict = self.alu.execute(rs1_data, alu_b, ctrl['ALUOp'])
            alu_result = alu_result_dict['result']
            alu_zero = alu_result_dict['Z']
        
        mem_data = [0] * 32
        if ctrl['MemRead'] == 1:
            mem_addr = bits_to_int(alu_result)
            try:
                mem_data = self.dmem.read_word(mem_addr)
            except ValueError as e:
                print(f"Warning: Memory read error at {hex(mem_addr)}: {e}")
                mem_data = [0] * 32
        
        if ctrl['MemWrite'] == 1:
            mem_addr = bits_to_int(alu_result)
            try:
                self.dmem.write_word(mem_addr, rs2_data)
            except ValueError as e:
                print(f"Warning: Memory write error at {hex(mem_addr)}: {e}")
        
        if ctrl['MemToReg'] == 1:
            write_data = mem_data
        elif ctrl['Jump'] == 1:
            write_data = int_to_bits(self.pc + 4, 32)
        else:
            write_data = alu_result
        
        branch_taken = False
        if ctrl['Branch'] == 1:
            if instr_name == 'BEQ':
                branch_taken = (rs1_data == rs2_data)
            elif instr_name == 'BNE':
                branch_taken = (rs1_data != rs2_data)
        
        if ctrl['Jump'] == 1:
            if instr_name == 'JAL':
                next_pc = self.pc + bits_to_int(decoded['imm_j_sext'])
            elif instr_name == 'JALR':
                next_pc = (bits_to_int(rs1_data) + bits_to_int(decoded['imm_i_sext'])) & 0xFFFFFFFE
            else:
                next_pc = self.pc + 4
        elif branch_taken:
            next_pc = self.pc + bits_to_int(decoded['imm_b_sext'])
        else:
            next_pc = self.pc + 4
        
        if ctrl['RegWrite'] == 1:
            self.reg_file.write(decoded['rd'], write_data, enable=True)
        
        self.pc = next_pc
        
        self.reg_file.clock_edge()
        
        self.cycle_count += 1
        self.instruction_count += 1
        
        return True
    
    def run(self, max_cycles: int = 1000, verbose: bool = False) -> dict:
        initial_pc = self.pc
        
        while not self.halted and self.cycle_count < max_cycles:
            if verbose:
                print(f"Cycle {self.cycle_count}: PC = {hex(self.pc)}")
            
            if not self.execute_cycle():
                break
        
        return {
            'cycles': self.cycle_count,
            'instructions': self.instruction_count,
            'halted': self.halted,
            'final_pc': self.pc,
            'initial_pc': initial_pc
        }
    
    def reset(self):
        self.pc = 0x00000000
        self.halted = False
        self.cycle_count = 0
        self.instruction_count = 0
        
        for i in range(32):
            self.reg_file.write(i, [0] * 32, enable=False)
        self.reg_file.clock_edge()
    
    def get_state(self) -> dict:
        return {
            'pc': self.pc,
            'halted': self.halted,
            'cycle_count': self.cycle_count,
            'instruction_count': self.instruction_count,
            'registers': self.reg_file.dump_registers(),
            'data_memory': self.dmem.dump_memory()
        }

