#ifndef FILE_HANDLER_H
#define FILE_HANDLER_H

#include <cstdint>
#include <string>
#include <vector>

class FileHandler {
public:
    static std::vector<std::uint8_t> readAll(const std::string& path);
    static void writeAll(const std::string& path, const std::vector<std::uint8_t>& data);
    static std::uint64_t fileSize(const std::string& path);
};

#endif
