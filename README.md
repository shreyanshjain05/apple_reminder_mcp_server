# MCP Apple Reminders Server

A Model Context Protocol (MCP) server that provides programmatic access to Apple Reminders through FastMCP. This server allows you to create, read, list, and delete reminders using AppleScript integration.

## Features

- **Create Reminders**: Add new reminders with due dates, times, notes, and locations
- **Get Reminders**: Retrieve reminders from specific lists (completed or pending)
- **List Reminder Lists**: View all available reminder lists
- **Delete Reminders**: Remove reminders by name from specific lists or all lists

## Prerequisites

- macOS (required for Apple Reminders and AppleScript)
- Python 3.7+
- Apple Reminders app

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mcp-apple-reminders
```

2. Install dependencies:
```bash
pip install fastmcp python-dotenv
```

3. Create a `.env` file in the project root:
```env
HOST=localhost
PORT=8000
```

## Usage

### Running the Server

```bash
python mcp_apple_reminders.py
```

The server will start on the configured host and port (default: localhost:8000).

### Available Tools

#### 1. Create Reminder

Create a new reminder with specified details.

**Parameters:**
- `title` (required): The title of the reminder
- `due_date` (required): Due date as datetime.date object
- `due_time` (optional): Due time in HHMMSS format (default: 09:00:00)
- `notes` (optional): Additional notes for the reminder
- `list_name` (optional): Target list name (default: "Reminder Created using Agent")
- `location` (optional): Location for location-based reminders

**Example:**
```python
await create_reminder(
    title="Team Meeting",
    due_date=datetime.date(2024, 12, 25),
    due_time="143000",  # 2:30 PM
    notes="Discuss Q4 goals",
    list_name="Work"
)
```

#### 2. Get Reminders

Retrieve reminders from a specific list.

**Parameters:**
- `list_name` (required): The name of the reminder list
- `completed` (optional): Whether to fetch completed reminders (default: False)
- `limit` (optional): Maximum number of reminders to return (default: 20)

**Example:**
```python
await get_reminder(
    list_name="Work",
    completed=False,
    limit=10
)
```

**Returns:** JSON array of reminders with name, body, due_date, and completed status.

#### 3. List Reminder Lists

Get all available reminder lists.

**Example:**
```python
await list_reminder_lists()
```

**Returns:** JSON array of list names.

#### 4. Delete Reminder

Delete a reminder by name.

**Parameters:**
- `name` (required): The exact name of the reminder to delete
- `list_name` (optional): Specific list to search in (searches all lists if not provided)

**Example:**
```python
await delete_reminder(
    name="Team Meeting",
    list_name="Work"
)
```

## Architecture

The server uses:
- **FastMCP**: For creating the MCP server and exposing tools
- **AppleScript**: For interacting with the Apple Reminders app
- **subprocess**: For executing AppleScript commands
- **asyncio**: For asynchronous operations

## Error Handling

- All functions include try-catch blocks for error handling
- AppleScript errors are captured and returned as formatted error messages
- JSON responses include error fields when operations fail

## Limitations

- Only works on macOS due to AppleScript dependency
- Requires Apple Reminders app to be installed
- Location-based reminders may require additional permissions
- Date/time formatting must match AppleScript expectations

## Security Considerations

- The server runs locally by default
- No authentication is implemented - add authentication if exposing externally
- AppleScript commands are constructed with user input - ensure proper sanitization in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on macOS
5. Submit a pull request

