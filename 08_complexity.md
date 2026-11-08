# Time and Space Complexity

Let:
- `N` be the number of bytes in the input file.
- `K` be the number of different byte values.

There are only 256 possible byte values, so K cannot be more than 256.

## Time complexity

| Operation | Complexity |
|---|---|
| Count frequencies | O(N) |
| Build the Huffman Tree | O(K log K) |
| Generate codes | O(K) |
| Encode data | O(N + encoded bits) |
| Decode data | O(encoded bits) |

Counting frequencies takes O(N) because the program checks every byte in the file.

The tree takes O(K log K) because the priority queue is used to remove and add nodes.

## Space complexity

The tree can have at most `2K - 1` nodes.

The program also keeps the file data in memory while compressing or decompressing. So the file data needs O(N) memory.
