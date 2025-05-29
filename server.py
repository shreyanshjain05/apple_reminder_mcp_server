from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import asyncio
import json
import os
import subprocess
import datetime
from typing import Optional

load_dotenv()
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")

mcp = FastMCP(
    "mcp-apple-reminders",
    description="MCP server for managing Apple Reminder",
    host=HOST,
    port=PORT
)

def run_applescript(script: str) -> str:
    """Execute AppleScript and return the result"""
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with return code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return ""

@mcp.tool()
async def create_reminder(
    title: str,
    due_date: datetime.date,
    due_time: Optional[str] = None,
    notes: Optional[str] = None,
    list_name: Optional[str] = "Reminder Created using Agent",
    location: Optional[str] = None,
) -> str:
    """
    Create a new reminder in Apple Reminder.
    Args:
        title: The title of the reminder
        due_date: Required due date (datetime.date)
        due_time: Required due time (Default 9 AM)
        notes: Optional notes/body text for the reminder
        list_name: Name of the reminders list (default: "Reminder Created using Agent")
        location: Location where reminder has to get activated
    Returns:
        Success message with reminder details 
    """
    try:
        # Handle time input
        if due_time:
            # Convert string to time object
            due_time_obj = datetime.time(
                int(due_time[:2]),   # hour
                int(due_time[2:4]),  # minute
                int(due_time[4:])    # second
            )
        else:
            due_time_obj = datetime.time(9, 0, 0)  # Default to 9:00 AM

        # Combine date and time
        full_due_datetime = datetime.datetime.combine(due_date, due_time_obj)

        # Format for AppleScript
        applescript_date = full_due_datetime.strftime('date "%-d %B %Y %H:%M:%S"')  # e.g., date "1 June 2025 15:30:00"

        script_part = [
            'tell application "Reminders"',
            f'set newReminder to make new reminder with properties {{name:"{title}", due date:{applescript_date}'
        ]
        
        if notes:
            script_part[-1] += f', body:"{notes}"'
        if location:
            script_part[-1] += f', location:"{location}"'
        script_part[-1] += '}'

        script_part.extend([
            f'set targetList to list "{list_name}"',
            'move newReminder to targetList',
            'end tell'
        ])

        script = "\n".join(script_part)
        result = run_applescript(script)
        return f"Reminder '{title}' created successfully in list '{list_name}'. AppleScript Output: {result}"
    except Exception as e:
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
        list_name: The name of the reminder list (default is all lists).
        completed: Whether to fetch completed reminders (default is False).
        limit: Max number of reminders to fetch (default is 20).
    
    Returns:
        A JSON-formatted string of reminders.
    """
    try:
        if not list_name:
            return json.dumps({"error": "list_name is required"}, indent=2)

        # Simplified AppleScript with better error handling
        completed_str = "true" if completed else "false"
        
        script = f'''
tell application "Reminders"
    set output to ""
    try
        set targetList to list "{list_name}"
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
        if list_name:
            # Search in specific list
            script = f'''
tell application "Reminders"
    set deletedCount to 0
    try
        set targetList to list "{list_name}"
        set allReminders to reminders of targetList
        
        repeat with currentReminder in allReminders
            if name of currentReminder is "{name}" then
                delete currentReminder
                set deletedCount to deletedCount + 1
            end if
        end repeat
        
        if deletedCount > 0 then
            return "SUCCESS: Deleted " & deletedCount & " reminder(s) named '" & "{name}" & "' from list '" & "{list_name}" & "'"
        else
            return "NOT_FOUND: No reminder named '" & "{name}" & "' found in list '" & "{list_name}" & "'"
        end if
        
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''
        else:
            # Search in all lists
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
                if name of currentReminder is "{name}" then
                    delete currentReminder
                    set deletedCount to deletedCount + 1
                end if
            end repeat
        end repeat
        
        if deletedCount > 0 then
            return "SUCCESS: Deleted " & deletedCount & " reminder(s) named '" & "{name}" & "'"
        else
            return "NOT_FOUND: No reminder named '" & "{name}" & "' found in any list. Searched lists: " & searchedLists
        end if
        
    on error errorMessage
        return "ERROR: " & errorMessage
    end try
end tell
'''

        result = run_applescript(script)
        
        if result.startswith("SUCCESS:"):
            return f" {result[8:]}"  # Remove "SUCCESS:" prefix
        elif result.startswith("NOT_FOUND:"):
            return f" {result[10:]}"  # Remove "NOT_FOUND:" prefix
        elif result.startswith("ERROR:"):
            return f" {result}"
        else:
            return f"Reminder deletion completed. {result}"
            
    except Exception as e:
        return f"Failed to delete reminder: {str(e)}"

if __name__ == "__main__":
    import asyncio

    async def test_functions():
        print("=== Creating a test reminder ===")
        create_result = await create_reminder(
            title="Test Reminder",
            due_date=datetime.date(2026, 5, 30),
            notes="This is a test note",
            list_name="Reminders"
        )
        print(create_result)

        print("\n=== Getting reminders from 'Reminders' list ===")
        get_result = await get_reminder(list_name='Reminders')
        print(get_result)

        print("\n=== Listing all available reminder lists ===")
        list_result = await list_reminder_lists()
        print(list_result)

        print("\n=== Deleting the test reminder ===")
        delete_result = await delete_reminder(name="Test Reminder", list_name="Reminders")
        print(delete_result)

    asyncio.run(test_functions())
