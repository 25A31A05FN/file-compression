#ifndef COMPRESSOR_H
#define COMPRESSOR_H

#include <string>

class Compressor {
public:
    static void compress(const std::string& inputPath, const std::string& outputPath);
};

#endif
