cmake_minimum_required(VERSION 3.16)
project(HuffmanFileCompression VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(huffman
    src/main.cpp
    src/HuffmanTree.cpp
    src/Compressor.cpp
    src/Decompressor.cpp
    src/FileHandler.cpp
    src/Statistics.cpp
)

target_include_directories(huffman PRIVATE include)

if(MSVC)
    target_compile_options(huffman PRIVATE /W4)
else()
    target_compile_options(huffman PRIVATE -Wall -Wextra -Wpedantic)
endif()
