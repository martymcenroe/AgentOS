```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mock-project"
version = "0.1.0"
description = "A mock Python project for testing codebase context analysis"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "fastapi>=0.100.0",
    "pytest>=7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
line-length = 88
target-version = "py311"
```
