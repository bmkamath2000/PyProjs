#!/usr/bin/env python3
"""
MKBCompression v2 -- block-wise Lehmer-code + BST compressor for any file.

Pipeline per block of N bytes (N in 7, 15, 127, 255, or a short tail block):

  1. Sort the block.  The sorted values are stored as a balanced BST in
     pre-order, each node using the fewest bits its [low, high] window allows
     (same idea as BSTProcessor in MKBCompression.py).
  2. The original order is stored as a Lehmer code, packed as ONE mixed-radix
     integer (ceil(log2(#arrangements)) bits) instead of one field per digit.
     For distinct values this is exactly the classic Lehmer / factorial-base
     number; for repeated values it is the multiset generalisation, so
     duplicates cost nothing extra.

Changes versus the original routine
  * works on any byte stream, any length (tail block handled, length in header)
  * duplicates are handled (the original BST needed distinct values)
  * the BST window is tightened: strictly-increasing transform t[k] = s[k] + k
    lets every node reserve room for its left/right subtree
  * file-level min/max byte narrows the value range (text -> ~7 bits, not 8)
  * Lehmer code is computed with a Fenwick tree, O(n log n) instead of O(n^2)
  * bit I/O uses an integer accumulator instead of one bit per loop turn
  * --block auto benchmarks 7/15/127/255 on a sample and picks the best

Usage
  python MKBCompression_v2.py c  in.bin out.mkb [-b auto|7|15|127|255]
  python MKBCompression_v2.py d  out.mkb restored.bin
  python MKBCompression_v2.py bench in.bin
  python MKBCompression_v2.py selftest
"""
import argparse
import os
import struct
import sys
import time
from functools import lru_cache

MAGIC = b"MKB2"
HEADER = struct.Struct(">4sBBBQ")  # magic, block, lo, hi, original length
BLOCK_CHOICES = (7, 15, 127, 255)

FACT = [1]
for _i in range(1, 256):
    FACT.append(FACT[-1] * _i)


# --------------------------------------------------------------------------
# Bit I/O
# --------------------------------------------------------------------------
class BitWriter:
    __slots__ = ("out", "acc", "nbits")

    def __init__(self):
        self.out = bytearray()
        self.acc = 0
        self.nbits = 0

    def write(self, value, bits):
        if bits <= 0:
            return
        self.acc = (self.acc << bits) | value
        self.nbits += bits
        if self.nbits >= 4096:
            self._flush()

    def _flush(self):
        nbytes = self.nbits >> 3
        if nbytes:
            keep = self.nbits - nbytes * 8
            self.out += (self.acc >> keep).to_bytes(nbytes, "big")
            self.acc &= (1 << keep) - 1
            self.nbits = keep

    def getvalue(self):
        pad = (-self.nbits) % 8
        self.acc <<= pad
        self.nbits += pad
        self._flush()
        return bytes(self.out)


class BitReader:
    __slots__ = ("data", "pos", "limit")

    def __init__(self, data, start_byte=0):
        self.data = data
        self.pos = start_byte * 8
        self.limit = len(data) * 8

    def read(self, bits):
        if bits <= 0:
            return 0
        end = self.pos + bits
        if end > self.limit:
            raise ValueError("truncated or corrupt stream")
        b0 = self.pos >> 3
        b1 = (end + 7) >> 3
        chunk = int.from_bytes(self.data[b0:b1], "big")
        self.pos = end
        return (chunk >> (b1 * 8 - end)) & ((1 << bits) - 1)


def bits_for(size):
    """Bits needed to index a window holding `size` possible values."""
    return (size - 1).bit_length() if size > 1 else 0


# --------------------------------------------------------------------------
# Sorted values -> pre-order BST with shrinking windows
# --------------------------------------------------------------------------
def bst_encode(w, t, l, r, low, high):
    """t is strictly increasing; t[l..r] must lie inside [low, high]."""
    if l > r:
        return
    mid = (l + r) >> 1
    lo = low + (mid - l)       # room for the mid-l smaller nodes
    hi = high - (r - mid)      # room for the r-mid larger nodes
    v = t[mid]
    w.write(v - lo, bits_for(hi - lo + 1))
    bst_encode(w, t, l, mid - 1, low, v - 1)
    bst_encode(w, t, mid + 1, r, v + 1, high)


def bst_decode(rd, t, l, r, low, high):
    if l > r:
        return
    mid = (l + r) >> 1
    lo = low + (mid - l)
    hi = high - (r - mid)
    v = lo + rd.read(bits_for(hi - lo + 1))
    t[mid] = v
    bst_decode(rd, t, l, mid - 1, low, v - 1)
    bst_decode(rd, t, mid + 1, r, v + 1, high)


# --------------------------------------------------------------------------
# Lehmer code, generalised to repeated values (multiset permutation rank)
# --------------------------------------------------------------------------
def _runs(sorted_vals):
    distinct, counts = [], []
    prev = None
    for v in sorted_vals:
        if v == prev:
            counts[-1] += 1
        else:
            distinct.append(v)
            counts.append(1)
            prev = v
    return distinct, counts


def _multinomial(n, counts):
    total = FACT[n]
    for c in counts:
        if c > 1:
            total //= FACT[c]
    return total


def _fenwick(counts):
    d = len(counts)
    tree = [0] * (d + 1)
    for i in range(1, d + 1):
        tree[i] += counts[i - 1]
        j = i + (i & -i)
        if j <= d:
            tree[j] += tree[i]
    return tree


def rank_encode(vals, distinct, counts):
    """Return (rank, bits).  rank is the Lehmer number of `vals` among all
    arrangements of its multiset; for distinct values it is the classic
    factorial-base Lehmer code."""
    n = len(vals)
    total = _multinomial(n, counts)
    bits = (total - 1).bit_length()
    if bits == 0:
        return 0, 0
    d = len(distinct)
    idx = {v: i for i, v in enumerate(distinct)}
    cnt = list(counts)
    tree = _fenwick(cnt)
    rank = 0
    rem = n
    for x in vals:
        i = idx[x]
        s, j = 0, i
        while j > 0:
            s += tree[j]
            j -= j & -j
        c = cnt[i]
        if s:
            rank += total * s // rem
        total = total * c // rem
        if total == 1:          # rest of the block is forced
            break
        cnt[i] = c - 1
        j = i + 1
        while j <= d:
            tree[j] -= 1
            j += j & -j
        rem -= 1
    return rank, bits


def rank_decode(rank, n, distinct, counts):
    d = len(distinct)
    cnt = list(counts)
    total = _multinomial(n, cnt)
    tree = _fenwick(cnt)
    top = 1 << (d.bit_length() - 1)
    out = []
    rem = n
    while rem:
        if total == 1:
            for i in range(d):
                if cnt[i]:
                    out.extend([distinct[i]] * cnt[i])
            break
        k = rank * rem // total + 1          # k-th smallest remaining value
        pos, step, kk = 0, top, k
        while step:
            nxt = pos + step
            if nxt <= d and tree[nxt] < kk:
                pos = nxt
                kk -= tree[nxt]
            step >>= 1
        i = pos
        s = k - kk                           # remaining items smaller than it
        c = cnt[i]
        rank -= total * s // rem
        total = total * c // rem
        out.append(distinct[i])
        cnt[i] = c - 1
        j = i + 1
        while j <= d:
            tree[j] -= 1
            j += j & -j
        rem -= 1
    return out


# --------------------------------------------------------------------------
# One block
# --------------------------------------------------------------------------
def encode_block(w, vals, lo, span):
    n = len(vals)
    sv = sorted(vals)
    distinct, counts = _runs(sv)
    t = [v - lo + k for k, v in enumerate(sv)]       # strictly increasing
    bst_encode(w, t, 0, n - 1, 0, span + n - 2)
    rank, bits = rank_encode(vals, distinct, counts)
    w.write(rank, bits)


def decode_block(rd, n, lo, span):
    t = [0] * n
    bst_decode(rd, t, 0, n - 1, 0, span + n - 2)
    sv = [t[k] - k + lo for k in range(n)]
    distinct, counts = _runs(sv)
    total = _multinomial(n, counts)
    rank = rd.read((total - 1).bit_length())
    return rank_decode(rank, n, distinct, counts)


# --------------------------------------------------------------------------
# File level
# --------------------------------------------------------------------------
def compress(data, block):
    if block not in BLOCK_CHOICES and not (1 <= block <= 255):
        raise ValueError("block must be between 1 and 255")
    n = len(data)
    lo, hi = (min(data), max(data)) if n else (0, 0)
    span = hi - lo + 1
    w = BitWriter()
    full, tail = divmod(n, block)
    for b in range(full):
        encode_block(w, list(data[b * block:(b + 1) * block]), lo, span)
    if tail:
        encode_block(w, list(data[full * block:]), lo, span)
    packed = HEADER.pack(MAGIC, block, lo, hi, n) + w.getvalue()
    if len(packed) >= HEADER.size + n:       # incompressible: store raw (block=0)
        return HEADER.pack(MAGIC, 0, 0, 0, n) + bytes(data)
    return packed


def decompress(blob):
    if len(blob) < HEADER.size:
        raise ValueError("not an MKB2 file")
    magic, block, lo, hi, n = HEADER.unpack_from(blob)
    if magic != MAGIC:
        raise ValueError("not an MKB2 file")
    if block == 0:                           # stored raw
        raw = blob[HEADER.size:HEADER.size + n]
        if len(raw) != n:
            raise ValueError("truncated stream")
        return bytes(raw)
    if hi < lo:
        raise ValueError("not an MKB2 file")
    span = hi - lo + 1
    rd = BitReader(blob, HEADER.size)
    out = bytearray()
    full, tail = divmod(n, block)
    for _ in range(full):
        out.extend(decode_block(rd, block, lo, span))
    if tail:
        out.extend(decode_block(rd, tail, lo, span))
    return bytes(out)


def benchmark(data, sample=65536):
    """Time each candidate block size on a sample. Returns list of dicts."""
    chunk = data[:sample]
    rows = []
    for blk in BLOCK_CHOICES:
        t0 = time.perf_counter()
        packed = compress(chunk, blk)
        dt = time.perf_counter() - t0
        rows.append({
            "block": blk,
            "size": len(packed),
            "ratio": len(packed) / max(1, len(chunk)),
            "seconds": dt,
            "kb_per_s": len(chunk) / 1024 / dt if dt else float("inf"),
        })
    return rows


def choose_block(data, tolerance=3.0, sample=65536):
    """Smallest output among candidates whose time is within `tolerance` x
    of the fastest candidate (tolerance=1.0 -> pure speed pick)."""
    rows = benchmark(data, sample)
    fastest = min(r["seconds"] for r in rows)
    ok = [r for r in rows if r["seconds"] <= fastest * tolerance]
    return min(ok, key=lambda r: (r["size"], r["seconds"]))["block"]


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def selftest():
    import random
    rnd = random.Random(1)
    # the example from the original script
    ex = bytes([231, 3, 45, 0, 23, 32, 78])
    assert decompress(compress(ex, 7)) == ex
    cases = {
        "empty": b"",
        "one": b"x",
        "const": b"a" * 1000,
        "text": (b"the quick brown fox jumps over the lazy dog. " * 40)[:1500],
        "random": bytes(rnd.randrange(256) for _ in range(2000)),
        "skewed": bytes(rnd.choice(b"aaaaaaabbbc\x00\xff") for _ in range(1999)),
        "ramp": bytes(range(256)) * 3,
    }
    for name, data in cases.items():
        for blk in BLOCK_CHOICES + (1, 2, 5, 200):
            assert decompress(compress(data, blk)) == data, (name, blk)
    print("selftest OK")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("c", help="compress")
    c.add_argument("src")
    c.add_argument("dst")
    c.add_argument("-b", "--block", default="auto")
    c.add_argument("--tolerance", type=float, default=3.0,
                   help="auto mode: allowed slowdown vs fastest block size")
    d = sub.add_parser("d", help="decompress")
    d.add_argument("src")
    d.add_argument("dst")
    b = sub.add_parser("bench", help="benchmark block sizes on a file")
    b.add_argument("src")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)

    if a.cmd == "selftest":
        selftest()
    elif a.cmd == "bench":
        data = open(a.src, "rb").read()
        print(f"{'block':>5} {'bytes':>9} {'ratio':>7} {'KB/s':>8}")
        for r in benchmark(data):
            print(f"{r['block']:>5} {r['size']:>9} {r['ratio']:>7.3f} {r['kb_per_s']:>8.1f}")
    elif a.cmd == "c":
        data = open(a.src, "rb").read()
        blk = choose_block(data, a.tolerance) if a.block == "auto" else int(a.block)
        t0 = time.perf_counter()
        blob = compress(data, blk)
        dt = time.perf_counter() - t0
        open(a.dst, "wb").write(blob)
        print(f"block={blk}  {len(data)} -> {len(blob)} bytes "
              f"({len(blob) / max(1, len(data)):.3f})  {dt:.2f}s")
    elif a.cmd == "d":
        blob = open(a.src, "rb").read()
        open(a.dst, "wb").write(decompress(blob))
        print("done")


if __name__ == "__main__":
    main()
