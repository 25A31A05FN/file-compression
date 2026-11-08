#!/usr/bin/env python3
"""Simple end-to-end tests for the Huffman command-line program.

Run after building:
    python tests/test_roundtrip.py build/huffman
On Windows, use:
    python tests/test_roundtrip.py build/Release/huffman.exe
"""

import hashlib
import pathlib
import subprocess
import sys
import tempfile

if len(sys.argv) != 2:
    print("Usage: python tests/test_roundtrip.py <path-to-huffman-executable>")
    raise SystemExit(2)

program = pathlib.Path(sys.argv[1]).resolve()
if not program.exists():
    raise SystemExit(f"Executable not found: {program}")

test_data = {
    "empty": b"",
    "one_byte_value": b"Z" * 500,
    "simple_text": b"AAAAABBBCC",
    "all_byte_values": bytes(range(256)) * 3,
    "binary_data": bytes([0, 255, 10, 13, 0, 128, 64, 32]) * 100,
}

with tempfile.TemporaryDirectory() as temp_dir:
    folder = pathlib.Path(temp_dir)

    for name, original in test_data.items():
        source = folder / f"{name}.bin"
        compressed = folder / f"{name}.huff"
        restored = folder / f"{name}.restored"
        source.write_bytes(original)

        subprocess.run(
            [str(program), "compress", str(source), str(compressed)],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [str(program), "decompress", str(compressed), str(restored)],
            check=True,
            capture_output=True,
            text=True,
        )

        original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        restored_hash = hashlib.sha256(restored.read_bytes()).hexdigest()
        if original_hash != restored_hash:
            raise AssertionError(f"Round-trip test failed: {name}")

        print(f"PASS: {name}")

print("All round-trip tests passed.")
