# Ideas Folder (Encrypted Pre-Issue Ideation)

Every repo can have an `ideas/` folder for capturing thoughts before they're ready to become issues.

## Setup (Using Generator)

```bash
poetry run --directory $AGENTOS_ROOT python $AGENTOS_ROOT/tools/assemblyzero-generate.py --project YOUR_PROJECT --ideas
```

## Setup (Manual for git-crypt)

```bash
# 1. Initialize git-crypt in repo
git-crypt init

# 2. Export and store key securely
git-crypt export-key ../your-project-ideas.key
# Store in 1Password as "your-project-ideas-key"
# Then DELETE the .key file!

# 3. Commit the setup
git add .gitattributes ideas/
git commit -m "feat: add encrypted ideas folder"
```

## Unlocking on a New Machine

```bash
# Get key from 1Password, save to temp file via clipboard (NOT echo!)
pbpaste | base64 -d > /tmp/repo.key            # macOS
# OR: xclip -selection clipboard -o | base64 -d > /tmp/repo.key   # Linux
# OR: powershell -c "Get-Clipboard" | base64 -d > /tmp/repo.key   # Windows

git-crypt unlock /tmp/repo.key
rm /tmp/repo.key
```

**SECURITY WARNING:** Never use `echo "KEY" | base64 -d > file` - this leaks the key to shell history.

## Windows Installation

```bash
choco install git-crypt   # or: scoop install git-crypt
```
