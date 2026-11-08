#ifndef STATISTICS_H
#define STATISTICS_H

#include <cstdint>
#include <string>

class Statistics {
public:
    static void printCompression(std::uint64_t originalBytes,
                                 std::uint64_t compressedBytes);
};

#endif
