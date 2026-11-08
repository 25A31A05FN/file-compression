"""
Huffman Coding - File Compression (Advanced Data Structures mini project)

Data structures implemented from scratch (no heapq):
    1. MinHeap       - array-based binary heap
    2. PairingHeap   - pointer-based mergeable heap (amortized O(1) insert/meld)
    3. Node          - Huffman tree, also reused as a binary decode trie
    4. BitWriter     - bit-level output buffer
    5. dict          - frequency table and code table (hash maps)

Also uses canonical Huffman codes, so the header stores only code LENGTHS
(2 bytes per symbol) instead of full frequencies (5 bytes per symbol).

Usage:
    python huffman.py compress   input.txt  output.huf [--heap binary|pairing]
    python huffman.py decompress output.huf restored.txt
    python huffman.py codes      input.txt          # canonical code table + entropy
    python huffman.py bench                         # binary heap vs pairing heap
    python huffman.py test                          # round-trip self tests

File format (.huf):
    4 bytes   magic  b"HUF2"
    8 bytes   original size in bytes
    2 bytes   number of distinct symbols n
    n * 2     (symbol: 1 byte, code length: 1 byte)
    rest      canonical-Huffman bit stream, zero-padded to a whole byte
"""
import math
import os
import random
import struct
import sys
import time
from collections import Counter

MAGIC = b"HUF2"


# ======================================================================
# Data structure 1: binary min-heap (array-based)
# parent(i) = (i-1)//2, children = 2i+1, 2i+2
# push: O(log n)   pop: O(log n)
# ======================================================================
class MinHeap:
    def __init__(self):
        self.a = []

    def __len__(self):
        return len(self.a)

    def push(self, x):
        a = self.a
        a.append(x)
        i = len(a) - 1
        while i > 0:                       # sift up
            p = (i - 1) // 2
            if a[i] < a[p]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def pop(self):
        a = self.a
        top = a[0]
        last = a.pop()
        if a:
            a[0] = last
            i, n = 0, len(a)
            while True:                    # sift down
                l, r, m = 2 * i + 1, 2 * i + 2, i
                if l < n and a[l] < a[m]:
                    m = l
                if r < n and a[r] < a[m]:
                    m = r
                if m == i:
                    break
                a[i], a[m] = a[m], a[i]
                i = m
        return top


# ======================================================================
# Data structure 2: pairing heap (heap-ordered multiway tree)
# push / meld: O(1)   pop: O(log n) amortized (two-pass pairing)
# ======================================================================
class _PNode:
    __slots__ = ("item", "kids")

    def __init__(self, item):
        self.item = item
        self.kids = []


class PairingHeap:
    def __init__(self):
        self.root = None
        self.n = 0

    def __len__(self):
        return self.n

    @staticmethod
    def _meld(a, b):
        if a is None:
            return b
        if b is None:
            return a
        if b.item < a.item:
            a, b = b, a
        a.kids.append(b)                   # larger root becomes a child
        return a

    def push(self, x):
        self.root = self._meld(self.root, _PNode(x))
        self.n += 1

    def pop(self):
        if self.root is None:
            raise IndexError("pop from empty heap")
        r = self.root
        kids = r.kids
        # pass 1: meld children in pairs, left to right
        paired = [self._meld(kids[i], kids[i + 1]) if i + 1 < len(kids) else kids[i]
                  for i in range(0, len(kids), 2)]
        # pass 2: meld the results right to left
        new = None
        for t in reversed(paired):
            new = self._meld(new, t)
        self.root = new
        self.n -= 1
        return r.item


HEAPS = {"binary": MinHeap, "pairing": PairingHeap}


# ======================================================================
# Data structure 3: Huffman tree / binary decode trie
# ======================================================================
class Node:
    __slots__ = ("sym", "freq", "left", "right")

    def __init__(self, sym=None, freq=0, left=None, right=None):
        self.sym, self.freq, self.left, self.right = sym, freq, left, right


def build_tree(freq, heap_cls=MinHeap):
    """Greedy Huffman construction: repeatedly merge the two lightest trees."""
    heap = heap_cls()
    for order, (sym, f) in enumerate(sorted(freq.items())):
        heap.push((f, order, Node(sym, f)))     # 'order' breaks ties deterministically
    order = len(freq)
    while len(heap) > 1:
        f1, _, a = heap.pop()
        f2, _, b = heap.pop()
        heap.push((f1 + f2, order, Node(None, f1 + f2, a, b)))
        order += 1
    return heap.pop()[2]


def code_lengths(root):
    """Depth of every leaf = its code length."""
    if root.sym is not None:                    # only one distinct byte in the file
        return {root.sym: 1}
    lengths, stack = {}, [(root, 0)]
    while stack:
        node, d = stack.pop()
        if node.sym is not None:
            lengths[node.sym] = d
        else:
            stack.append((node.left, d + 1))
            stack.append((node.right, d + 1))
    return lengths


def canonical_codes(lengths):
    """Assign codes in (length, symbol) order: the decoder can rebuild them
    from lengths alone."""
    codes, code, prev = {}, 0, 0
    for sym, ln in sorted(lengths.items(), key=lambda kv: (kv[1], kv[0])):
        code <<= (ln - prev)
        codes[sym] = (code, ln)
        code += 1
        prev = ln
    return codes


def build_decode_trie(codes):
    """Insert every code into a binary trie; leaves hold the symbol."""
    root = Node()
    for sym, (code, ln) in codes.items():
        node = root
        for i in range(ln - 1, -1, -1):
            bit = (code >> i) & 1
            child = node.right if bit else node.left
            if child is None:
                child = Node()
                if bit:
                    node.right = child
                else:
                    node.left = child
            node = child
        node.sym = sym
    return root


# ======================================================================
# Data structure 4: bit-level writer
# ======================================================================
class BitWriter:
    def __init__(self):
        self.buf, self.acc, self.n = bytearray(), 0, 0

    def write(self, code, length):
        self.acc = (self.acc << length) | code
        self.n += length
        while self.n >= 8:
            self.n -= 8
            self.buf.append((self.acc >> self.n) & 0xFF)
        self.acc &= (1 << self.n) - 1

    def finish(self):
        if self.n:
            self.buf.append((self.acc << (8 - self.n)) & 0xFF)
            self.acc = self.n = 0
        return bytes(self.buf)


# ======================================================================
# Compress / decompress
# ======================================================================
def compress_bytes(data, heap_cls=MinHeap):
    if not data:
        return MAGIC + struct.pack(">QH", 0, 0)
    freq = Counter(data)
    lengths = code_lengths(build_tree(freq, heap_cls))
    codes = canonical_codes(lengths)
    w = BitWriter()
    for b in data:
        w.write(*codes[b])
    header = MAGIC + struct.pack(">QH", len(data), len(lengths))
    header += b"".join(bytes((s, l)) for s, l in sorted(lengths.items()))
    return header + w.finish()


def decompress_bytes(blob):
    if blob[:4] != MAGIC:
        raise ValueError("Not a HUF2 file")
    size, n = struct.unpack(">QH", blob[4:14])
    if size == 0:
        return b""
    pos = 14
    lengths = {blob[pos + 2 * i]: blob[pos + 2 * i + 1] for i in range(n)}
    pos += 2 * n
    root = build_decode_trie(canonical_codes(lengths))
    out, node = bytearray(), root
    for byte in blob[pos:]:
        for i in range(7, -1, -1):
            node = node.right if (byte >> i) & 1 else node.left
            if node is None:
                raise ValueError("Corrupt file")
            if node.sym is not None:
                out.append(node.sym)
                if len(out) == size:
                    return bytes(out)
                node = root
    raise ValueError("Unexpected end of data")


# ======================================================================
# File helpers, analysis and CLI
# ======================================================================
def compress_file(src, dst, heap_cls):
    data = open(src, "rb").read()
    blob = compress_bytes(data, heap_cls)
    open(dst, "wb").write(blob)
    o, c = len(data), len(blob)
    print(f"Original  : {o} bytes")
    print(f"Compressed: {c} bytes")
    if o:
        print(f"Ratio     : {c / o:.1%} of original ({1 - c / o:.1%} saved)")


def decompress_file(src, dst):
    open(dst, "wb").write(decompress_bytes(open(src, "rb").read()))
    print(f"Restored {dst}")


def show_codes(src):
    data = open(src, "rb").read()
    freq = Counter(data)
    codes = canonical_codes(code_lengths(build_tree(freq)))
    print(f"{'char':>6} {'freq':>7}  canonical code")
    for sym, (code, ln) in sorted(codes.items(), key=lambda kv: (kv[1][1], kv[0])):
        ch = repr(chr(sym)) if 32 <= sym < 127 else f"0x{sym:02x}"
        print(f"{ch:>6} {freq[sym]:>7}  {format(code, f'0{ln}b')}")
    n = len(data)
    avg = sum(freq[s] * codes[s][1] for s in codes) / n
    entropy = -sum(f / n * math.log2(f / n) for f in freq.values())
    print(f"\nEntropy H            : {entropy:.3f} bits/symbol")
    print(f"Huffman average length: {avg:.3f} bits/symbol  (H <= avg < H + 1)")
    print(f"Fixed-length encoding : 8.000 bits/symbol")


def bench(n=100000):
    data = [random.random() for _ in range(n)]
    expected = sorted(data)
    print(f"{n} pushes + {n} pops (heap sort):")
    for name, cls in HEAPS.items():
        h, t = cls(), time.perf_counter()
        for x in data:
            h.push(x)
        out = [h.pop() for _ in range(n)]
        dt = time.perf_counter() - t
        assert out == expected, f"{name} heap returned wrong order"
        print(f"  {name:8} {dt:.3f}s  (sorted correctly)")


def self_test():
    cases = [
        b"",
        b"a",
        b"aaaaaaaa",
        b"abracadabra",
        b"the quick brown fox jumps over the lazy dog " * 50,
        bytes(range(256)) * 4,
        os.urandom(5000),
    ]
    for i, data in enumerate(cases, 1):
        outs = []
        for name, cls in HEAPS.items():
            blob = compress_bytes(data, cls)
            assert decompress_bytes(blob) == data, f"case {i} failed with {name} heap"
            outs.append(blob)
        assert outs[0] == outs[1], "heaps produced different output"
        print(f"case {i}: PASS  ({len(data)} -> {len(outs[0])} bytes, both heaps identical)")
    for cls in HEAPS.values():
        h, xs = cls(), [random.randint(0, 50) for _ in range(500)]
        for x in xs:
            h.push(x)
        assert [h.pop() for _ in xs] == sorted(xs)
    print("heap tests: PASS")
    print("All tests passed.")


if __name__ == "__main__":
    args = sys.argv[1:]
    heap_name = "binary"
    if "--heap" in args:
        i = args.index("--heap")
        heap_name = args[i + 1] if i + 1 < len(args) else ""
        del args[i:i + 2]
    if heap_name not in HEAPS:
        sys.exit("--heap must be 'binary' or 'pairing'")
    if len(args) == 3 and args[0] == "compress":
        compress_file(args[1], args[2], HEAPS[heap_name])
    elif len(args) == 3 and args[0] == "decompress":
        decompress_file(args[1], args[2])
    elif len(args) == 2 and args[0] == "codes":
        show_codes(args[1])
    elif args == ["bench"]:
        bench()
    elif args == ["test"]:
        self_test()
    else:
        print(__doc__)
