"""
Streamlit front end for the Huffman compressor.
Run:  streamlit run app.py      (keep it in the same folder as huffman.py)
"""
import math
import time
from collections import Counter

import streamlit as st

from huffman import (HEAPS, build_tree, canonical_codes, code_lengths,
                     compress_bytes, decompress_bytes)

st.set_page_config(page_title="Huffman Compressor", page_icon="🗜️", layout="wide")


def sym_label(sym):
    return repr(chr(sym)) if 32 <= sym < 127 else f"0x{sym:02x}"


def to_dot(root):
    """Graphviz DOT source for the Huffman tree (left edge = 0, right edge = 1)."""
    lines = ["digraph G {", "node [fontsize=10];"]
    stack, nxt = [(root, 0)], 1
    while stack:
        node, i = stack.pop()
        if node.sym is not None:
            ch = sym_label(node.sym).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'n{i} [label="{ch}\\n{node.freq}", shape=box];')
        else:
            lines.append(f'n{i} [label="{node.freq}", shape=circle];')
            for bit, child in (("0", node.left), ("1", node.right)):
                j = nxt
                nxt += 1
                lines.append(f'n{i} -> n{j} [label="{bit}"];')
                stack.append((child, j))
    lines.append("}")
    return "\n".join(lines)


st.title("🗜️ Huffman Coding File Compressor")
st.caption("Advanced Data Structures mini project: custom heaps, Huffman tree, "
           "decode trie and canonical codes")

with st.sidebar:
    st.header("Settings")
    heap_name = st.radio(
        "Priority queue",
        list(HEAPS),
        format_func=lambda k: {"binary": "Binary min-heap", "pairing": "Pairing heap"}[k],
        help="Both heaps give identical output; they differ in how they get there.",
    )
    st.markdown("**Binary heap**: array, push/pop O(log n)\n\n"
                "**Pairing heap**: tree, push O(1), pop O(log n) amortized")

tab_c, tab_d = st.tabs(["Compress", "Decompress"])

# ---------------------------------------------------------------- Compress
with tab_c:
    source = st.radio("Input", ["Upload a file", "Type text"], horizontal=True)
    data, name = b"", "text"
    if source == "Upload a file":
        up = st.file_uploader("Choose any file", key="comp_up")
        if up is not None:
            data, name = up.getvalue(), up.name
    else:
        text = st.text_area("Text to compress", "abracadabra", height=120)
        data = text.encode("utf-8")

    if len(data) > 5_000_000:
        st.warning("Large file: this is pure Python, so it may take a while.")

    if data:
        freq = Counter(data)
        t0 = time.perf_counter()
        blob = compress_bytes(data, HEAPS[heap_name])
        dt = time.perf_counter() - t0
        root = build_tree(freq, HEAPS[heap_name])
        lengths = code_lengths(root)
        codes = canonical_codes(lengths)
        n = len(data)
        avg = sum(freq[s] * lengths[s] for s in freq) / n
        entropy = -sum(f / n * math.log2(f / n) for f in freq.values())

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Original", f"{n:,} B")
        c2.metric("Compressed", f"{len(blob):,} B")
        c3.metric("Saved", f"{(1 - len(blob) / n):.1%}")
        c4.metric("Time", f"{dt * 1000:.1f} ms")
        if len(blob) >= n:
            st.info("The output is not smaller: the header costs more than the "
                    "compression saves. This happens with tiny or random files.")

        ok = decompress_bytes(blob) == data
        (st.success if ok else st.error)(
            "Round-trip check passed: decompressed data matches the original."
            if ok else "Round-trip check FAILED.")

        st.download_button("⬇️ Download .huf file", blob,
                           file_name=name + ".huf", mime="application/octet-stream")

        st.subheader("Code table")
        st.caption(f"Entropy H = {entropy:.3f} bits/symbol, Huffman average = "
                   f"{avg:.3f} (theory: H <= avg < H + 1), fixed-length = 8.000")
        rows = [{"symbol": sym_label(s), "frequency": freq[s],
                 "code length": ln, "canonical code": format(c, f"0{ln}b")}
                for s, (c, ln) in sorted(codes.items(), key=lambda kv: (kv[1][1], kv[0]))]
        st.dataframe(rows, use_container_width=True, hide_index=True)

        st.subheader("Huffman tree")
        if len(freq) <= 40:
            st.graphviz_chart(to_dot(root))
            st.caption("Leaf depth gives each code length. The stored codes are the "
                       "canonical re-assignment of those lengths, so the bit patterns "
                       "can differ from the paths drawn here.")
        else:
            st.info(f"{len(freq)} distinct symbols: too many to draw clearly "
                    "(limit 40). Try a text file.")
    else:
        st.info("Upload a file or type some text to begin.")

# -------------------------------------------------------------- Decompress
with tab_d:
    up = st.file_uploader("Choose a .huf file", type=["huf"], key="dec_up")
    if up is not None:
        try:
            restored = decompress_bytes(up.getvalue())
        except (ValueError, IndexError) as e:
            st.error(f"Could not decompress: {e}")
        else:
            out_name = up.name[:-4] if up.name.endswith(".huf") else up.name + ".out"
            st.success(f"Restored {len(restored):,} bytes from {len(up.getvalue()):,} bytes.")
            st.download_button("⬇️ Download restored file", restored, file_name=out_name)
            try:
                st.text_area("Preview", restored[:2000].decode("utf-8"), height=150)
            except UnicodeDecodeError:
                st.caption("Binary content: no text preview.")
