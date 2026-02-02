I need to add `.agentos/` to the `.gitignore` file as specified in the LLD. The test checks for this pattern in the project's `.gitignore`.

```gitignore
# File: .gitignore (append to existing file)

# Per-repo AgentOS workflow database
.agentos/
```

Note: The `.gitignore` entry should be appended to the existing `.gitignore` file in the repository. If you're using the Edit tool, you would add this line to the end of the existing `.gitignore` file.