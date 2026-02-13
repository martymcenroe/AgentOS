# AssemblyZero Configuration

## Path Configuration

AssemblyZero paths are configured in `~/.assemblyzero/config.json`:

| Variable | Default (Unix) | Used For |
|----------|----------------|----------|
| `assemblyzero_root` | `/c/Users/mcwiz/Projects/AssemblyZero` | Tool execution, config source |
| `projects_root` | `/c/Users/mcwiz/Projects` | Project detection |
| `user_claude_dir` | `/c/Users/mcwiz/.claude` | User-level commands |

**If the config file doesn't exist, defaults are used.**

## Customizing Paths

1. Copy `AssemblyZero/.assemblyzero/config.example.json` to `~/.assemblyzero/config.json`
2. Edit paths for your machine
3. Both Windows and Unix formats are required (tools use different formats)

## Python Import

Tools import paths via:

```python
from assemblyzero_config import config
root = config.assemblyzero_root()            # Windows format
root_unix = config.assemblyzero_root_unix()  # Unix format
```

## Configuration Files

- `~/.assemblyzero/hard_block_commands.txt` - Additional patterns to block
- `~/.assemblyzero/safe_paths.txt` - Paths where destructive commands are allowed
