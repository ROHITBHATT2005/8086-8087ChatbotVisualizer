class Memory:
    def __init__(self, size=0x10000):
        self.size = size
        self.data = bytearray(size)
        
    def reset(self):
        self.data = bytearray(self.size)
        
    def read_byte(self, address):
        address &= 0xFFFF
        return self.data[address]
    
    def read_word(self, address):
        address &= 0xFFFF
        low = self.data[address]
        high = self.data[(address + 1) & 0xFFFF]
        return (high << 8) | low
    
    def write_byte(self, address, value):
        address &= 0xFFFF
        self.data[address] = value & 0xFF
        
    def write_word(self, address, value):
        address &= 0xFFFF
        self.data[address] = value & 0xFF
        self.data[(address + 1) & 0xFFFF] = (value >> 8) & 0xFF
        
    def dump(self, start, length=16):
        lines = []
        for i in range(start, start + length, 16):
            addr = i & 0xFFFF
            bytes_str = ' '.join(f'{self.data[addr+j]:02X}' for j in range(16) if addr+j < self.size)
            lines.append(f"{addr:04X}: {bytes_str}")
        return '\n'.join(lines)