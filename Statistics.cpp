#include "Statistics.h"

#include <iomanip>
#include <iostream>

void Statistics::printCompression(std::uint64_t originalBytes,
                                  std::uint64_t compressedBytes) {
    std::cout << "\n--- Compression results ---\n";
    std::cout << "Original size:   " << originalBytes << " bytes\n";
    std::cout << "Compressed size: " << compressedBytes << " bytes\n";

    if (originalBytes == 0) {
        std::cout << "Space saved:     Not applicable (empty file)\n";
        return;
    }

    const double saved =
        (1.0 - static_cast<double>(compressedBytes) /
                   static_cast<double>(originalBytes)) * 100.0;

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Space saved:     " << saved << "%\n";

    if (compressedBytes > originalBytes) {
        std::cout << "Note: The compressed file is larger. The header adds "
                     "overhead, especially for small files.\n";
    }
}
