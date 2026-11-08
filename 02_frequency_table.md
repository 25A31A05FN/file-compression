# Frequency Table

A frequency table shows how many times each byte is present in a file.

Example:

```text
BANANA
```

| Character | Frequency |
|---|---:|
| B | 1 |
| A | 3 |
| N | 2 |

The total frequency is 6 because the word has six characters.

We need this table because Huffman Coding uses the frequencies to decide which bytes get shorter codes.

In this project, an array with 256 positions is used. Each position stores the count for one byte value.
