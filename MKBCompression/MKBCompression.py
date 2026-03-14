import math

class BitStream:
    def __init__(self, data=None):
        self.buffer = bytearray(data) if data else bytearray()
        self.bit_offset = 0

    def write(self, value, bits):
        if bits <= 0: return
        for i in range(bits - 1, -1, -1):
            bit = (value >> i) & 1
            if self.bit_offset % 8 == 0:
                self.buffer.append(0)
            if bit:
                self.buffer[-1] |= (1 << (7 - (self.bit_offset % 8)))
            self.bit_offset += 1

    def read(self, bits):
        if bits <= 0: return 0
        value = 0
        for _ in range(bits):
            byte_idx = self.bit_offset // 8
            bit_idx = 7 - (self.bit_offset % 8)
            bit = (self.buffer[byte_idx] >> bit_idx) & 1
            value = (value << 1) | bit
            self.bit_offset += 1
        return value

def get_lehmer_code(sequence):
    elements = sorted(sequence)
    lehmer = []
    temp_sequence = list(sequence)
    for x in temp_sequence:
        idx = elements.index(x)
        lehmer.append(idx)
        elements.pop(idx)
    return lehmer

def decode_lehmer_code(lehmer, sorted_elements):
    elements = sorted(sorted_elements)
    res = []
    for idx in lehmer:
        res.append(elements.pop(idx))
    return res

def get_bits_needed(low, high):
    """Calculates bits needed to represent values in range [low, high] inclusive."""
    range_size = (high - low) + 1
    if range_size <= 1: return 0
    return (range_size - 1).bit_length()

class BSTProcessor:
    def __init__(self, sorted_vals=None):
        self.sorted_vals = sorted_vals
        self.result_map = {}

    def encode(self, stream, l_idx, r_idx, low_val, high_val):
        if l_idx > r_idx: return
        mid = (l_idx + r_idx) // 2
        val = self.sorted_vals[mid]
        
        bits = get_bits_needed(low_val, high_val)
        stream.write(val - low_val, bits)
        
        # BST Property: 
        # Left child range: [low_val, val - 1]
        # Right child range: [val + 1, high_val]
        self.encode(stream, l_idx, mid - 1, low_val, val - 1)
        self.encode(stream, mid + 1, r_idx, val + 1, high_val)

    def decode(self, stream, l_idx, r_idx, low_val, high_val):
        if l_idx > r_idx: return
        mid = (l_idx + r_idx) // 2
        
        bits = get_bits_needed(low_val, high_val)
        val_offset = stream.read(bits)
        actual_val = low_val + val_offset
        self.result_map[mid] = actual_val
        
        self.decode(stream, l_idx, mid - 1, low_val, actual_val - 1)
        self.decode(stream, mid + 1, r_idx, actual_val + 1, high_val)

def encode_56bit(input_str):
    """Encodes a 7-char string into exactly 7 bytes (56 bits)."""
    assert len(input_str) == 7, "This specific routine requires 7 characters"
    
    original = [ord(c) for c in input_str]
    sorted_vals = sorted(original)
    lehmer = get_lehmer_code(original)
    
    stream = BitStream()
    
    # 1. Lehmer Code: 14 bits total
    # (3+3+3+2+2+1 bits)
    for i in range(7):
        bits = (7 - 1 - i).bit_length()
        if bits > 0:
            stream.write(lehmer[i], bits)
            
    # 2. BST Sorted Values: ~42 bits
    bst = BSTProcessor(sorted_vals)
    bst.encode(stream, 0, 6, 0, 255)
    
    return bytes(stream.buffer)

def decode_56bit(bit_data):
    stream = BitStream(bit_data)
    n = 7
    
    # 1. Read Lehmer
    lehmer = []
    for i in range(n):
        bits = (n - 1 - i).bit_length()
        lehmer.append(stream.read(bits))
        
    # 2. Read BST Values
    bst = BSTProcessor()
    bst.decode(stream, 0, n - 1, 0, 255)
    sorted_vals = [bst.result_map[i] for i in range(n)]
    
    # 3. Reconstruct
    original_ords = decode_lehmer_code(lehmer, sorted_vals)
    return "".join(chr(x) for x in original_ords)

# --- Verification ---
example_chars = "".join([chr(231), chr(3), chr(45), chr(0), chr(23), chr(32), chr(78)])

encoded = encode_56bit(example_chars)
decoded = decode_56bit(encoded)

print(f"Input Ordinals: {[ord(c) for c in example_chars]}")
print(f"Encoded Hex:    {encoded.hex()}")
print(f"Total Bytes:    {len(encoded)} ({len(encoded)*8} bits)")
print(f"Match Success:  {example_chars == decoded}")