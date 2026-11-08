# What is Huffman Coding?

Huffman Coding is a way to reduce the size of data.

It gives:
- Short codes to bytes that appear many times.
- Longer codes to bytes that appear fewer times.

For example, take this text:

```text
AAAAABBC
```

The frequency of each character is:

| Character | Frequency |
|---|---:|
| A | 5 |
| B | 2 |
| C | 1 |

The program uses these frequencies to build a Huffman Tree and create codes.

Huffman Coding is called lossless compression. This means we can get the original data back without changing it.
