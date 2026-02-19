

```
# Mock Project

A mock repository for testing the codebase context analysis node.

## Overview

This project simulates a real repository with source code, configuration,
and documentation files. It is used by the test suite for Issue #401
(Codebase Context Analysis for Requirements Workflow).

## Features

- Authentication module (src/auth.py)
- Main application entry point (src/main.py)
- Standard Python project layout with pyproject.toml

## Getting Started

```bash
pip install -e .
python -m src.main
```

## Architecture

The project follows a simple flat module structure under `src/`.
All modules use snake_case naming and absolute imports.
```
