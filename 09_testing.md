# 9. Testing the Project

Testing checks that the program works for different kinds of input.

Try these cases:

| Test | What to check |
|---|---|
| Normal text file | Restored file matches original |
| Empty file | Decompression creates an empty file |
| One repeated byte | All bytes are restored |
| Many different bytes | All byte values are handled |
| Binary file | Exact bytes are restored |
| Wrong compressed file | Program displays an error |
| Missing input file | Program displays an error |

## Compare files

After compressing and decompressing, compare the original file with the restored file.

On Windows PowerShell:

```powershell
Get-FileHash examples\input.txt
Get-FileHash restored.txt
```

The two hash values should be the same.

On Linux or macOS:

```bash
cmp examples/input.txt restored.txt
```

No output means the files match.
