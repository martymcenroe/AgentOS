# Setting Up a New Project with AssemblyZero

## Generate Configs

```bash
poetry run --directory /c/Users/mcwiz/Projects/AssemblyZero python /c/Users/mcwiz/Projects/AssemblyZero/tools/assemblyzero-generate.py --project YOUR_PROJECT
```

Where the AssemblyZero root is configured in `~/.assemblyzero/config.json` (see `assemblyzero-config.md`).

## Manual Setup

1. Create `.claude/project.json` (copy from AssemblyZero example)
2. Edit variables for your project
3. Run the generator above
4. Create project-specific `CLAUDE.md` if needed

## Project Structure

Each project gets:
- `.claude/project.json` - Project-specific variables
- `CLAUDE.md` - Project-specific workflows
- If using full workflow: add `**Workflow:** Read AssemblyZero/WORKFLOW.md` to CLAUDE.md
