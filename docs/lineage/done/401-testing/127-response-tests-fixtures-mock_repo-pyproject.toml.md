```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "mock-project"
version = "1.0.0"
description = "A mock project for testing codebase context analysis"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.1.0",
    "fastapi>=0.100.0",
    "pytest>=7.0.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]

[tool.ruff]
line-length = 88
target-version = "py311"
```
