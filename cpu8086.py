from memory import Memory

class CPU8086:
    def __init__(self):
        self.ax = 0
        self.bx = 0
        self.cx = 0
        self.dx = 0
        
        self.si = 0
        self.di = 0
        self.bp = 0
        self.sp = 0xFFFF
        
        self.cs = 0
        self.ds = 0
        self.ss = 0
        self.es = 0
        
        self.ip = 0
        
        self.flags = {
            'CF': 0,
            'PF': 0,
            'AF': 0,
            'ZF': 0,
            'SF': 0,
            'TF': 0,
            'IF': 0,
            'DF': 0,
            'OF': 0
        }
        
        self.memory = Memory(0x10000)
        
    def reset(self):
        self.__init__()
        self.memory.reset()
        
    def _get_reg16(self, name):
        regs = {
            'AX': self.ax, 'BX': self.bx, 'CX': self.cx, 'DX': self.dx,
            'SI': self.si, 'DI': self.di, 'BP': self.bp, 'SP': self.sp,
            'CS': self.cs, 'DS': self.ds, 'SS': self.ss, 'ES': self.es,
            'IP': self.ip
        }
        return regs[name.upper()]
    
    def _set_reg16(self, name, value):
        value &= 0xFFFF
        if name.upper() == 'AX': self.ax = value
        elif name.upper() == 'BX': self.bx = value
        elif name.upper() == 'CX': self.cx = value
        elif name.upper() == 'DX': self.dx = value
        elif name.upper() == 'SI': self.si = value
        elif name.upper() == 'DI': self.di = value
        elif name.upper() == 'BP': self.bp = value
        elif name.upper() == 'SP': self.sp = value
        elif name.upper() == 'CS': self.cs = value
        elif name.upper() == 'DS': self.ds = value
        elif name.upper() == 'SS': self.ss = value
        elif name.upper() == 'ES': self.es = value
        elif name.upper() == 'IP': self.ip = value
    
    def _get_reg8(self, name):
        if name == 'AL': return self.ax & 0xFF
        elif name == 'AH': return (self.ax >> 8) & 0xFF
        elif name == 'BL': return self.bx & 0xFF
        elif name == 'BH': return (self.bx >> 8) & 0xFF
        elif name == 'CL': return self.cx & 0xFF
        elif name == 'CH': return (self.cx >> 8) & 0xFF
        elif name == 'DL': return self.dx & 0xFF
        elif name == 'DH': return (self.dx >> 8) & 0xFF
        return 0
    
    def _set_reg8(self, name, value):
        value &= 0xFF
        if name == 'AL': self.ax = (self.ax & 0xFF00) | value
        elif name == 'AH': self.ax = (self.ax & 0x00FF) | (value << 8)
        elif name == 'BL': self.bx = (self.bx & 0xFF00) | value
        elif name == 'BH': self.bx = (self.bx & 0x00FF) | (value << 8)
        elif name == 'CL': self.cx = (self.cx & 0xFF00) | value
        elif name == 'CH': self.cx = (self.cx & 0x00FF) | (value << 8)
        elif name == 'DL': self.dx = (self.dx & 0xFF00) | value
        elif name == 'DH': self.dx = (self.dx & 0x00FF) | (value << 8)
    
    def _get_operand_value(self, operand):
        op = operand.strip()
        if op.startswith('[') and op.endswith(']'):
            addr_expr = op[1:-1]
            if addr_expr in ['BX', 'SI', 'DI', 'BP']:
                addr = self._get_reg16(addr_expr)
            elif addr_expr.isdigit() or addr_expr.upper().startswith('0X'):
                addr = int(addr_expr, 0)
            else:
                addr = int(addr_expr, 0)
            return self.memory.read_word(addr)
        if op.isdigit() or (op.upper().startswith('0X') and all(c in '0123456789ABCDEFX' for c in op.upper())):
            return int(op, 0)
        if op in ['AL','AH','BL','BH','CL','CH','DL','DH']:
            return self._get_reg8(op)
        return self._get_reg16(op)
    
    def _set_operand_value(self, operand, value):
        op = operand.strip()
        if op.startswith('[') and op.endswith(']'):
            addr_expr = op[1:-1]
            if addr_expr in ['BX', 'SI', 'DI', 'BP']:
                addr = self._get_reg16(addr_expr)
            else:
                addr = int(addr_expr, 0)
            self.memory.write_word(addr, value & 0xFFFF)
        elif op in ['AL','AH','BL','BH','CL','CH','DL','DH']:
            self._set_reg8(op, value)
        else:
            self._set_reg16(op, value)
    
    def _update_flags(self, result, size=16, carry=0, overflow=0, auxiliary=0):
        mask = 0xFF if size == 8 else 0xFFFF
        result &= mask
        self.flags['ZF'] = 1 if result == 0 else 0
        self.flags['SF'] = 1 if (result & (0x80 if size==8 else 0x8000)) else 0
        self.flags['CF'] = carry
        self.flags['OF'] = overflow
        self.flags['AF'] = auxiliary
        self.flags['PF'] = 1 if bin(result & 0xFF).count('1') % 2 == 0 else 0
    
    def execute(self, instruction):
        parts = instruction.strip().upper().replace(',', ' ').split()
        if not parts:
            return "Empty instruction."
        mnemonic = parts[0]
        
        try:
            if mnemonic == 'MOV':
                dest, src = parts[1], parts[2]
                val = self._get_operand_value(src)
                self._set_operand_value(dest, val)
                return f"MOV {dest}, {src} : {dest} = {val} (hex: 0x{val:04X})"
            
            elif mnemonic == 'XCHG':
                op1, op2 = parts[1], parts[2]
                val1 = self._get_operand_value(op1)
                val2 = self._get_operand_value(op2)
                self._set_operand_value(op1, val2)
                self._set_operand_value(op2, val1)
                return f"XCHG {op1}, {op2} : {op1}={val2} (0x{val2:04X}), {op2}={val1} (0x{val1:04X})"
            
            elif mnemonic == 'LEA':
                dest, src = parts[1], parts[2]
                if src.startswith('[') and src.endswith(']'):
                    addr_expr = src[1:-1]
                    if addr_expr in ['BX','SI','DI','BP']:
                        addr = self._get_reg16(addr_expr)
                    else:
                        addr = int(addr_expr, 0)
                else:
                    return "LEA requires memory operand."
                self._set_reg16(dest, addr)
                return f"LEA {dest}, {src} : {dest} = {addr} (0x{addr:04X})"
            
            elif mnemonic == 'PUSH':
                src = parts[1]
                val = self._get_operand_value(src)
                self.sp = (self.sp - 2) & 0xFFFF
                self.memory.write_word(self.sp, val)
                return f"PUSH {src} : value {val} pushed to SP=0x{self.sp:04X}"
            
            elif mnemonic == 'POP':
                dest = parts[1]
                val = self.memory.read_word(self.sp)
                self.sp = (self.sp + 2) & 0xFFFF
                self._set_operand_value(dest, val)
                return f"POP {dest} : {dest} = {val} (0x{val:04X})"
            elif mnemonic == 'ADD':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 + op2
                carry = 1 if result > 0xFFFF else 0
                overflow = 1 if ((op1 & 0x8000) == (op2 & 0x8000) and (result & 0x8000) != (op1 & 0x8000)) else 0
                aux = 1 if ((op1 & 0xF) + (op2 & 0xF)) > 0xF else 0
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, carry, overflow, aux)
                return f"ADD {dest}, {src} → Result: {result & 0xFFFF} (hex: 0x{result & 0xFFFF:04X}) | Flags: ZF={self.flags['ZF']} CF={self.flags['CF']} OF={self.flags['OF']}"
            
            elif mnemonic == 'ADC':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 + op2 + self.flags['CF']
                carry = 1 if result > 0xFFFF else 0
                overflow = 1 if ((op1 & 0x8000) == (op2 & 0x8000) and (result & 0x8000) != (op1 & 0x8000)) else 0
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, carry, overflow)
                return f"ADC {dest}, {src} → Result: {result & 0xFFFF} (0x{result & 0xFFFF:04X}) | CF={self.flags['CF']}"
            
            elif mnemonic == 'SUB':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 - op2
                carry = 1 if op1 < op2 else 0
                overflow = 1 if ((op1 & 0x8000) != (op2 & 0x8000) and (result & 0x8000) != (op1 & 0x8000)) else 0
                self._set_operand_value(dest, result)
                self._update_flags(result & 0xFFFF, 16, carry, overflow)
                return f"SUB {dest}, {src} → Result: {result & 0xFFFF} (hex: 0x{result & 0xFFFF:04X}) | Flags: ZF={self.flags['ZF']} CF={self.flags['CF']} OF={self.flags['OF']}"
            
            elif mnemonic == 'SBB':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 - op2 - self.flags['CF']
                carry = 1 if (op1 - self.flags['CF']) < op2 else 0
                overflow = 1 if ((op1 & 0x8000) != (op2 & 0x8000) and (result & 0x8000) != (op1 & 0x8000)) else 0
                self._set_operand_value(dest, result)
                self._update_flags(result & 0xFFFF, 16, carry, overflow)
                return f"SBB {dest}, {src} → Result: {result & 0xFFFF} (0x{result & 0xFFFF:04X}) | CF={self.flags['CF']}"
            elif mnemonic == 'NEG':
                dest = parts[1]
                val = self._get_operand_value(dest)
                result = (-val) & 0xFFFF
                carry = 1 if val != 0 else 0
                overflow = 1 if val == 0x8000 else 0
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, carry, overflow)
                return f"NEG {dest} → Result: {result} (0x{result:04X}) | CF={carry} OF={overflow}"
            
            elif mnemonic == 'CBW':
                al = self.ax & 0xFF
                self.ax = al if (al & 0x80) == 0 else (al | 0xFF00)
                return f"CBW : AL sign-extended to AX = {self.ax} (0x{self.ax:04X})"
            
            elif mnemonic == 'CWD':
                self.dx = 0 if (self.ax & 0x8000) == 0 else 0xFFFF
                return f"CWD : DX = {self.dx:04X}, AX = {self.ax:04X}"
            
            elif mnemonic == 'MUL':
                src = parts[1]
                op = self._get_operand_value(src)
                result = self.ax * op
                self.ax = result & 0xFFFF
                self.dx = (result >> 16) & 0xFFFF
                carry = 1 if self.dx != 0 else 0
                self._update_flags(self.ax, 16, carry, 0)
                return f"MUL {src} → Result: {result} (hex: 0x{result:08X}) → AX={self.ax} (0x{self.ax:04X}), DX={self.dx} (0x{self.dx:04X}) | CF={self.flags['CF']}"
            
            elif mnemonic == 'DIV':
                src = parts[1]
                op = self._get_operand_value(src)
                if op == 0:
                    return "Error: Division by zero."
                dividend = (self.dx << 16) | self.ax
                quotient = dividend // op
                remainder = dividend % op
                if quotient > 0xFFFF:
                    return "Error: Division overflow."
                self.ax = quotient
                self.dx = remainder
                return f"DIV {src} → Quotient: {quotient} (0x{quotient:04X}), Remainder: {remainder} (0x{remainder:04X})"
            
            elif mnemonic == 'INC':
                dest = parts[1]
                val = self._get_operand_value(dest) + 1
                self._set_operand_value(dest, val)
                overflow = 1 if val == 0x8000 else 0
                self._update_flags(val, 16, self.flags['CF'], overflow)
                return f"INC {dest} → Result: {val & 0xFFFF} (hex: 0x{val & 0xFFFF:04X})"
            
            elif mnemonic == 'DEC':
                dest = parts[1]
                val = self._get_operand_value(dest) - 1
                self._set_operand_value(dest, val)
                overflow = 1 if val == 0x7FFF else 0
                self._update_flags(val, 16, self.flags['CF'], overflow)
                return f"DEC {dest} → Result: {val & 0xFFFF} (hex: 0x{val & 0xFFFF:04X})"

            elif mnemonic == 'AND':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 & op2
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, 0, 0)
                self.flags['OF'] = 0
                self.flags['CF'] = 0
                return f"AND {dest}, {src} → Result: {result} (hex: 0x{result:04X}) | Flags: ZF={self.flags['ZF']} SF={self.flags['SF']}"
            
            elif mnemonic == 'TEST':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 & op2
                self._update_flags(result, 16, 0, 0)
                self.flags['OF'] = 0
                self.flags['CF'] = 0
                return f"TEST {dest}, {src} : result {result} (0x{result:04X}) | ZF={self.flags['ZF']} SF={self.flags['SF']}"
            
            elif mnemonic == 'OR':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 | op2
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, 0, 0)
                self.flags['OF'] = 0
                self.flags['CF'] = 0
                return f"OR {dest}, {src} → Result: {result} (hex: 0x{result:04X}) | Flags: ZF={self.flags['ZF']} SF={self.flags['SF']}"
            
            elif mnemonic == 'XOR':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 ^ op2
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, 0, 0)
                self.flags['OF'] = 0
                self.flags['CF'] = 0
                return f"XOR {dest}, {src} → Result: {result} (hex: 0x{result:04X}) | Flags: ZF={self.flags['ZF']} SF={self.flags['SF']}"
            
            elif mnemonic == 'NOT':
                dest = parts[1]
                val = self._get_operand_value(dest)
                result = ~val & 0xFFFF
                self._set_operand_value(dest, result)
                return f"NOT {dest} → Result: {result} (hex: 0x{result:04X})"
            
            elif mnemonic == 'SHL':
                dest, count = parts[1], parts[2]
                val = self._get_operand_value(dest)
                cnt = int(count) if count.isdigit() else self._get_reg8('CL')
                result = (val << cnt) & 0xFFFF
                carry = 1 if (val & (1 << (16 - cnt))) else 0
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, carry, 0)
                return f"SHL {dest}, {cnt} → Result: {result} (hex: 0x{result:04X}) | CF={carry}"
            
            elif mnemonic == 'SHR':
                dest, count = parts[1], parts[2]
                val = self._get_operand_value(dest)
                cnt = int(count) if count.isdigit() else self._get_reg8('CL')
                result = val >> cnt
                carry = 1 if (val >> (cnt - 1)) & 1 else 0
                self._set_operand_value(dest, result)
                self._update_flags(result, 16, carry, 0)
                return f"SHR {dest}, {cnt} → Result: {result} (hex: 0x{result:04X}) | CF={carry}"
            elif mnemonic == 'STC':
                self.flags['CF'] = 1
                return "STC : CF set to 1"
            elif mnemonic == 'CLC':
                self.flags['CF'] = 0
                return "CLC : CF cleared to 0"
            elif mnemonic == 'CMC':
                self.flags['CF'] = 1 - self.flags['CF']
                return f"CMC : CF complemented to {self.flags['CF']}"
            elif mnemonic == 'CMP':
                dest, src = parts[1], parts[2]
                op1 = self._get_operand_value(dest)
                op2 = self._get_operand_value(src)
                result = op1 - op2
                carry = 1 if op1 < op2 else 0
                overflow = 1 if ((op1 & 0x8000) != (op2 & 0x8000) and (result & 0x8000) != (op1 & 0x8000)) else 0
                self._update_flags(result & 0xFFFF, 16, carry, overflow)
                return f"CMP {dest}, {src} : Flags updated (ZF={self.flags['ZF']}, CF={self.flags['CF']})"
            
            elif mnemonic in ['JMP', 'JE', 'JZ', 'JNE', 'JNZ', 'JC', 'JNC', 'JO', 'JNO', 'JS', 'JNS']:
                target = parts[1]
                if mnemonic == 'JMP':
                    return f"Unconditional jump to {target}"
                elif mnemonic in ['JE', 'JZ']:
                    return f"Jump if zero (ZF=1) to {target}: {'Taken' if self.flags['ZF'] else 'Not taken'}"
                elif mnemonic in ['JNE', 'JNZ']:
                    return f"Jump if not zero (ZF=0) to {target}: {'Taken' if not self.flags['ZF'] else 'Not taken'}"
                elif mnemonic == 'JC':
                    return f"Jump if carry (CF=1) to {target}: {'Taken' if self.flags['CF'] else 'Not taken'}"
                elif mnemonic == 'JNC':
                    return f"Jump if not carry (CF=0) to {target}: {'Taken' if not self.flags['CF'] else 'Not taken'}"
                else:
                    return f"Conditional jump {mnemonic} to {target}"
            
            elif mnemonic == 'LOOP':
                target = parts[1]
                self.cx = (self.cx - 1) & 0xFFFF
                return f"LOOP {target} : CX={self.cx} -> {'Jump' if self.cx != 0 else 'Fall through'}"
            elif mnemonic == 'LOOPE':
                target = parts[1]
                self.cx = (self.cx - 1) & 0xFFFF
                cond = (self.cx != 0) and (self.flags['ZF'] == 1)
                return f"LOOPE {target} : CX={self.cx}, ZF={self.flags['ZF']} -> {'Jump' if cond else 'Fall through'}"
            elif mnemonic == 'LOOPNE':
                target = parts[1]
                self.cx = (self.cx - 1) & 0xFFFF
                cond = (self.cx != 0) and (self.flags['ZF'] == 0)
                return f"LOOPNE {target} : CX={self.cx}, ZF={self.flags['ZF']} -> {'Jump' if cond else 'Fall through'}"
            
            elif mnemonic == 'CALL':
                target = parts[1]
                self.sp = (self.sp - 2) & 0xFFFF
                self.memory.write_word(self.sp, self.ip)
                return f"CALL {target} : return address pushed."
            
            elif mnemonic == 'RET':
                self.ip = self.memory.read_word(self.sp)
                self.sp = (self.sp + 2) & 0xFFFF
                return f"RET : returning to {self.ip:04X}"
            
            elif mnemonic == 'INT':
                num = parts[1]
                return f"Software interrupt {num} (simulated)."
            
            else:
                return f"Unknown instruction: {mnemonic}"
                
        except Exception as e:
            return f"CPU Error: {str(e)}"
    
    def get_state(self):
        lines = [
            f"AX={self.ax:04X}  BX={self.bx:04X}  CX={self.cx:04X}  DX={self.dx:04X}",
            f"SI={self.si:04X}  DI={self.di:04X}  BP={self.bp:04X}  SP={self.sp:04X}",
            f"CS={self.cs:04X}  DS={self.ds:04X}  SS={self.ss:04X}  ES={self.es:04X}  IP={self.ip:04X}",
            f"Flags: CF={self.flags['CF']} PF={self.flags['PF']} AF={self.flags['AF']} ZF={self.flags['ZF']} SF={self.flags['SF']} OF={self.flags['OF']}"
        ]
        return '\n'.join(lines)