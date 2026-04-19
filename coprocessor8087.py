import math

class Coprocessor8087:
    def __init__(self):
        self.stack = [0.0] * 8
        self.top = 0
        self.status_word = 0
        self.control_word = 0x037F

    def reset(self):
        self.__init__()

    def _push(self, value):
        self.top = (self.top - 1) & 7
        self.stack[self.top] = float(value)

    def _pop(self):
        val = self.stack[self.top]
        self.stack[self.top] = 0.0
        self.top = (self.top + 1) & 7
        return val

    def _st(self, index=0):
        return self.stack[(self.top + index) & 7]

    def _set_st(self, index, value):
        self.stack[(self.top + index) & 7] = float(value)

    def execute(self, instruction):
        parts = instruction.strip().upper().replace(',', ' ').split()
        if not parts:
            return "Empty FPU instruction."
        mnemonic = parts[0]

        try:
            if mnemonic == 'FINIT':
                self.reset()
                return "FPU initialized."

            elif mnemonic == 'FLD':
                src = parts[1]
                if src.startswith('ST('):
                    idx = int(src[3:-1])
                    val = self._st(idx)
                else:
                    val = float(src)
                self._push(val)
                return f"Loaded {val} onto FPU stack."

            elif mnemonic == 'FST':
                return f"ST(0) = {self._st(0)}"

            elif mnemonic == 'FSTP':
                val = self._pop()
                return f"Stored and popped {val}. New top = {self._st(0)}"

            elif mnemonic == 'FADD':
                st1 = self._st(1)
                st0 = self._st(0)
                result = st1 + st0
                self._set_st(1, result)
                self._pop()
                return f"FADD: {st1} + {st0} = {result}"

            elif mnemonic == 'FSUB':
                st1 = self._st(1)
                st0 = self._st(0)
                result = st1 - st0
                self._set_st(1, result)
                self._pop()
                return f"FSUB: {st1} - {st0} = {result}"

            elif mnemonic == 'FSUBR':
                st1 = self._st(1)
                st0 = self._st(0)
                result = st0 - st1
                self._set_st(1, result)
                self._pop()
                return f"FSUBR: {st0} - {st1} = {result}"

            elif mnemonic == 'FMUL':
                st1 = self._st(1)
                st0 = self._st(0)
                result = st1 * st0
                self._set_st(1, result)
                self._pop()
                return f"FMUL: {st1} * {st0} = {result}"

            elif mnemonic == 'FDIV':
                st1 = self._st(1)
                st0 = self._st(0)
                if st0 == 0:
                    return "Error: Division by zero."
                result = st1 / st0
                self._set_st(1, result)
                self._pop()
                return f"FDIV: {st1} / {st0} = {result}"

            elif mnemonic == 'FDIVR':
                st1 = self._st(1)
                st0 = self._st(0)
                if st1 == 0:
                    return "Error: Division by zero."
                result = st0 / st1
                self._set_st(1, result)
                self._pop()
                return f"FDIVR: {st0} / {st1} = {result}"

            elif mnemonic == 'FSQRT':
                st0 = self._st(0)
                if st0 < 0:
                    return "Error: Square root of negative number."
                result = math.sqrt(st0)
                self._set_st(0, result)
                return f"FSQRT: sqrt({st0}) = {result}"

            elif mnemonic == 'FABS':
                self._set_st(0, abs(self._st(0)))
                return f"FABS: ST(0) = {self._st(0)}"

            elif mnemonic == 'FCHS':
                self._set_st(0, -self._st(0))
                return f"FCHS: ST(0) = {self._st(0)}"

            elif mnemonic == 'FCOM':
                st0 = self._st(0)
                st1 = self._st(1)
                if st0 == st1:
                    self.status_word = 0x4000
                elif st0 < st1:
                    self.status_word = 0x0100
                else:
                    self.status_word = 0x0000
                return f"Compared ST(0)={st0} with ST(1)={st1}. Status: {'EQ' if st0==st1 else 'LT' if st0<st1 else 'GT'}"

            elif mnemonic == 'FWAIT':
                return "FPU synchronized."

            else:
                return f"Unknown FPU instruction: {mnemonic}"

        except Exception as e:
            return f"FPU Error: {str(e)}"

    def get_stack_state(self):
        lines = []
        for i in range(8):
            idx = (self.top + i) & 7
            marker = "ST(0)" if i == 0 else f"ST({i})"
            lines.append(f"{marker}: {self.stack[idx]:.6f}")
        return '\n'.join(lines)