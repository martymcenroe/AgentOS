```toml
[tool.poetry]
name = "mock-repository"
version = "0.1.0"
description = "A sample Python project for testing codebase context analysis"

[tool.poetry.dependencies]
python = "^3.11"
langgraph = "^0.1.0"
fastapi = "^0.100.0"
pydantic = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
black = "^23.0"

[project]
name = "mock-repository"
version = "0.1.0"
description = "A sample Python project for testing codebase context analysis"
requires-python = ">=3.11"
dependencies = [
    "langgraph>=0.1.0",
    "fastapi>=0.100.0",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4",
    "black>=23.0",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
