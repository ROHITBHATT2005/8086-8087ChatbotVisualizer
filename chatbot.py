import re
import datetime
import random
import math
from cpu8086 import CPU8086
from coprocessor8087 import Coprocessor8087

class ChatBot:
    def __init__(self):
        self.cpu = CPU8086()
        self.fpu = Coprocessor8087()
        self.user_name = None
        self.state = "INIT"
        self.context = {}
        self.last_cpu_result = None
        self.last_fpu_result = None
        self.tutorial_step = 0
        self.tutorial_active = False

        self.jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "What's a microprocessor's favorite music? Heavy Metal!",
            "Why did the 8086 break up with the 8087? It needed more space!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem!",
        ]
        self.cpu_facts = {
            "architecture": "The 8086 is a 16-bit microprocessor with a 20-bit address bus, allowing access to 1MB of memory.",
            "registers": "8086 has four general-purpose 16-bit registers: AX, BX, CX, DX. Each can be split into high/low bytes (AH/AL, etc.).",
            "segment": "Memory is segmented: CS (code), DS (data), SS (stack), ES (extra). Physical address = segment * 16 + offset.",
            "flags": "Flags include CF (carry), ZF (zero), SF (sign), OF (overflow), PF (parity), AF (auxiliary), DF (direction), IF (interrupt), TF (trap).",
            "pipeline": "8086 uses a 6-byte prefetch queue to overlap instruction fetch and execution (pipelining).",
            "addressing": "Addressing modes: immediate, register, direct, register indirect, based, indexed, based-indexed.",
            "interrupts": "Supports 256 interrupts; INT 21h is DOS function dispatcher.",
            "mnemonics": "Common instructions: MOV, ADD, SUB, MUL, DIV, INC, DEC, AND, OR, XOR, NOT, SHL, SHR, JMP, CALL, RET.",
            "stack": "Stack grows downward; SP points to top. PUSH decrements SP, POP increments SP.",
            "alu": "16-bit ALU performs arithmetic and logical operations.",
            "bus": "Multiplexed address/data bus to save pins.",
            "minmax": "Can operate in minimum mode (single processor) or maximum mode (coprocessor/multiprocessor).",
            "coprocessor": "8087 NDP (Numeric Data Processor) adds floating-point hardware.",
            "clock": "Original speeds: 5, 8, 10 MHz.",
            "registers_special": "SI (source index), DI (destination index), BP (base pointer), SP (stack pointer).",
            "instruction_set": "Over 100 instructions, including string operations (MOVSB, STOSB, etc.).",
            "addressing_modes_detail": "Example: MOV AX, [BX+SI+10] uses based-indexed with displacement.",
            "flag_CF": "Carry Flag: set on unsigned overflow (addition carry-out or subtraction borrow).",
            "flag_OF": "Overflow Flag: set on signed overflow (result too large for destination).",
            "flag_ZF": "Zero Flag: set if result is zero.",
            "flag_SF": "Sign Flag: set to the most significant bit of result.",
            "effective_address": "EA = base + index + displacement (up to 3 components).",
            "instruction_encoding": "Instructions are 1 to 6 bytes long, including opcode, mod-reg-r/m, and displacement/immediate.",
            "real_mode": "8086 operates in real mode with no memory protection.",
            "prefetch": "BIU (Bus Interface Unit) prefetches instructions while EU (Execution Unit) executes.",
            "flag_AF": "Auxiliary Carry Flag: used for BCD arithmetic; set on carry/borrow from lower nibble.",
            "flag_PF": "Parity Flag: set if low byte of result has even number of 1 bits.",
            "flag_DF": "Direction Flag: controls auto-increment/decrement of SI/DI in string instructions.",
            "flag_IF": "Interrupt Flag: if set, maskable interrupts are enabled.",
            "flag_TF": "Trap Flag: if set, CPU single-steps (used for debugging).",
        }

    def process_input(self, user_input):
        user_input = user_input.strip()
        if not user_input:
            return "Please say something."

        text_lower = user_input.lower()
        if 'call me' in text_lower:
            match = re.search(r'call me\s+(.+)', text_lower)
            if match:
                self.user_name = match.group(1).strip().title()
                return f"Okay, I'll call you {self.user_name}."

        if 'my name is' in text_lower:
            match = re.search(r'my name is\s+(.+)', text_lower)
            if match:
                self.user_name = match.group(1).strip().title()
                return f"Nice to meet you, {self.user_name}!"

        if text_lower == 'help':
            return self._get_help()

        if self.tutorial_active:
            return self._handle_tutorial(user_input)

        cpu_result = self._try_cpu_command(user_input)
        if cpu_result is not None:
            return cpu_result

        fpu_result = self._try_fpu_command(user_input)
        if fpu_result is not None:
            return fpu_result

        edu = self._try_educational(user_input)
        if edu:
            return edu

        return self._handle_conversation(user_input)

    def _execute_program(self, program_text):
        lines = program_text.strip().split('\n')
        results = []
        line_number = 1
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                line_number += 1
                continue
                
            if line.startswith(';'):
                line_number += 1
                continue
                
            if ';' in line:
                line = line[:line.index(';')].strip()
                if not line:
                    line_number += 1
                    continue
            
            if ':' in line:
                if line.endswith(':'):
                    line_number += 1
                    continue
                parts = line.split(':', 1)
                if len(parts) > 1:
                    line = parts[1].strip()
                    if not line:
                        line_number += 1
                        continue
            
            try:
                res = self.cpu.execute(line)
                results.append(f"{line_number:02d}: {line}\n   => {res}")
            except Exception as e:
                results.append(f"{line_number:02d}: {line}\n   => Error: {str(e)}")
            
            line_number += 1
        
        if not results:
            return "No valid instructions found in program."
        
        return "📋 Program Execution Trace:\n" + "\n".join(results)
    def _try_cpu_command(self, text):
        upper_text = text.upper()
        if '.' in text:
            return None

        if self.last_cpu_result is not None:
            context_patterns = [
                (r'(?:ADD|PLUS)\s+(\d+)\s+TO\s+LAST\s+RESULT', 'ADD_LAST'),
                (r'ADD\s+LAST\s+RESULT\s+AND\s+(\d+)', 'ADD_LAST'),
                (r'SUB(?:TRACT)?\s+(\d+)\s+FROM\s+LAST\s+RESULT', 'SUB_LAST_REV'),
                (r'MUL(?:TIPLY)?\s+LAST\s+RESULT\s+BY\s+(\d+)', 'MUL_LAST'),
                (r'DIV(?:IDE)?\s+LAST\s+RESULT\s+BY\s+(\d+)', 'DIV_LAST'),
            ]
            for pattern, op_type in context_patterns:
                match = re.search(pattern, upper_text, re.IGNORECASE)
                if match:
                    val = int(match.group(1))
                    last = self.last_cpu_result
                    if op_type == 'ADD_LAST':
                        result = last + val
                        self.cpu.ax = last
                        cpu_res = self.cpu.execute(f"ADD AX, {val}")
                        self.last_cpu_result = result & 0xFFFF
                        return f"{cpu_res}\n\n📊 Contextual: {last} + {val} = {result & 0xFFFF}"
                    elif op_type == 'SUB_LAST_REV':
                        result = last - val
                        self.cpu.ax = last
                        cpu_res = self.cpu.execute(f"SUB AX, {val}")
                        self.last_cpu_result = result & 0xFFFF
                        return f"{cpu_res}\n\n📊 Contextual: {last} - {val} = {result & 0xFFFF}"
                    elif op_type == 'MUL_LAST':
                        result = last * val
                        self.cpu.ax = last
                        cpu_res = self.cpu.execute(f"MUL {val}")
                        self.last_cpu_result = result
                        return f"{cpu_res}\n\n📊 Contextual: {last} * {val} = {result}"
                    elif op_type == 'DIV_LAST':
                        if val == 0:
                            return "Division by zero error."
                        result = last // val
                        self.cpu.ax = last
                        self.cpu.dx = 0
                        cpu_res = self.cpu.execute(f"DIV {val}")
                        self.last_cpu_result = result
                        return f"{cpu_res}\n\n📊 Contextual: {last} / {val} = {result}"

        mem_match = re.search(r'store\s+(\d+)\s+at\s+\[?([0-9A-FX]+)\]?', upper_text, re.IGNORECASE)
        if mem_match:
            value = int(mem_match.group(1))
            addr_str = mem_match.group(2).replace('X', 'x')
            addr = int(addr_str, 0) & 0xFFFF
            self.cpu.memory.write_word(addr, value)
            return (f"📦 Stored {value} (0x{value:04X}) at memory address 0x{addr:04X}.\n"
                    f"   Little-endian: low byte {value & 0xFF:02X} at 0x{addr:04X}, "
                    f"high byte {(value>>8)&0xFF:02X} at 0x{(addr+1)&0xFFFF:04X}")

        mem_match = re.search(r'load\s+from\s+\[?([0-9A-FX]+|BX|SI|DI)\]?', upper_text, re.IGNORECASE)
        if mem_match:
            addr_expr = mem_match.group(1).upper()
            if addr_expr in ['BX','SI','DI']:
                addr = self.cpu._get_reg16(addr_expr)
            else:
                addr = int(addr_expr.replace('X','x'), 0) & 0xFFFF
            value = self.cpu.memory.read_word(addr)
            self.cpu.ax = value
            return f"📥 Loaded {value} (0x{value:04X}) from memory [0x{addr:04X}] into AX."

        mem_match = re.search(r'fill\s+([0-9A-FX]+)\s+to\s+([0-9A-FX]+)\s+with\s+(\d+)', upper_text, re.IGNORECASE)
        if mem_match:
            start = int(mem_match.group(1).replace('X','x'), 0) & 0xFFFF
            end = int(mem_match.group(2).replace('X','x'), 0) & 0xFFFF
            val = int(mem_match.group(3)) & 0xFF
            for addr in range(start, end+1):
                self.cpu.memory.write_byte(addr, val)
            return f"🧹 Filled memory 0x{start:04X}-0x{end:04X} with byte {val:02X}."

        mem_match = re.search(r'show mem(?:ory)?\s+(?:at\s+)?([0-9A-FX]+)', upper_text, re.IGNORECASE)
        if mem_match:
            addr = int(mem_match.group(1).replace('X','x'), 0) & 0xFFF0
            dump = self.cpu.memory.dump(addr, 64)
            return f"Memory dump starting at 0x{addr:04X}:\n{dump}"

        if 'show stack' in upper_text:
            sp = self.cpu.sp
            start = max(0, sp - 32)
            dump = self.cpu.memory.dump(start, 64)
            return f"Stack region (SP=0x{sp:04X}):\n{dump}"

        mnemonics = ['MOV', 'ADD', 'SUB', 'MUL', 'DIV', 'INC', 'DEC', 'CMP',
                     'AND', 'OR', 'XOR', 'NOT', 'SHL', 'SHR', 'PUSH', 'POP',
                     'XCHG', 'JMP', 'JE', 'JZ', 'JNE', 'JNZ', 'CALL', 'RET', 'INT',
                     'ADC', 'SBB', 'NEG', 'CBW', 'CWD', 'TEST', 'LEA', 'STC', 'CLC', 'CMC',
                     'LOOP', 'LOOPE', 'LOOPNE']
        first_word = upper_text.split()[0] if text.split() else ""
        if first_word in mnemonics:
            explanation = self._explain_8086_execution(text)
            result = self.cpu.execute(text)
            self.last_cpu_result = self._extract_result_value(result)
            return f"🔧 8086 Direct Instruction\n{result}\n\n📘 Explanation:\n{explanation}"

        patterns = [
            (r'SUB(?:TRACT)?\s+(\d+)\s+FROM\s+(\d+)', 'SUB_REV'),
            (r'(?:ADD|SUM|PLUS)\s+(\d+)\s+(?:AND|&|BY|TO|\+)?\s*(\d+)', 'ADD'),
            (r'(\d+)\s*\+\s*(\d+)', 'ADD'),
            (r'SUB(?:TRACT)?\s+(\d+)\s+(?:AND|&|BY)?\s*(\d+)', 'SUB'),
            (r'(\d+)\s*-\s*(\d+)', 'SUB'),
            (r'MUL(?:TIPLY)?\s+(\d+)\s+(?:AND|&|BY|TIMES|\*)?\s*(\d+)', 'MUL'),
            (r'(\d+)\s*\*\s*(\d+)', 'MUL'),
            (r'DIV(?:IDE)?\s+(\d+)\s+(?:BY|AND|&|\/)?\s*(\d+)', 'DIV'),
            (r'(\d+)\s*\/\s*(\d+)', 'DIV'),
            (r'AND\s+(\d+)\s+(?:WITH|AND|&)?\s*(\d+)', 'AND'),
            (r'(\d+)\s*&\s*(\d+)', 'AND'),
            (r'OR\s+(\d+)\s+(?:WITH|OR|\|)?\s*(\d+)', 'OR'),
            (r'(\d+)\s*\|\s*(\d+)', 'OR'),
            (r'XOR\s+(\d+)\s+(?:WITH|XOR|\^)?\s*(\d+)', 'XOR'),
            (r'(\d+)\s*\^\s*(\d+)', 'XOR'),
            (r'SHIFT\s+LEFT\s+(\d+)\s+(?:BY)?\s*(\d+)', 'SHL'),
            (r'SHL\s+(\d+)\s+(\d+)', 'SHL'),
            (r'(\d+)\s*<<\s*(\d+)', 'SHL'),
            (r'SHIFT\s+RIGHT\s+(\d+)\s+(?:BY)?\s*(\d+)', 'SHR'),
            (r'SHR\s+(\d+)\s+(\d+)', 'SHR'),
            (r'(\d+)\s*>>\s*(\d+)', 'SHR'),
        ]
        for pattern, op_type in patterns:
            match = re.search(pattern, upper_text)
            if match:
                return self._handle_arithmetic_match(op_type, match)

        if 'last result' in text.lower():
            return f"Last CPU result: {self.last_cpu_result}" if self.last_cpu_result is not None else "No CPU calculation yet."

        if any(phrase in upper_text for phrase in ['SHOW REG', 'REGISTER', 'CPU STATE']):
            return "Current CPU State:\n" + self.cpu.get_state()

        if 'show mem' in upper_text and 'at' not in upper_text and 'stack' not in upper_text:
            return "Memory Dump (first 64 bytes):\n" + self.cpu.memory.dump(0, 64)

        if 'RESET CPU' in upper_text:
            self.cpu.reset()
            self.last_cpu_result = None
            return "✅ CPU has been reset. All registers, flags, and memory cleared."

        return None

    def _handle_arithmetic_match(self, op_type, match):
        if op_type == 'ADD':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_arithmetic_8086('ADD', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"ADD AX, {b}")
            self.last_cpu_result = (a + b) & 0xFFFF
            return f"{result}\n\n{explanation}"
        elif op_type == 'SUB':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_arithmetic_8086('SUB', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"SUB AX, {b}")
            self.last_cpu_result = (a - b) & 0xFFFF
            return f"{result}\n\n{explanation}"
        elif op_type == 'SUB_REV':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_arithmetic_8086('SUB', b, a)
            self.cpu.ax = b
            result = self.cpu.execute(f"SUB AX, {a}")
            self.last_cpu_result = (b - a) & 0xFFFF
            return f"{result}\n\n{explanation}"
        elif op_type == 'MUL':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_arithmetic_8086('MUL', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"MUL {b}")
            self.last_cpu_result = a * b
            return f"{result}\n\n{explanation}"
        elif op_type == 'DIV':
            a, b = int(match.group(1)), int(match.group(2))
            if b == 0:
                return "Division by zero error."
            explanation = self._explain_arithmetic_8086('DIV', a, b)
            self.cpu.ax = a
            self.cpu.dx = 0
            result = self.cpu.execute(f"DIV {b}")
            self.last_cpu_result = a // b
            return f"{result}\n\n{explanation}"
        elif op_type == 'AND':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_logical_8086('AND', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"AND AX, {b}")
            self.last_cpu_result = a & b
            return f"{result}\n\n{explanation}"
        elif op_type == 'OR':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_logical_8086('OR', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"OR AX, {b}")
            self.last_cpu_result = a | b
            return f"{result}\n\n{explanation}"
        elif op_type == 'XOR':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_logical_8086('XOR', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"XOR AX, {b}")
            self.last_cpu_result = a ^ b
            return f"{result}\n\n{explanation}"
        elif op_type == 'SHL':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_shift_8086('SHL', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"SHL AX, {b}")
            self.last_cpu_result = (a << b) & 0xFFFF
            return f"{result}\n\n{explanation}"
        elif op_type == 'SHR':
            a, b = int(match.group(1)), int(match.group(2))
            explanation = self._explain_shift_8086('SHR', a, b)
            self.cpu.ax = a
            result = self.cpu.execute(f"SHR AX, {b}")
            self.last_cpu_result = a >> b
            return f"{result}\n\n{explanation}"
        return "Operation not handled."

    def _extract_result_value(self, result_str):
        match = re.search(r'Result:\s*(\d+)', result_str)
        if match:
            return int(match.group(1))
        match = re.search(r'=\s*(\d+)', result_str)
        if match:
            return int(match.group(1))
        return None

    def _explain_8086_execution(self, instruction):
        parts = instruction.strip().upper().replace(',', ' ').split()
        mnemonic = parts[0]
        explanations = {
            'MOV': "The MOV instruction transfers data from source to destination.\n"
                   "Step 1: CPU fetches the instruction from memory.\n"
                   "Step 2: Decodes it as a data transfer operation.\n"
                   "Step 3: Reads the source operand (register or immediate).\n"
                   "Step 4: Writes the value to the destination register.",
            'ADD': "The ADD instruction performs integer addition.\n"
                   "Step 1: CPU fetches the instruction.\n"
                   "Step 2: ALU receives the two operands.\n"
                   "Step 3: Performs binary addition.\n"
                   "Step 4: Updates destination register and flags (ZF, SF, CF, OF).",
            'SUB': "The SUB instruction subtracts source from destination.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: ALU computes destination - source using two's complement addition.\n"
                   "Step 3: Result stored in destination; flags updated.",
            'MUL': "MUL performs unsigned multiplication.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: Multiplies AX by the source operand.\n"
                   "Step 3: 32-bit result stored in DX:AX (high word in DX, low in AX).\n"
                   "Step 4: CF and OF set if DX != 0.",
            'DIV': "DIV performs unsigned division.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: Divides DX:AX (32-bit) by the source operand.\n"
                   "Step 3: Quotient stored in AX, remainder in DX.\n"
                   "Step 4: If quotient exceeds 16 bits, an interrupt is generated (simulated).",
            'AND': "AND performs bitwise logical AND.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: ALU computes bitwise AND between operands.\n"
                   "Step 3: Result stored in destination; CF=OF=0, SF/ZF/PF updated.",
            'OR': "OR performs bitwise logical OR.\n"
                  "Step 1: Fetch and decode.\n"
                  "Step 2: ALU computes bitwise OR.\n"
                  "Step 3: Result stored; CF=OF=0, SF/ZF/PF updated.",
            'XOR': "XOR performs bitwise exclusive OR.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: ALU computes XOR.\n"
                   "Step 3: Result stored; CF=OF=0, SF/ZF/PF updated.",
            'SHL': "SHL shifts bits left by count.\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: Shift left count times; bits shifted out go to CF.\n"
                   "Step 3: Zero fills right side; OF set if sign bit changes.",
            'SHR': "SHR shifts bits right by count (logical shift).\n"
                   "Step 1: Fetch and decode.\n"
                   "Step 2: Shift right; LSB -> CF; zero fills MSB.\n"
                   "Step 3: OF undefined for count > 1.",
            'PUSH': "PUSH decrements SP by 2 and stores the operand on the stack.",
            'POP': "POP loads the operand from the stack and increments SP by 2.",
        }
        return explanations.get(mnemonic, "Instruction executed using 8086 fetch-decode-execute cycle.")

    def _explain_arithmetic_8086(self, op, a, b):
        if op == 'ADD':
            result = a + b
            binary_a = f"{a:016b}"
            binary_b = f"{b:016b}"
            binary_result = f"{result & 0xFFFF:016b}"
            return (f"=== 8086 ADD Operation ===\n"
                    f"1. MOV AX, {a}  ; Load first number into AX register\n"
                    f"2. ADD AX, {b}  ; Add second number to AX\n"
                    f"   AX before: {a} (binary: {binary_a})\n"
                    f"   + operand: {b} (binary: {binary_b})\n"
                    f"   = result:   {result & 0xFFFF} (binary: {binary_result})\n"
                    f"3. Flags updated: ZF={'1' if result & 0xFFFF == 0 else '0'}, "
                    f"CF={'1' if result > 0xFFFF else '0'}, "
                    f"OF={'1' if ((a & 0x8000) == (b & 0x8000) and (result & 0x8000) != (a & 0x8000)) else '0'}")
        elif op == 'SUB':
            result = a - b
            return (f"=== 8086 SUB Operation ===\n"
                    f"1. MOV AX, {a}\n"
                    f"2. SUB AX, {b}\n"
                    f"   AX before: {a} (0x{a:04X})\n"
                    f"   - operand:  {b} (0x{b:04X})\n"
                    f"   = result:   {result & 0xFFFF} (0x{result & 0xFFFF:04X})\n"
                    f"3. Flags: ZF={'1' if result & 0xFFFF == 0 else '0'}, "
                    f"CF={'1' if a < b else '0'}, "
                    f"SF={'1' if (result & 0x8000) else '0'}")
        elif op == 'MUL':
            result = a * b
            high = (result >> 16) & 0xFFFF
            low = result & 0xFFFF
            return (f"=== 8086 MUL Operation ===\n"
                    f"1. MOV AX, {a}\n"
                    f"2. MUL {b}  ; Multiply AX by {b}\n"
                    f"   AX = {a} (0x{a:04X})\n"
                    f"   * {b} = {result} (0x{result:08X})\n"
                    f"   Result: DX (high) = {high} (0x{high:04X}), AX (low) = {low} (0x{low:04X})\n"
                    f"3. CF=OF={'1' if high != 0 else '0'} ({'set because high word non-zero' if high != 0 else 'clear'})")
        elif op == 'DIV':
            if b == 0:
                return "Division by zero error."
            quotient = a // b
            remainder = a % b
            return (f"=== 8086 DIV Operation ===\n"
                    f"1. MOV AX, {a}  ; Dividend low word\n"
                    f"2. MOV DX, 0    ; Dividend high word (zero for 16-bit division)\n"
                    f"3. DIV {b}      ; Divide DX:AX by {b}\n"
                    f"   DX:AX = 0x0000{a:04X} = {a}\n"
                    f"   / {b} = quotient {quotient} (0x{quotient:04X}), remainder {remainder} (0x{remainder:04X})\n"
                    f"4. AX = {quotient}, DX = {remainder}")
        else:
            return f"Performed {op} operation using 8086 ALU."

    def _explain_logical_8086(self, op, a, b):
        if op == 'AND':
            result = a & b
            binary_a = f"{a:016b}"
            binary_b = f"{b:016b}"
            binary_result = f"{result:016b}"
            return (f"=== 8086 AND Operation ===\n"
                    f"1. MOV AX, {a}  ; {binary_a}\n"
                    f"2. AND AX, {b}  ; {binary_b}\n"
                    f"   Bitwise AND:\n"
                    f"   {binary_a}\n"
                    f"   &\n"
                    f"   {binary_b}\n"
                    f"   =\n"
                    f"   {binary_result} = {result} (0x{result:04X})\n"
                    f"3. CF=0, OF=0, ZF={'1' if result==0 else '0'}, SF={'1' if (result & 0x8000) else '0'}")
        elif op == 'OR':
            result = a | b
            return (f"=== 8086 OR Operation ===\n"
                    f"1. MOV AX, {a}\n"
                    f"2. OR AX, {b}\n"
                    f"   Bitwise OR yields: {result} (0x{result:04X})\n"
                    f"3. CF=0, OF=0, flags updated.")
        elif op == 'XOR':
            result = a ^ b
            return (f"=== 8086 XOR Operation ===\n"
                    f"1. MOV AX, {a}\n"
                    f"2. XOR AX, {b}\n"
                    f"   Bitwise XOR yields: {result} (0x{result:04X})\n"
                    f"3. CF=0, OF=0, flags updated.")
        return f"{op} operation executed."

    def _explain_shift_8086(self, op, a, count):
        if op == 'SHL':
            result = (a << count) & 0xFFFF
            carry = 1 if (a & (1 << (16 - count))) else 0
            binary_a = f"{a:016b}"
            binary_result = f"{result:016b}"
            return (f"=== 8086 SHL (Shift Left) ===\n"
                    f"1. MOV AX, {a}  ; {binary_a}\n"
                    f"2. SHL AX, {count}  ; Shift left {count} bit(s)\n"
                    f"   Before: {binary_a}\n"
                    f"   After:  {binary_result} (shifted left, LSBs zero-filled)\n"
                    f"   Result: {result} (0x{result:04X})\n"
                    f"3. CF={carry} (last bit shifted out), OF updated.")
        elif op == 'SHR':
            result = a >> count
            carry = 1 if (a >> (count - 1)) & 1 else 0
            return (f"=== 8086 SHR (Shift Right) ===\n"
                    f"1. MOV AX, {a}\n"
                    f"2. SHR AX, {count}  ; Logical shift right\n"
                    f"   Result: {result} (0x{result:04X})\n"
                    f"3. CF={carry} (last bit shifted out).")
        return f"{op} executed."

    def _try_fpu_command(self, text):
        upper_text = text.upper()
        fpu_mnemonics = ['FINIT', 'FLD', 'FST', 'FSTP', 'FADD', 'FSUB', 'FSUBR',
                         'FMUL', 'FDIV', 'FDIVR', 'FSQRT', 'FABS', 'FCHS', 'FCOM', 'FWAIT']
        first_word = upper_text.split()[0] if text.split() else ""
        if first_word in fpu_mnemonics:
            explanation = self._explain_fpu_execution(text)
            result = self.fpu.execute(text)
            self.last_fpu_result = self._extract_fpu_result(result)
            return f"🔧 8087 FPU Instruction\n{result}\n\n📘 Explanation:\n{explanation}"

        patterns = [
            (r'(?:WHAT IS|CALCULATE|COMPUTE)?\s*SQRT\s+OF\s+([\d.]+)', 'FSQRT'),
            (r'SQRT\s+([\d.]+)', 'FSQRT'),
            (r'ADD\s+([\d.]+)\s+(?:AND|&|\+)?\s*([\d.]+)', 'FADD'),
            (r'([\d.]+)\s*\+\s*([\d.]+)', 'FADD'),
            (r'SUBTRACT\s+([\d.]+)\s+FROM\s+([\d.]+)', 'FSUBR'),
            (r'([\d.]+)\s*-\s*([\d.]+)', 'FSUB'),
            (r'MULTIPLY\s+([\d.]+)\s+(?:BY|AND|TIMES|\*)?\s*([\d.]+)', 'FMUL'),
            (r'([\d.]+)\s*\*\s*([\d.]+)', 'FMUL'),
            (r'DIVIDE\s+([\d.]+)\s+BY\s+([\d.]+)', 'FDIV'),
            (r'([\d.]+)\s*\/\s*([\d.]+)', 'FDIV'),
        ]
        for pattern, op in patterns:
            match = re.search(pattern, upper_text, re.IGNORECASE)  # <-- FIX HERE
            if match:
                if op == 'FSQRT':
                    val = float(match.group(1))
                    self.fpu._push(val)
                    explanation = self._explain_fpu_op('FSQRT', val, None)
                    result = self.fpu.execute('FSQRT')
                    self.last_fpu_result = math.sqrt(val)
                    return f"{result}\n\n{explanation}"
                elif op in ['FADD','FSUB','FSUBR','FMUL','FDIV']:
                    a = float(match.group(1))
                    b = float(match.group(2))
                    if op == 'FADD':
                        self.fpu._push(a); self.fpu._push(b)
                        explanation = self._explain_fpu_op('FADD', a, b)
                        result = self.fpu.execute('FADD')
                        self.last_fpu_result = a + b
                    elif op == 'FSUB':
                        self.fpu._push(a); self.fpu._push(b)
                        explanation = self._explain_fpu_op('FSUB', a, b)
                        result = self.fpu.execute('FSUB')
                        self.last_fpu_result = a - b
                    elif op == 'FSUBR':
                        self.fpu._push(b); self.fpu._push(a)
                        explanation = self._explain_fpu_op('FSUBR', a, b)
                        result = self.fpu.execute('FSUBR')
                        self.last_fpu_result = b - a
                    elif op == 'FMUL':
                        self.fpu._push(a); self.fpu._push(b)
                        explanation = self._explain_fpu_op('FMUL', a, b)
                        result = self.fpu.execute('FMUL')
                        self.last_fpu_result = a * b
                    elif op == 'FDIV':
                        if b == 0:
                            return "Division by zero error."
                        self.fpu._push(a); self.fpu._push(b)
                        explanation = self._explain_fpu_op('FDIV', a, b)
                        result = self.fpu.execute('FDIV')
                        self.last_fpu_result = a / b
                    return f"{result}\n\n{explanation}"

        if 'last fpu result' in text.lower():
            return f"Last FPU result: {self.last_fpu_result}" if self.last_fpu_result is not None else "No FPU calculation yet."

        if 'fpu stack' in upper_text:
            return "FPU Stack:\n" + self.fpu.get_stack_state()

        if 'RESET FPU' in upper_text:
            self.fpu.reset()
            self.last_fpu_result = None
            return "✅ FPU has been reset. Stack cleared."

        return None
    
    def _extract_fpu_result(self, result_str):
        match = re.search(r'=\s*([\d.]+)', result_str)
        return float(match.group(1)) if match else None

    def _explain_fpu_execution(self, instruction):
        parts = instruction.strip().upper().replace(',', ' ').split()
        mnemonic = parts[0]
        explanations = {
            'FLD': "FLD loads a floating-point value onto the FPU stack.\n"
                   "Step 1: Decrement stack pointer (TOP).\n"
                   "Step 2: Convert value to 80-bit extended precision.\n"
                   "Step 3: Store at new ST(0).",
            'FADD': "FADD adds ST(0) to ST(1) and pops the stack.\n"
                    "Step 1: Fetch ST(0) and ST(1).\n"
                    "Step 2: Perform addition using 80-bit hardware.\n"
                    "Step 3: Store result in ST(1), then pop (increment TOP).",
            'FMUL': "FMUL multiplies ST(0) and ST(1), result in ST(1), pop.",
            'FDIV': "FDIV divides ST(1) by ST(0), pop.",
            'FSQRT': "FSQRT replaces ST(0) with its square root.",
        }
        return explanations.get(mnemonic, "FPU instruction executed with 80-bit precision.")

    def _explain_fpu_op(self, op, a, b=None):
        if op == 'FSQRT':
            res = math.sqrt(a)
            return (f"=== 8087 FSQRT Operation ===\n"
                    f"1. FLD {a}  ; Load value onto FPU stack\n"
                    f"2. FSQRT    ; Compute square root\n"
                    f"   ST(0) = sqrt({a}) = {res}\n"
                    f"3. Result left in ST(0).")
        elif op == 'FADD':
            res = a + b
            return (f"=== 8087 FADD Operation ===\n"
                    f"1. FLD {a}  ; Push first number\n"
                    f"2. FLD {b}  ; Push second number\n"
                    f"3. FADD      ; ST(1) = ST(1) + ST(0), pop\n"
                    f"   {a} + {b} = {res}\n"
                    f"4. Result in ST(0).")
        elif op == 'FSUB':
            res = a - b
            return (f"=== 8087 FSUB Operation ===\n"
                    f"1. FLD {a}\n2. FLD {b}\n3. FSUB  ; ST(1) = ST(1) - ST(0), pop\n"
                    f"   {a} - {b} = {res}")
        elif op == 'FSUBR':
            res = b - a
            return (f"=== 8087 FSUBR Operation ===\n"
                    f"1. FLD {b}\n2. FLD {a}\n3. FSUBR ; ST(1) = ST(0) - ST(1), pop\n"
                    f"   {b} - {a} = {res}")
        elif op == 'FMUL':
            res = a * b
            return (f"=== 8087 FMUL Operation ===\n"
                    f"1. FLD {a}\n2. FLD {b}\n3. FMUL  ; {a} * {b} = {res}")
        elif op == 'FDIV':
            if b == 0:
                return "Division by zero error."
            res = a / b
            return (f"=== 8087 FDIV Operation ===\n"
                    f"1. FLD {a}\n2. FLD {b}\n3. FDIV  ; {a} / {b} = {res}")
        return f"FPU {op} executed."

    def _try_educational(self, text):
        text_lower = text.lower()
        for keyword, fact in self.cpu_facts.items():
            if keyword in text_lower:
                return f"📚 8086 Fact about {keyword}:\n{fact}"
        if "tell me about 8086" in text_lower or "what is 8086" in text_lower:
            return self.cpu_facts["architecture"]
        if "list facts" in text_lower:
            facts = "\n".join([f"• {v}" for k,v in list(self.cpu_facts.items())[:10]])
            return f"Here are some 8086 facts:\n{facts}\n... ask about specific topics."
        return None

    def _start_tutorial(self):
        self.tutorial_active = True
        self.tutorial_step = 1
        return ("🎓 8086 Assembly Tutorial Started!\n"
                "We'll write a simple program step by step.\n"
                "First, let's move a number into AX. Type: MOV AX, 5")

    def _handle_tutorial(self, text):
        if not self.tutorial_active:
            return None
        step = self.tutorial_step
        response = ""
        if step == 1:
            if re.match(r'MOV\s+AX,\s*\d+', text.upper()):
                self.cpu.execute(text)
                response = "Good! Now add another number. Type: ADD AX, 3"
                self.tutorial_step = 2
            else:
                response = "Try: MOV AX, 5"
        elif step == 2:
            if re.match(r'ADD\s+AX,\s*\d+', text.upper()):
                self.cpu.execute(text)
                response = "Great! The result is in AX. Now let's store it in BX. Type: MOV BX, AX"
                self.tutorial_step = 3
            else:
                response = "Try: ADD AX, 3"
        elif step == 3:
            if re.match(r'MOV\s+BX,\s*AX', text.upper()):
                self.cpu.execute(text)
                response = "Excellent! You've completed the basic tutorial. Type 'show registers' to see the result.\nTutorial finished."
                self.tutorial_active = False
            else:
                response = "Try: MOV BX, AX"
        return response

    def _handle_conversation(self, text):
        text_lower = text.lower()
        if self.state == "INIT":
            self.state = "ASK_NAME"
            return "Hello! I'm your advanced MPMC chatbot with 8086 CPU and 8087 FPU simulation. What's your name?"
        elif self.state == "ASK_NAME":
            self.user_name = text.strip()
            self.state = "CONVERSATION"
            return (f"Nice to meet you, {self.user_name}! I can perform arithmetic using 8086 instructions, "
                    f"floating-point math with 8087, and have a memory subsystem.\n"
                    f"Type 'help' to see what I can do.")
        elif self.state == "CONVERSATION":
            if any(word in text_lower for word in ['hello', 'hi', 'hey', 'greetings']):
                return f"Hello {self.user_name}! How can I help you today?"
            if 'help' in text_lower:
                return self._get_help()
            if 'call me' in text_lower:
                match = re.search(r'call me\s+(.+)', text_lower)
                if match:
                    self.user_name = match.group(1).strip().title()
                    return f"Okay, I'll call you {self.user_name}."
            elif 'my name is' in text_lower:
                match = re.search(r'my name is\s+(.+)', text_lower)
                if match:
                    self.user_name = match.group(1).strip().title()
                    return f"Nice to meet you, {self.user_name}!"
            if 'my name' in text_lower or 'who am i' in text_lower:
                return f"Your name is {self.user_name}." if self.user_name else "I don't know your name yet."
            if 'time' in text_lower:
                return datetime.datetime.now().strftime('%H:%M:%S')
            if 'date' in text_lower:
                return datetime.datetime.now().strftime('%B %d, %Y')
            if 'joke' in text_lower or 'funny' in text_lower:
                return random.choice(self.jokes)
            if any(word in text_lower for word in ['bye', 'goodbye', 'exit', 'quit']):
                return f"Goodbye {self.user_name}! It was nice talking to you."
            return "I'm not sure how to respond. You can ask me to do calculations, show CPU state, or just chat. Type 'help' for options."

    def _get_help(self):
        return """
📋 Available Commands:

🔹 Natural Arithmetic:
   • "add 5 6" or "5 + 6"
   • "subtract 3 from 10" or "10 - 3"
   • "multiply 5 by 6" or "5 * 6"
   • "divide 10 by 2" or "10 / 2"
   • "and 5 and 3" or "5 & 3"
   • "or 5 or 3" or "5 | 3"
   • "xor 5 xor 3" or "5 ^ 3"
   • "shift left 5 by 2" or "5 << 2"
   • "shift right 10 by 1" or "10 >> 1"

🔹 Floating-Point (8087):
   • "sqrt of 9" or "sqrt 16"
   • "add 3.14 and 2.86" or "3.14 + 2.86"
   • "multiply 2.5 by 4" or "2.5 * 4"

🔹 Direct 8086 Instructions:
   MOV, ADD, SUB, MUL, DIV, INC, DEC, CMP, AND, OR, XOR, NOT, SHL, SHR, PUSH, POP, XCHG, JMP, CALL, RET
   Example: "MOV AX, 5" then "ADD AX, 3"

🔹 Advanced Direct 8086:
   ADC, SBB, NEG, CBW, CWD, TEST, LEA, STC, CLC, CMC, LOOP, LOOPE, LOOPNE

🔹 8087 FPU Instructions:
   FINIT, FLD, FADD, FSUB, FMUL, FDIV, FSQRT, etc.

🔹 Memory Commands:
   • "store 1234 at 1000"
   • "load from [1000]" or "load from [BX]"
   • "fill 1000 to 100F with 55"
   • "show memory at 1000"
   • "show stack"

🔹 Multi-line Program:
   Type "run program" to open an editor.

🔹 Educational Q&A:
   • "tell me about 8086"
   • "what are flags?"
   • "explain pipelining"
   • "list facts"

🔹 Interactive Tutorial:
   Type "tutorial" to start a guided assembly lesson.

🔹 Contextual Memory:
   • "add 5 to last result"
   • "multiply last result by 3"

🔹 System Commands:
   • "show registers" / "show cpu state"
   • "show memory"
   • "fpu stack"
   • "reset cpu" / "reset fpu"

🔹 Chat:
   • "what's my name", "call me [name]"
   • "time", "date", "tell me a joke"
   • "bye" to exit
"""