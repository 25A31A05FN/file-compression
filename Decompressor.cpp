#include "Decompressor.h"

#include "FileHandler.h"
#include "HuffmanTree.h"

#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <vector>

namespace {
std::uint64_t readU64(std::istream& input) {
    std::uint64_t value = 0;
    for (int i = 0; i < 8; ++i) {
        const int byte = input.get();
        if (byte == EOF) throw std::runtime_error("Compressed file header is incomplete.");
        value |= static_cast<std::uint64_t>(static_cast<unsigned char>(byte)) << (i * 8);
    }
    return value;
}
}

void Decompressor::decompress(const std::string& inputPath,
                              const std::string& outputPath) {
    if (inputPath == outputPath) {
        throw std::runtime_error("Input and output paths must be different.");
    }

    std::ifstream input(inputPath, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Could not open compressed file: " + inputPath);
    }

    char magic[4];
    input.read(magic, 4);
    if (!input || magic[0] != 'H' || magic[1] != 'U' ||
        magic[2] != 'F' || magic[3] != '1') {
        throw std::runtime_error("This is not a supported HUF1 compressed file.");
    }

    const std::uint64_t originalSize = readU64(input);

    HuffmanTree::FrequencyTable frequencies{};
    std::uint64_t frequencyTotal = 0;

    for (std::size_t i = 0; i < frequencies.size(); ++i) {
        frequencies[i] = readU64(input);
        if (frequencies[i] > std::numeric_limits<std::uint64_t>::max() - frequencyTotal) {
            throw std::runtime_error("Invalid frequency table.");
        }
        frequencyTotal += frequencies[i];
    }

    if (frequencyTotal != originalSize) {
        throw std::runtime_error("Compressed file has an invalid frequency table.");
    }

    HuffmanTree tree(frequencies);
    std::vector<std::uint8_t> restored;
    if (originalSize > static_cast<std::uint64_t>(restored.max_size())) {
        throw std::runtime_error("The original file is too large for this system.");
    }
    restored.reserve(static_cast<std::size_t>(originalSize));

    if (originalSize > 0) {
        auto current = tree.root();
        if (!current) throw std::runtime_error("Compressed file does not contain a valid tree.");

        if (current->isLeaf()) {
            restored.assign(static_cast<std::size_t>(originalSize), current->byte);
        } else {
            while (restored.size() < originalSize) {
                const int packed = input.get();
                if (packed == EOF) {
                    throw std::runtime_error("Compressed data ended before decoding was complete.");
                }

                const unsigned char byte = static_cast<unsigned char>(packed);
                for (int bitIndex = 7; bitIndex >= 0 && restored.size() < originalSize; --bitIndex) {
                    const bool bit = ((byte >> bitIndex) & 1U) != 0;
                    current = bit ? current->right : current->left;

                    if (!current) {
                        throw std::runtime_error("Compressed data contains an invalid bit sequence.");
                    }

                    if (current->isLeaf()) {
                        restored.push_back(current->byte);
                        current = tree.root();
                    }
                }
            }
        }
    }

    FileHandler::writeAll(outputPath, restored);
    std::cout << "Decompression completed.\n";
    std::cout << "Restored size: " << restored.size() << " bytes\n";
}
