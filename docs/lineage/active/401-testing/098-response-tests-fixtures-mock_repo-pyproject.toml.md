```toml
[tool.poetry]
name = "mock-project"
version = "0.1.0"
description = "A sample Python project for testing codebase analysis"

[project]
name = "mock-project"
version = "0.1.0"
description = "A sample Python project for testing codebase analysis"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.1.0",
    "fastapi>=0.100.0",
    "pytest>=7.0.0",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.pytest.ini_options]
testpaths = ["tests"]
```
