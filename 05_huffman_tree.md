# Building the Huffman Tree

The program uses a priority queue to get the two smallest frequencies.

Steps:

1. Make a node for each byte that appears in the file.
2. Add the nodes to the priority queue.
3. Remove the two nodes with the smallest frequencies.
4. Make a new parent node with their added frequency.
5. Add the parent node back to the queue.
6. Continue until one node is left.

The last node is the root of the Huffman Tree.

The code for this part is in `HuffmanTree.cpp`. The node details are in `HuffmanNode.h`.
