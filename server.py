"""Apple Reminders MCP Server implementation."""

from mcp.server.fastmcp import FastMCP
import json
import subprocess
import datetime
from typing import Optional
import logging
from dateutil import parser as date_parser

__version__ = "0.1.0"

logging.basicConfig(level=logging.INFO)

mcp = FastMCP("mcp-apple-reminders")


def sanitize_for_applescript(text: str) -> str:
    """
    Sanitize user input to prevent AppleScript injection.
    
    Escapes backslashes and double quotes which could break or exploit AppleScript.
    """
    if text is None:
        return ""
    # Escape backslashes first, then double quotes
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    return text


def run_applescript(script: str) -> str:
    """Execute AppleScript and return the result."""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"AppleScript failed with return code {e.returncode}: {e.stderr}")
        return ""


@mcp.tool()
async def create_reminder(
    title: str,
    due_date: str,
    due_time: Optional[str] = None,
    notes: Optional[str] = None,
    list_name: Optional[str] = "Reminder Created using Agent",
    location: Optional[str] = None,
) -> str:
    """
    Create a new reminder in Apple Reminder.
    
    Args:
        title: The title of the reminder
        due_date: Due date (e.g. "2024-12-25", "tomorrow", "next Friday", "30 Jan 2026")
        due_time: Due time in HHMMSS format (default: 090000 for 9 AM)
        notes: Optional notes/body text for the reminder
        list_name: Name of the reminders list (default: "Reminder Created using Agent")
        location: Location where reminder has to get activated
        
    Returns:
        Success message with reminder details
    """
    try:
        # Parse date
        try:
            due_date_obj = date_parser.parse(due_date).date()
        except Exception:
            return f"Error: Could not parse date '{due_date}'. Please use a format like YYYY-MM-DD or 'tomorrow'."

        # Handle time input
        if due_time:
            try:
                due_time_obj = datetime.time(
                    int(due_time[:2]),
                    int(due_time[2:4]),
                    int(due_time[4:]) if len(due_time) > 4 else 0
                )
            except (ValueError, IndexError):
                return f"Error: Invalid time format '{due_time}'. Use HHMMSS format (e.g., 140000 for 2 PM)."
        else:
            due_time_obj = datetime.time(9, 0, 0)

        # Combine date and time
        full_due_datetime = datetime.datetime.combine(due_date_obj, due_time_obj)

        # Format for AppleScript
        applescript_date = full_due_datetime.strftime('date "%-d %B %Y %H:%M:%S"')

        # Sanitize all user inputs
        safe_title = sanitize_for_applescript(title)
        safe_notes = sanitize_for_applescript(notes) if notes else None
        safe_location = sanitize_for_applescript(location) if location else None
        safe_list_name = sanitize_for_applescript(list_name)

        script_parts = [
            'tell application "Reminders"',
            f'set newReminder to make new reminder with properties {{name:"{safe_title}", due date:{applescript_date}'
        ]
        
        if safe_notes:
            script_parts[-1] += f', body:"{safe_notes}"'
        if safe_location:
            script_parts[-1] += f', location:"{safe_location}"'
        script_parts[-1] += '}'

        script_parts.extend([
            f'set targetList to list "{safe_list_name}"',
            'move newReminder to targetList',
            'end tell'
        ])

        script = "\n".join(script_parts)
        result = run_applescript(script)
        return f"Reminder '{title}' created successfully in list '{list_name}'. AppleScript Output: {result}"
    except Exception as e:
        logging.exception("Failed to create reminder")
        return f"Failed to create reminder: {str(e)}"


@mcp.tool()
async def get_reminder(
    list_name: Optional[str] = None,
    completed: bool = False,
    limit: int = 20
) -> str:
    """
    Get reminders from Apple Reminders.
    
    Args:
        list_name: The name of the reminder list (required).
        completed: Whether to fetch completed reminders (default: False).
        limit: Max number of reminders to fetch (default: 20).
    
    Returns:
        A JSON-formatted string of reminders.
    """
    try:
        if not list_name:
            return json.dumps({"error": "list_name is required"}, indent=2)

        safe_list_name = sanitize_for_applescript(list_name)
        completed_str = "true" if completed else "false"
        
        script = f'''
tell application "Reminders"
    set output to ""
    try
        set targetList to list "{safe_list_name}"
        set allReminders to reminders of targetList
        
        repeat with currentReminder in allReminders
            set isCompleted to completed of currentReminder
            if (isCompleted as string) is "{completed_str}" then
                set reminderName to name of currentReminder
                
                set reminderBody to ""
                try
                    set reminderBody to body of currentReminder
                on error
                    set reminderBody to ""
                end try
                
                set reminderDue to ""
                try
                    set reminderDue to (due date of currentReminder) as string
                on error
                    set reminderDue to ""
                end try
                
                set completedStatus to (completed of currentReminder) as string
                
                set output to output & reminderName & "|||" & reminderBody & "|||" & reminderDue & "|||" & completedStatus & "\\n"
            end if
        end repeat
        
        return output
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''

        result = run_applescript(script)
        
        if not result or result.startswith("ERROR:"):
            if result.startswith("ERROR:"):
                return json.dumps({"error": result}, indent=2)
            return json.dumps([], indent=2)

        # Parse the delimited result
        reminders = []
        lines = result.strip().split('\n')
        
        for line in lines:
            if line.strip():
                parts = line.split('|||')
                if len(parts) >= 4:
                    reminder_data = {
                        "name": parts[0],
                        "body": parts[1] if parts[1] else "",
                        "due_date": parts[2] if parts[2] else "",
                        "completed": parts[3] == "true"
                    }
                    reminders.append(reminder_data)
                    if len(reminders) >= limit:
                        break

        return json.dumps(reminders, indent=2)

    except Exception as e:
        logging.exception("Failed to get reminders")
        return json.dumps({"error": f"Failed to get reminders: {str(e)}"}, indent=2)


@mcp.tool()
async def list_reminder_lists() -> str:
    """
    Get all available reminder lists.
    
    Returns:
        A JSON-formatted string of reminder list names.
    """
    try:
        script = '''
tell application "Reminders"
    set listNames to ""
    try
        set allLists to every list
        repeat with currentList in allLists
            set listNames to listNames & (name of currentList) & "\\n"
        end repeat
        return listNames
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''
        
        result = run_applescript(script)
        
        if not result:
            return json.dumps([], indent=2)
            
        if result.startswith("ERROR:"):
            return json.dumps({"error": result}, indent=2)
            
        list_names = [name.strip() for name in result.strip().split('\n') if name.strip()]
        return json.dumps(list_names, indent=2)
        
    except Exception as e:
        logging.exception("Failed to get reminder lists")
        return json.dumps({"error": f"Failed to get reminder lists: {str(e)}"}, indent=2)


@mcp.tool()
async def delete_reminder(
    name: str,
    list_name: Optional[str] = None
) -> str:
    """
    Delete a reminder by name.
    
    Args:
        name: The name/title of the reminder to delete
        list_name: Optional specific list to search in. If not provided, searches all lists.
    
    Returns:
        Completion message indicating success or failure
    """
    try:
        safe_name = sanitize_for_applescript(name)
        
        if list_name:
            safe_list_name = sanitize_for_applescript(list_name)
            script = f'''
tell application "Reminders"
    set deletedCount to 0
    try
        set targetList to list "{safe_list_name}"
        set allReminders to reminders of targetList
        
        repeat with currentReminder in allReminders
            if name of currentReminder is "{safe_name}" then
                delete currentReminder
                set deletedCount to deletedCount + 1
            end if
        end repeat
        
        if deletedCount > 0 then
            return "SUCCESS: Deleted " & deletedCount & " reminder(s) named '{name}' from list '{list_name}'"
        else
            return "NOT_FOUND: No reminder named '{name}' found in list '{list_name}'"
        end if
        
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''
        else:
            script = f'''
tell application "Reminders"
    set deletedCount to 0
    set searchedLists to ""
    try
        set allLists to every list
        
        repeat with currentList in allLists
            set listName to name of currentList
            set searchedLists to searchedLists & listName & ", "
            set allReminders to reminders of currentList
            
            repeat with currentReminder in allReminders
                if name of currentReminder is "{safe_name}" then
                    delete currentReminder
                    set deletedCount to deletedCount + 1
                end if
            end repeat
        end repeat
        
        if deletedCount > 0 then
            return "SUCCESS: Deleted " & deletedCount & " reminder(s) named '{name}'"
        else
            return "NOT_FOUND: No reminder named '{name}' found in any list. Searched lists: " & searchedLists
        end if
        
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''

        result = run_applescript(script)
        
        if result.startswith("SUCCESS:"):
            return result[9:]
        elif result.startswith("NOT_FOUND:"):
            return result[11:]
        elif result.startswith("ERROR:"):
            return result
        else:
            return f"Reminder deletion completed. {result}"
            
    except Exception as e:
        logging.exception("Failed to delete reminder")
        return f"Failed to delete reminder: {str(e)}"


def main():
    """Entry point for the MCP server."""
    logging.info("Starting Apple Reminders MCP server...")
    mcp.run()


if __name__ == "__main__":
    main()
