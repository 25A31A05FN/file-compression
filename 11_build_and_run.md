# 11. Build and Run

## What you need

- A C++17 compiler.
- CMake 3.16 or newer.

## Build

From the repository's main folder:

```bash
cmake -S . -B build
cmake --build build
```

## Run on Windows

```powershell
.\build\Release\huffman.exe compress examples\input.txt output.huff
.\build\Release\huffman.exe decompress output.huff restored.txt
```

If your build puts the executable directly in `build`, use:

```powershell
.\build\huffman.exe compress examples\input.txt output.huff
```

## Run on Linux or macOS

```bash
./build/huffman compress examples/input.txt output.huff
./build/huffman decompress output.huff restored.txt
```

## Run tests

```bash
python tests/test_roundtrip.py build/huffman
```

On Windows, give the executable's actual path, often:

```powershell
python tests/test_roundtrip.py build/Release/huffman.exe
```
