```toml
[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[project]
name = "mock-repository"
version = "0.1.0"
description = "A sample Python project for testing codebase analysis"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.2.0",
    "fastapi>=0.104.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.black]
line-length = 88
```
