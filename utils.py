def format_hex(val, width=4):
    return f"{val:0{width}X}"

def parse_number(s):
    s = s.strip()
    if s.lower().startswith('0x'):
        return int(s, 16)
    return int(s)

def format_flags(flags_dict):
    return ' '.join(f"{k}={v}" for k, v in flags_dict.items())