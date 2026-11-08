# Huffman File Compression

A file compression and decompression application developed using **C++17** and the **Huffman Coding Algorithm**. This project demonstrates how greedy algorithms and binary trees can be used to reduce file size while preserving the original data.

## 📌 Project Overview

Huffman Coding is a lossless data compression technique that assigns variable-length binary codes to characters based on their frequency of occurrence.

Characters that appear more frequently receive shorter codes, while less frequent characters receive longer codes.

This project reads an input file, calculates byte frequencies, constructs a Huffman tree, generates binary codes, and compresses the file. It can also decompress the compressed file to restore the original content.

## 🎯 Objectives

- Implement the Huffman Coding algorithm using C++.
- Understand the Greedy Algorithm approach.
- Implement a Binary Tree for encoding and decoding.
- Use a Priority Queue to construct the Huffman Tree efficiently.
- Perform lossless file compression and decompression.
- Analyze compression statistics and file size reduction.

## 🛠️ Technologies Used

- **Programming Language:** C++17
- **Data Structures:** Binary Tree, Priority Queue
- **Algorithm:** Huffman Coding (Greedy Algorithm)
- **Build System:** CMake
- **Testing:** Python

## 📂 Project Structure

```text
HuffmanFileCompression/
│
├── include/
│   ├── Compressor.h
│   ├── Decompressor.h
│   ├── FileHandler.h
│   ├── HuffmanNode.h
│   ├── HuffmanTree.h
│   └── Statistics.h
│
├── src/
│   ├── main.cpp
│   ├── Compressor.cpp
│   ├── Decompressor.cpp
│   ├── FileHandler.cpp
│   ├── HuffmanTree.cpp
│   └── Statistics.cpp
│
├── tests/
│   └── test_roundtrip.py
│
├── examples/
│
├── CMakeLists.txt
├── README.md
├── LICENSE
└── .gitignore
```

*Note: Keep only the folders and files that actually exist in your GitHub repository. Add `Statistics.h` if it is not already present.*

## ⚙️ How It Works

### 1. Frequency Calculation
The program reads the input file and calculates the frequency of each byte.

### 2. Huffman Tree Construction
A minimum priority queue is used to construct the Huffman Tree by repeatedly combining the two nodes with the lowest frequencies.

### 3. Code Generation
The tree is traversed recursively to generate binary codes for each byte.

### 4. File Compression
The generated codes are used to encode the original data into a compressed binary file.

### 5. File Decompression
The compressed file header and encoded data are read to reconstruct the Huffman Tree and restore the original file.

## 🚀 Getting Started

### Prerequisites

- C++ compiler supporting C++17
- CMake 3.16 or later
- Python 3 (for running tests)

### Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd HuffmanFileCompression
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### Build the Project

```bash
cmake -S . -B build
cmake --build build
```

## ▶️ Usage

### Compress a File

```bash
./build/huffman compress input.txt output.huff
```

### Decompress a File

```bash
./build/huffman decompress output.huff restored.txt
```

The executable name or path may differ depending on your CMake configuration and operating system.

## 🧪 Testing

The project includes a Python round-trip testing script.

Run:

```bash
python test_roundtrip.py
```

The tests cover:

- Empty files
- Single-byte files
- Simple text files
- Files containing all 256 possible byte values
- Binary files

The round-trip process checks whether the decompressed file matches the original file.

## 📊 Key Features

- Lossless file compression.
- Huffman Tree construction.
- Priority Queue-based node selection.
- Binary file handling.
- Compression and decompression support.
- Compression statistics.
- Round-trip testing for data integrity.

## 📚 Concepts Demonstrated

| Concept | Application |
|---|---|
| Greedy Algorithm | Selecting minimum-frequency nodes |
| Binary Tree | Constructing the Huffman Tree |
| Priority Queue | Efficient node selection |
| Recursion | Generating Huffman codes |
| File Handling | Reading and writing binary files |
| Compression | Reducing file storage requirements |

## 🔮 Future Enhancements

- Improve memory efficiency for large files.
- Add a graphical user interface.
- Support batch file compression.
- Add compression performance comparisons.
- Extend support to directory compression.

## 👨‍💻 Academic Project

**Project Title:** Huffman File Compression  
**Domain:** Advanced Data Structures and Algorithms (ADSAA)  
**Language:** C++17  
**Algorithm:** Huffman Coding  

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
