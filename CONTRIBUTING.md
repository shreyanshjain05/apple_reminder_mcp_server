# Contributing to Apple Reminders MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/shreyanshjain05/apple_reminder_mcp_server.git
   cd apple_reminder_mcp_server
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:
   ```bash
   pytest tests/ -v
   ```

4. Commit with a descriptive message:
   ```bash
   git commit -m "Add: description of your change"
   ```

5. Push and create a Pull Request

## Code Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints
- **Always sanitize user inputs** using `sanitize_for_applescript()` before including in AppleScript

## Testing

- Add tests for new functionality in `tests/test_server.py`
- Ensure all tests pass before submitting a PR
- Tests run automatically on PRs via GitHub Actions

## Reporting Issues

When reporting issues, please include:
- macOS version
- Python version
- Steps to reproduce
- Expected vs actual behavior

## Questions?

Open an issue for any questions or suggestions!
