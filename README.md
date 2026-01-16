# Apple Reminders MCP Server

[![PyPI version](https://badge.fury.io/py/apple-reminders-mcp.svg)](https://badge.fury.io/py/apple-reminders-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/shreyanshjain05/apple_reminder_mcp_server/actions/workflows/test.yml/badge.svg)](https://github.com/shreyanshjain05/apple_reminder_mcp_server/actions/workflows/test.yml)

A Model Context Protocol (MCP) server that enables AI assistants to interact with Apple Reminders on macOS. This server provides tools to create, read, list, and delete reminders programmatically through AppleScript.

## Features

- ✅ Create reminders with due dates, times, notes, and locations
- 📋 List all reminder lists
- 🔍 Fetch reminders from specific lists (completed or pending)
- 🗑️ Delete reminders by name
- 🤖 Compatible with Claude Desktop and other MCP clients
- 🍎 Native macOS integration via AppleScript
- 🔒 Input sanitization to prevent AppleScript injection

## Demo


https://github.com/user-attachments/assets/d36e0df3-ff4b-4f48-bb29-41ddb5483c6b



## Prerequisites

- macOS (required for AppleScript)
- Python 3.10 or higher
- Apple Reminders app

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install apple-reminders-mcp
```

### Option 2: Install from source

```bash
git clone https://github.com/shreyanshjain05/apple_reminder_mcp_server.git
cd apple_reminder_mcp_server
pip install -e .
```

## Usage

### Running the Server

If installed via pip:
```bash
apple-reminders-mcp
```

Or run directly:
```bash
python -m apple_reminders_mcp.server
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector python3 server.py
```

This will:
- Start a proxy server on `localhost:6277`
- Open the inspector interface in your browser at `http://localhost:6274`
- Display a session token for authentication

### Integration with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "apple-reminders": {
      "command": "python3",
      "args": ["/path/to/apple_reminder_mcp_server/server.py"]
    }
  }
}
```

> **Note**: Replace `/path/to/` with the actual path where you cloned the repo. If you get "Server disconnected" errors, use the full path to your Python executable (run `which python3` to find it).


## Available Tools

### 1. create_reminder

Creates a new reminder in Apple Reminders.

**Parameters:**
- `title` (required): The title of the reminder
- `due_date` (required): Due date (e.g., "2024-12-25", "tomorrow", "next Friday")
- `due_time` (optional): Time in HHMMSS format (default: 090000 for 9 AM)
- `notes` (optional): Additional notes/body text
- `list_name` (optional): Target list name (default: "Reminder Created using Agent")
- `location` (optional): Location for location-based reminders

**Example:**
```json
{
  "title": "Team Meeting",
  "due_date": "tomorrow",
  "due_time": "140000",
  "notes": "Discuss Q1 goals",
  "list_name": "Work"
}
```

### 2. get_reminder

Fetches reminders from a specific list.

**Parameters:**
- `list_name` (required): Name of the reminder list
- `completed` (optional): Whether to fetch completed reminders (default: false)
- `limit` (optional): Maximum number of reminders to return (default: 20)

### 3. list_reminder_lists

Returns all available reminder lists. No parameters required.

### 4. delete_reminder

Deletes a reminder by name.

**Parameters:**
- `name` (required): The exact name of the reminder to delete
- `list_name` (optional): Specific list to search in (searches all lists if not provided)

## Troubleshooting

### Common Issues

1. **Permission errors with AppleScript**
   - Grant Terminal/IDE permission to control Reminders in System Preferences → Security & Privacy → Automation

2. **"No reminder list found" error**
   - Make sure the list name exactly matches (case-sensitive)
   - Use `list_reminder_lists` to see available lists

3. **Date parsing errors**
   - Use standard formats like "YYYY-MM-DD" or natural language like "tomorrow"

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Project Structure

```
apple_reminder_mcp_server/
├── apple_reminders_mcp/
│   ├── __init__.py
│   └── server.py          # Main MCP server implementation
├── tests/
│   └── test_server.py     # Unit tests
├── .github/workflows/
│   ├── test.yml           # CI testing
│   └── publish.yml        # PyPI publishing
├── pyproject.toml         # Package configuration
└── README.md
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/modelcontextprotocol/fastmcp)
- Uses AppleScript for native macOS integration
- Compatible with the [Model Context Protocol](https://modelcontextprotocol.io)
