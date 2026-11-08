#include "Compressor.h"
#include "Decompressor.h"

#include <exception>
#include <iostream>
#include <string>

void printUsage(const char* program) {
    std::cout << "Huffman File Compression (C++17)\n\n"
              << "Usage:\n"
              << "  " << program << " compress <input-file> <output.huff>\n"
              << "  " << program << " decompress <input.huff> <output-file>\n\n"
              << "Examples:\n"
              << "  " << program << " compress examples/input.txt output.huff\n"
              << "  " << program << " decompress output.huff restored.txt\n";
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        printUsage(argv[0]);
        return 1;
    }

    const std::string command = argv[1];

    try {
        if (command == "compress") {
            Compressor::compress(argv[2], argv[3]);
        } else if (command == "decompress") {
            Decompressor::decompress(argv[2], argv[3]);
        } else {
            printUsage(argv[0]);
            return 1;
        }
    } catch (const std::exception& error) {
        std::cerr << "Error: " << error.what() << '\n';
        return 1;
    }

    return 0;
}
