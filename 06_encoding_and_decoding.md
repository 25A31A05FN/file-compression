# Encoding and Decoding

## Encoding

Encoding changes each byte into its Huffman code.

To get a code, start at the root:
- Write `0` when moving left.
- Write `1` when moving right.
- Stop when the leaf is reached.

The bits are saved in the compressed file.

## Decoding

Decoding changes the bits back into the original bytes.

1. Start at the root.
2. Read one bit.
3. Move left for `0` or right for `1`.
4. When a leaf is reached, write that byte.
5. Go back to the root and continue.

The original file size is stored in the compressed file. The program uses it to know when decoding is finished.

If the file has only one type of byte, the program uses code `0` for it.
