#include "Compressor.h"

#include "FileHandler.h"
#include "HuffmanTree.h"
#include "Statistics.h"

#include <array>
#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <vector>

namespace {
void writeU64(std::ostream& output, std::uint64_t value) {
    for (int i = 0; i < 8; ++i) {
        output.put(static_cast<char>((value >> (i * 8)) & 0xFF));
    }
    if (!output) throw std::runtime_error("Could not write compressed file header.");
}

}

void Compressor::compress(const std::string& inputPath,
                          const std::string& outputPath) {
    if (inputPath == outputPath) {
        throw std::runtime_error("Input and output paths must be different.");
    }

    const auto data = FileHandler::readAll(inputPath);

    HuffmanTree::FrequencyTable frequencies{};
    for (std::uint8_t byte : data) {
        ++frequencies[byte];
    }

    HuffmanTree tree(frequencies);

    std::ofstream output(outputPath, std::ios::binary);
    if (!output) {
        throw std::runtime_error("Could not create compressed file: " + outputPath);
    }

    // Write a small header so the decoder can rebuild the tree.
    output.write("HUF1", 4);
    writeU64(output, static_cast<std::uint64_t>(data.size()));

    for (std::uint64_t frequency : frequencies) {
        writeU64(output, frequency);
    }

    unsigned char buffer = 0;
    int bitsInBuffer = 0;

    for (std::uint8_t byte : data) {
        const std::string& code = tree.codes()[byte];
        for (char bit : code) {
            buffer = static_cast<unsigned char>((buffer << 1) | (bit == '1' ? 1 : 0));
            ++bitsInBuffer;

            if (bitsInBuffer == 8) {
                output.put(static_cast<char>(buffer));
                buffer = 0;
                bitsInBuffer = 0;
            }
        }
    }

    // Fill the unused bits in the last byte with zeroes.
    if (bitsInBuffer > 0) {
        buffer = static_cast<unsigned char>(buffer << (8 - bitsInBuffer));
        output.put(static_cast<char>(buffer));
    }

    if (!output) {
        throw std::runtime_error("An error occurred while writing compressed data.");
    }
    output.close();

    Statistics::printCompression(
        static_cast<std::uint64_t>(data.size()),
        FileHandler::fileSize(outputPath)
    );
}
