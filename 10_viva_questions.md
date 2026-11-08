# Viva Questions

**1. What is Huffman Coding?**

It is a method of compressing data by giving shorter codes to values that appear more often.

**2. Which method does Huffman Coding use?**

Greedy Method.

**3. Why is it called greedy?**

Because it selects the two smallest frequencies at every step.

**4. Which data structure is used in this project?**

A priority queue is used to get the smallest frequencies. A binary tree is used for the codes.

**5. What is a Huffman Tree?**

It is a binary tree used to make the codes.

**6. What does the left side mean?**

It means bit 0.

**7. What does the right side mean?**

It means bit 1.

**8. What is lossless compression?**

It means the original data can be recovered exactly.

**9. Why are frequencies stored in the compressed file?**

They are used to build the tree again during decompression.

**10. Does compression always reduce file size?**

No. The extra information stored in the compressed file can make a small file bigger.
