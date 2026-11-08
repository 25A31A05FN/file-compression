#include "FileHandler.h"

#include <fstream>
#include <iterator>
#include <stdexcept>

std::vector<std::uint8_t> FileHandler::readAll(const std::string& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        throw std::runtime_error("Could not open input file: " + path);
    }

    std::vector<std::uint8_t> data;
    char value;
    while (input.get(value)) {
        data.push_back(static_cast<std::uint8_t>(static_cast<unsigned char>(value)));
    }

    if (input.bad()) {
        throw std::runtime_error("An error occurred while reading: " + path);
    }
    return data;
}

void FileHandler::writeAll(const std::string& path, const std::vector<std::uint8_t>& data) {
    std::ofstream output(path, std::ios::binary);
    if (!output) {
        throw std::runtime_error("Could not create output file: " + path);
    }

    if (!data.empty()) {
        output.write(reinterpret_cast<const char*>(data.data()),
                     static_cast<std::streamsize>(data.size()));
    }

    if (!output) {
        throw std::runtime_error("An error occurred while writing: " + path);
    }
}

std::uint64_t FileHandler::fileSize(const std::string& path) {
    std::ifstream input(path, std::ios::binary | std::ios::ate);
    if (!input) {
        throw std::runtime_error("Could not open file to measure its size: " + path);
    }
    const auto position = input.tellg();
    if (position < 0) {
        throw std::runtime_error("Could not determine file size: " + path);
    }
    return static_cast<std::uint64_t>(position);
}
