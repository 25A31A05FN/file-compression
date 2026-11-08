#ifndef HUFFMAN_NODE_H
#define HUFFMAN_NODE_H

#include <cstdint>
#include <memory>

struct HuffmanNode {
    std::uint8_t byte;
    std::uint64_t frequency;
    int minByte;
    std::uint64_t order;
    std::shared_ptr<HuffmanNode> left;
    std::shared_ptr<HuffmanNode> right;

    HuffmanNode(std::uint8_t value, std::uint64_t count, std::uint64_t insertionOrder)
        : byte(value), frequency(count), minByte(value), order(insertionOrder),
          left(nullptr), right(nullptr) {}

    HuffmanNode(std::shared_ptr<HuffmanNode> leftChild,
                std::shared_ptr<HuffmanNode> rightChild,
                std::uint64_t insertionOrder)
        : byte(0),
          frequency(leftChild->frequency + rightChild->frequency),
          minByte(leftChild->minByte < rightChild->minByte ? leftChild->minByte : rightChild->minByte),
          order(insertionOrder),
          left(std::move(leftChild)),
          right(std::move(rightChild)) {}

    bool isLeaf() const {
        return !left && !right;
    }
};

#endif
