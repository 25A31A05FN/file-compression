# Greedy Method

A greedy method makes a choice at each step and continues with that choice.

In Huffman Coding, we always take the two nodes with the smallest frequencies and join them.

Example:

| Character | Frequency |
|---|---:|
| A | 5 |
| B | 9 |
| C | 12 |
| D | 13 |

First, A and B are selected because 5 and 9 are the smallest values.

Their new frequency is:

```text
5 + 9 = 14
```

The new node is put back with the other nodes. The same process continues until only one node is left.

This is the greedy part of Huffman Coding.
