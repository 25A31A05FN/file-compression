#include "HuffmanTree.h"

#include <queue>
#include <tuple>
#include <vector>

namespace {
struct NodeCompare {
    bool operator()(const std::shared_ptr<HuffmanNode>& a,
                    const std::shared_ptr<HuffmanNode>& b) const {
        // Keep the node with the smallest frequency at the top.
        return std::tie(a->frequency, a->minByte, a->order) >
               std::tie(b->frequency, b->minByte, b->order);
    }
};
}

HuffmanTree::HuffmanTree(const FrequencyTable& frequencies) {
    std::priority_queue<
        std::shared_ptr<HuffmanNode>,
        std::vector<std::shared_ptr<HuffmanNode>>,
        NodeCompare
    > minHeap;

    std::uint64_t insertionOrder = 0;

    for (std::size_t value = 0; value < frequencies.size(); ++value) {
        if (frequencies[value] > 0) {
            minHeap.push(std::make_shared<HuffmanNode>(
                static_cast<std::uint8_t>(value),
                frequencies[value],
                insertionOrder++
            ));
        }
    }

    while (minHeap.size() > 1) {
        auto first = minHeap.top();
        minHeap.pop();

        auto second = minHeap.top();
        minHeap.pop();

        minHeap.push(std::make_shared<HuffmanNode>(
            first, second, insertionOrder++
        ));
    }

    if (!minHeap.empty()) {
        root_ = minHeap.top();
        buildCodes(root_, "");
    }
}

void HuffmanTree::buildCodes(const std::shared_ptr<HuffmanNode>& node,
                             const std::string& prefix) {
    if (!node) return;

    if (node->isLeaf()) {
        // A one-symbol file still needs one bit per symbol.
        codes_[node->byte] = prefix.empty() ? "0" : prefix;
        return;
    }

    buildCodes(node->left, prefix + "0");
    buildCodes(node->right, prefix + "1");
}

const std::shared_ptr<HuffmanNode>& HuffmanTree::root() const {
    return root_;
}

const std::array<std::string, 256>& HuffmanTree::codes() const {
    return codes_;
}
