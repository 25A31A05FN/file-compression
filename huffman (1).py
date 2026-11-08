// huffman.h - Huffman coding with canonical codes (header-only)
//
// File format "HUF2" (identical to the Python version, files are interchangeable):
//   4 bytes  magic "HUF2"
//   8 bytes  original size, big-endian
//   2 bytes  number of distinct symbols n, big-endian
//   n * 2    (symbol, code length)
//   rest     canonical-Huffman bit stream, zero-padded to a whole byte
#pragma once
#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <deque>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "heaps.h"

namespace huff {

enum class HeapKind { Binary, Pairing };

// Codes longer than this are rejected. Reaching a depth of 56 would need an
// input of hundreds of gigabytes with Fibonacci-like frequencies.
constexpr int kMaxCodeLen = 56;
inline constexpr char kMagic[4] = {'H', 'U', 'F', '2'};

// ---------------------------------------------------------------------
// Huffman tree node (also reused as a binary trie node by the decoder)
// ---------------------------------------------------------------------
struct Node {
    int sym = -1;  // byte value for a leaf, -1 for an internal node
    std::uint64_t freq = 0;
    Node* left = nullptr;
    Node* right = nullptr;
};

// Owns every Node. A deque never moves existing elements, so pointers stay valid.
class NodePool {
    std::deque<Node> store_;

public:
    Node* make() {
        store_.emplace_back();
        return &store_.back();
    }
    Node* make(int sym, std::uint64_t freq, Node* l = nullptr, Node* r = nullptr) {
        Node* n = make();
        n->sym = sym;
        n->freq = freq;
        n->left = l;
        n->right = r;
        return n;
    }
};

using FreqTable = std::array<std::uint64_t, 256>;
using LengthTable = std::array<std::uint8_t, 256>;
struct Code {
    std::uint64_t bits = 0;
    int len = 0;
};
using CodeTable = std::array<Code, 256>;

// ---------------------------------------------------------------------
// Tree construction (greedy: merge the two lightest trees)
// ---------------------------------------------------------------------
struct Item {  // what goes into the heap
    std::uint64_t freq;
    std::uint32_t order;  // tie-breaker: makes the order total and deterministic
    Node* node;
    bool operator<(const Item& o) const {
        return freq != o.freq ? freq < o.freq : order < o.order;
    }
};

inline FreqTable count_freq(const std::vector<std::uint8_t>& data) {
    FreqTable f{};
    for (std::uint8_t b : data) ++f[b];
    return f;
}

template <typename Heap>
Node* build_tree_with(const FreqTable& freq, NodePool& pool) {
    Heap heap;
    std::uint32_t order = 0;
    for (int s = 0; s < 256; ++s)
        if (freq[s]) heap.push(Item{freq[s], order++, pool.make(s, freq[s])});
    if (heap.empty()) return nullptr;
    while (heap.size() > 1) {
        Item a = heap.pop();
        Item b = heap.pop();
        std::uint64_t f = a.freq + b.freq;
        heap.push(Item{f, order++, pool.make(-1, f, a.node, b.node)});
    }
    return heap.pop().node;
}

inline Node* build_tree(const FreqTable& freq, NodePool& pool, HeapKind kind) {
    return kind == HeapKind::Binary ? build_tree_with<MinHeap<Item>>(freq, pool)
                                    : build_tree_with<PairingHeap<Item>>(freq, pool);
}

// Depth of each leaf = its code length (0 means the symbol does not occur).
inline LengthTable code_lengths(const Node* root) {
    LengthTable len{};
    if (!root) return len;
    if (root->sym >= 0) {  // only one distinct byte in the file
        len[root->sym] = 1;
        return len;
    }
    std::vector<std::pair<const Node*, int>> stack{{root, 0}};
    while (!stack.empty()) {
        auto [node, d] = stack.back();
        stack.pop_back();
        if (node->sym >= 0) {
            if (d > kMaxCodeLen) throw std::runtime_error("code length exceeds supported maximum");
            len[node->sym] = static_cast<std::uint8_t>(d);
        } else {
            stack.push_back({node->left, d + 1});
            stack.push_back({node->right, d + 1});
        }
    }
    return len;
}

// Canonical codes: sort by (length, symbol), count upward. The decoder can
// rebuild exactly the same codes from the lengths alone.
inline CodeTable canonical_codes(const LengthTable& len) {
    std::vector<int> syms;
    for (int s = 0; s < 256; ++s)
        if (len[s]) syms.push_back(s);
    std::sort(syms.begin(), syms.end(), [&](int a, int b) {
        return len[a] != len[b] ? len[a] < len[b] : a < b;
    });
    CodeTable codes{};
    std::uint64_t code = 0;
    int prev = 0;
    for (int s : syms) {
        code <<= (len[s] - prev);
        codes[s] = Code{code, len[s]};
        ++code;
        prev = len[s];
    }
    return codes;
}

// Insert every code into a binary trie; leaves hold the symbol.
inline Node* build_decode_trie(const CodeTable& codes, NodePool& pool) {
    Node* root = pool.make();
    for (int s = 0; s < 256; ++s) {
        if (!codes[s].len) continue;
        Node* node = root;
        for (int i = codes[s].len - 1; i >= 0; --i) {
            Node*& slot = ((codes[s].bits >> i) & 1) ? node->right : node->left;
            if (!slot) slot = pool.make();
            node = slot;
        }
        node->sym = s;
    }
    return root;
}

// ---------------------------------------------------------------------
// Bit-level writer
// ---------------------------------------------------------------------
class BitWriter {
    std::vector<std::uint8_t> buf_;
    std::uint64_t acc_ = 0;
    int n_ = 0;  // number of pending bits in acc_ (always < 8 between calls)

public:
    void write(std::uint64_t code, int len) {
        acc_ = (acc_ << len) | code;
        n_ += len;
        while (n_ >= 8) {
            n_ -= 8;
            buf_.push_back(static_cast<std::uint8_t>((acc_ >> n_) & 0xFF));
        }
        acc_ &= (1ULL << n_) - 1;
    }
    std::vector<std::uint8_t> finish() {
        if (n_) {
            buf_.push_back(static_cast<std::uint8_t>((acc_ << (8 - n_)) & 0xFF));
            acc_ = 0;
            n_ = 0;
        }
        return std::move(buf_);
    }
};

// ---------------------------------------------------------------------
// Compress / decompress
// ---------------------------------------------------------------------
inline std::vector<std::uint8_t> compress(const std::vector<std::uint8_t>& data,
                                          HeapKind kind = HeapKind::Binary) {
    std::vector<std::uint8_t> out(kMagic, kMagic + 4);
    auto put_be = [&](std::uint64_t v, int bytes) {
        for (int i = bytes - 1; i >= 0; --i) out.push_back(static_cast<std::uint8_t>((v >> (8 * i)) & 0xFF));
    };
    if (data.empty()) {
        put_be(0, 8);
        put_be(0, 2);
        return out;
    }
    FreqTable freq = count_freq(data);
    NodePool pool;
    LengthTable len = code_lengths(build_tree(freq, pool, kind));
    CodeTable codes = canonical_codes(len);

    int n = 0;
    for (int s = 0; s < 256; ++s)
        if (len[s]) ++n;
    put_be(data.size(), 8);
    put_be(static_cast<std::uint64_t>(n), 2);
    for (int s = 0; s < 256; ++s)
        if (len[s]) {
            out.push_back(static_cast<std::uint8_t>(s));
            out.push_back(len[s]);
        }

    BitWriter w;
    for (std::uint8_t b : data) w.write(codes[b].bits, codes[b].len);
    std::vector<std::uint8_t> payload = w.finish();
    out.insert(out.end(), payload.begin(), payload.end());
    return out;
}

inline std::vector<std::uint8_t> decompress(const std::vector<std::uint8_t>& blob) {
    if (blob.size() < 14 || std::memcmp(blob.data(), kMagic, 4) != 0)
        throw std::runtime_error("Not a HUF2 file");
    auto get_be = [&](std::size_t off, int bytes) {
        std::uint64_t v = 0;
        for (int i = 0; i < bytes; ++i) v = (v << 8) | blob[off + i];
        return v;
    };
    std::uint64_t size = get_be(4, 8);
    std::size_t n = static_cast<std::size_t>(get_be(12, 2));
    if (size == 0) return {};

    std::size_t pos = 14;
    if (n == 0 || n > 256 || blob.size() < pos + 2 * n) throw std::runtime_error("Corrupt header");
    LengthTable len{};
    for (std::size_t i = 0; i < n; ++i) {
        int l = blob[pos + 2 * i + 1];
        if (l < 1 || l > kMaxCodeLen) throw std::runtime_error("Corrupt header");
        len[blob[pos + 2 * i]] = static_cast<std::uint8_t>(l);
    }
    pos += 2 * n;
    if (size > 8ULL * (blob.size() - pos)) throw std::runtime_error("Corrupt file");

    NodePool pool;
    const Node* root = build_decode_trie(canonical_codes(len), pool);
    std::vector<std::uint8_t> out;
    out.reserve(static_cast<std::size_t>(size));
    const Node* node = root;
    for (std::size_t p = pos; p < blob.size(); ++p) {
        for (int i = 7; i >= 0; --i) {
            node = ((blob[p] >> i) & 1) ? node->right : node->left;
            if (!node) throw std::runtime_error("Corrupt file");
            if (node->sym >= 0) {
                out.push_back(static_cast<std::uint8_t>(node->sym));
                if (out.size() == size) return out;
                node = root;
            }
        }
    }
    throw std::runtime_error("Unexpected end of data");
}

}  // namespace huff
