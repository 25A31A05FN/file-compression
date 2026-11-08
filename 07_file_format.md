# 7. How the .huff File Is Stored

A compressed file needs enough information for the decoder to rebuild the same tree.

This project stores:

| Part | Size | Meaning |
|---|---:|---|
| Signature | 4 bytes | The letters `HUF1` identify this format |
| Original size | 8 bytes | Number of bytes before compression |
| Frequency table | 2,048 bytes | 256 counters, each 8 bytes |
| Encoded data | Changes | The compressed bit stream |

The fixed header is 2,060 bytes.

## Why store the frequencies?

The decoder uses the frequencies to build the same Huffman Tree. It does not need a separate tree file.

## Why pack bits?

A text character `'0'` takes a whole byte if stored as text. This project stores eight encoded bits inside one byte instead.

## Padding

The last group may have fewer than eight useful bits. The compressor fills the unused positions with zeroes. The original size tells the decoder when to stop.
