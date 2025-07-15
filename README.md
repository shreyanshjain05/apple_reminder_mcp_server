# Apple Reminders MCP Server - Documentation

## README.md

```markdown
# Apple Reminders MCP Server

A Model Context Protocol (MCP) server that enables AI assistants to interact with Apple Reminders on macOS. This server provides tools to create, read, list, and delete reminders programmatically through AppleScript.

## Features

- ✅ Create reminders with due dates, times, notes, and locations
- 📋 List all reminder lists
- 🔍 Fetch reminders from specific lists (completed or pending)
- 🗑️ Delete reminders by name
- 🤖 Compatible with Claude Desktop and other MCP clients
- 🍎 Native macOS integration via AppleScript

## Prerequisites

- macOS (required for AppleScript)
- Python 3.10 or higher
- Apple Reminders app

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/apple-reminder-mcp-server.git
cd apple-reminder-mcp-server
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install mcp fastmcp python-dotenv
```

## Configuration

The server uses stdio transport by default, no additional configuration needed.

## Usage

### Running the Server

```bash
python3 server.py
```

### Testing with MCP Inspector

The MCP Inspector is a web-based tool for testing MCP servers. Follow these steps to test your server:

#### 1. Launch MCP Inspector

```bash
npx @modelcontextprotocol/inspector stdio "python3 server.py"
```

This will:
- Start a proxy server on `localhost:6277`
- Open the inspector interface in your browser at `http://localhost:6274`
- Display a session token for authentication

#### 2. Configure Connection Settings

When the inspector opens in your browser, configure the connection with these settings:

- **Transport Type**: `STDIO`
- **Command**: `python3`
- **Arguments**: `/Users/shreyanshjain/apple_reminder_mcp_server/server.py`

> Note: Replace the path in Arguments with the actual path to your server.py file

#### 3. Connect to the Server

Click "Connect" to establish connection with your MCP server. You should see:
- Server status change to "Connected"
- List of available tools in the interface

#### 4. Test the Tools

**Example: Testing create_reminder**

1. Select `create_reminder` from the tools list
2. Fill in the parameters:
   ```json
   {
     "title": "Test Reminder",
     "due_date": "2024-12-25",
     "due_time": "140000",
     "notes": "This is a test reminder",
     "list_name": "Reminder Created using Agent"
   }
   ```
3. Click "Execute"
4. Check the response:
   ```json
   {
     "result": "Reminder 'Test Reminder' created successfully in list 'Reminder Created using Agent'. AppleScript Output: "
   }
   ```

**Example: Testing list_reminder_lists**

1. Select `list_reminder_lists` from the tools list
2. No parameters needed
3. Click "Execute"
4. View your reminder lists in the response

**Example: Testing get_reminder**

1. Select `get_reminder` from the tools list
2. Fill in parameters:
   ```json
   {
     "list_name": "Reminder Created using Agent",
     "completed": false,
     "limit": 10
   }
   ```
3. Click "Execute"
4. View the reminders in the specified list

### Integration with Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "apple-reminders": {
      "command": "python3",
      "args": ["/path/to/your/apple_reminder_mcp_server/server.py"]
    }
  }
}
```

## Available Tools

### 1. create_reminder

Creates a new reminder in Apple Reminders.

**Parameters:**
- `title` (required): The title of the reminder
- `due_date` (required): Due date in YYYY-MM-DD format
- `due_time` (optional): Time in HHMMSS format (default: 090000 for 9 AM)
- `notes` (optional): Additional notes/body text
- `list_name` (optional): Target list name (default: "Reminder Created using Agent")
- `location` (optional): Location for location-based reminders

**Example Request:**
```json
{
  "title": "Team Meeting",
  "due_date": "2024-12-25",
  "due_time": "140000",
  "notes": "Discuss Q1 goals",
  "list_name": "Work"
}
```

**Example Response:**
```json
{
  "result": "Reminder 'Team Meeting' created successfully in list 'Work'. AppleScript Output: "
}
```

### 2. get_reminder

Fetches reminders from a specific list.

**Parameters:**
- `list_name` (required): Name of the reminder list
- `completed` (optional): Whether to fetch completed reminders (default: false)
- `limit` (optional): Maximum number of reminders to return (default: 20)

**Example Response:**
```json
[
  {
    "name": "Team Meeting",
    "body": "Discuss Q1 goals",
    "due_date": "Wednesday, December 25, 2024 at 2:00:00 PM",
    "completed": false
  }
]
```

### 3. list_reminder_lists

Returns all available reminder lists.

**Parameters:** None

**Example Response:**
```json
[
  "Reminders",
  "Work",
  "Personal",
  "Shopping",
  "Reminder Created using Agent"
]
```

### 4. delete_reminder

Deletes a reminder by name.

**Parameters:**
- `name` (required): The exact name of the reminder to delete
- `list_name` (optional): Specific list to search in (searches all lists if not provided)

**Example Response:**
```json
{
  "result": "Deleted 1 reminder(s) named 'Team Meeting' from list 'Work'"
}
```

## Output Schema

All tools return responses following this schema:

```json
{
  "type": "object",
  "properties": {
    "result": {
      "title": "Result",
      "type": "string"
    }
  },
  "required": ["result"],
  "title": "ToolOutput"
}
```

## Project Structure

```
apple_reminder_mcp_server/
├── server.py           # Main MCP server implementation
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore file
└── README.md          # This file
```

## Troubleshooting

### Common Issues

1. **"spawn python3 ENOENT" error in MCP Inspector**
   - Use separate fields for command and arguments
   - Command: `python3`
   - Arguments: `/full/path/to/server.py`

2. **"No reminder list found" error**
   - Make sure the list name exactly matches (case-sensitive)
   - Use `list_reminder_lists` to see available lists

3. **Permission errors with AppleScript**
   - Grant Terminal/IDE permission to control Reminders in System Preferences > Security & Privacy > Automation

4. **MCP Inspector connection issues**
   - Ensure the path in Arguments is absolute, not relative
   - Check that Python 3 is in your system PATH
   - Try using the full Python path: `/usr/bin/python3` or `/opt/homebrew/bin/python3`

### Debug Mode

To enable debug logging, modify the logging level in server.py:
```python
logging.basicConfig(level=logging.DEBUG)
```

### Verifying Server Operation

You can verify the server is working by checking the terminal output:
```
INFO:root:Starting MCP server with stdio transport...
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [FastMCP](https://github.com/modelcontextprotocol/fastmcp)
- Uses AppleScript for native macOS integration
- Compatible with the [Model Context Protocol](https://modelcontextprotocol.io)

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Ensure you're running on macOS with proper permissions

---
