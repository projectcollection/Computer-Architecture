"""CPU functionality."""

import sys

#opcodes
LDI     = 0b10000010
PRN     = 0b01000111 
MULT    = 0b10100010
ADD     = 0b10100000
HLT     = 0b00000001

PUSH    = 0b01000101
POP     = 0b01000110

CALL    = 0b01010000
RET     = 0b00010001

SP = 7

alu_op = {
    MULT:   "MULT",
    ADD:    "ADD"
}

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        capacity = 256
        self.ram = [0] * capacity
        self.reg = [0] * 8
        self.pc = 0
        self.reg[SP] = capacity - 1
        self.branchtable = {}
        self.branchtable[LDI] = self._LDI
        self.branchtable[PRN] = self._PRN
        self.branchtable['alu'] = self.alu
        self.branchtable[PUSH] = self._PUSH
        self.branchtable[POP] = self._POP
        self.branchtable[CALL] = self._CALL
        self.branchtable[RET] = self._RET

    def _LDI(self, inc):
        index = self.ram[self.pc + 1]
        self.reg[index] = self.ram[self.pc + 2]
        self.pc = self.pc + inc

    def _PRN(self, inc):
        index = self.ram[self.pc + 1]
        print(self.reg[index])
        self.pc = self.pc + inc

    def _MULT(self, inc):
        index_a = self.ram[self.pc + 1]
        index_b = self.ram[self.pc + 2]
        print(self.alu(alu_op[MULT], index_a, index_b))
        self.pc = self.pc + inc
       
    def _PUSH(self, inc):
        self.reg[SP] -= 1
        reg_index = self.ram_read(self.pc + 1)
        if self.reg[SP] != self.pc: #check if this is the right way to detect a stack overflow
            self.ram_write(self.reg[SP], self.reg[reg_index])
            self.pc = self.pc + inc
        else:
            print('stack overflow')
            sys.exit(2)

    def _POP(self, inc):
        reg_index = self.ram_read(self.pc + 1)
        if self.reg[SP] + 1 < len(self.ram):
            self.reg[reg_index] = self.ram_read(self.reg[SP])
            self.reg[SP] += 1
            self.pc = self.pc + inc
        else:
            print('bottom of stack')
            sys.exit(2)
    
    def _CALL(self, inc):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + inc
        
        reg_index = self.ram[self.pc + 1]
        self.pc = self.reg[reg_index]
    
    def _RET(self, _):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    def ram_read(self, index):
        return self.ram[index]

    def ram_write(self, index, value):
        self.ram[index] = value

    def load(self, file_name):
        """Load a program into memory."""

        file_extension = file_name.split('.')[-1]
        if file_extension != 'ls8':
            print(f".{file_extension} is unsupported.")
            sys.exit(2)
        
        try:
            address = 0
            with open(file_name, 'r') as f:
                all_lines = f.readlines()

                for instruction in all_lines:
                    op_code = instruction.split('#', 1)[0].strip()
                    if len(op_code) == 0:
                        continue
                    self.ram[address] = int(op_code, 2)
                    address += 1

        except FileNotFoundError:
            print(f'{file_name} does not exist.')
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == "MULT":
            return (self.reg[reg_a] * self.reg[reg_b])
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True

        while running:
            comm = self.ram[self.pc]
            inc = ((comm & 11000000) >> 6) + 1
            
            if comm in self.branchtable:
                self.branchtable[comm](inc)
            elif comm in alu_op:
                self.branchtable['alu'](alu_op[comm], self.ram_read(self.pc + 1), self.ram_read(self.pc + 2))
                self.pc = self.pc + inc
            elif comm == HLT:
                running = False
            else:
                print("unknown command")
                sys.exit(2)