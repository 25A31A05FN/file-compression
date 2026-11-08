#ifndef DECOMPRESSOR_H
#define DECOMPRESSOR_H

#include <string>

class Decompressor {
public:
    static void decompress(const std::string& inputPath, const std::string& outputPath);
};

#endif
