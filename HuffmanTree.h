#ifndef HUFFMAN_TREE_H
#define HUFFMAN_TREE_H

#include "HuffmanNode.h"
#include <array>
#include <cstdint>
#include <memory>
#include <string>

class HuffmanTree {
public:
    using FrequencyTable = std::array<std::uint64_t, 256>;

    explicit HuffmanTree(const FrequencyTable& frequencies);

    const std::shared_ptr<HuffmanNode>& root() const;
    const std::array<std::string, 256>& codes() const;

private:
    std::shared_ptr<HuffmanNode> root_;
    std::array<std::string, 256> codes_{};

    void buildCodes(const std::shared_ptr<HuffmanNode>& node, const std::string& prefix);
};

#endif
