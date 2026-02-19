

```python
[tool.poetry]
name = "mock-project"
version = "0.1.0"
description = "A mock project for testing codebase context analysis"

[tool.poetry.dependencies]
python = "^3.11"
langgraph = "^0.1.0"
fastapi = "^0.100.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"

[project]
name = "mock-project"
version = "0.1.0"
description = "A mock project for testing codebase context analysis"
dependencies = [
    "langgraph>=0.1.0",
    "fastapi>=0.100.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
]

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
