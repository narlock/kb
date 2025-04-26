"""
kb - settings.py
author: narlock

This file controls reading and writing settings to
~/Documents/narlock/kb/settings.json
"""

import ansi
import json
from pathlib import Path

SETTINGS_PATH = Path.home() / "Documents" / "narlock" / "kb" / "settings.json"

INITIAL_SETTINGS = {
    "recentProjectTitle": "kb",
    "nextProjectId": 1,
    "projects": [
        {
            "id": 0,
            "title": "kb",
            "nextTaskId": 1,
            "tasks": [
                {
                    "id": 0,
                    "title": "Task Title 1",
                    "type": "story",
                    "description": "Task description 1",
                    "acceptanceCriteria": "Acceptance Criteria for Task 1",
                    "priority": "medium",
                    "status": "todo",
                    "effort": 3,
                    "startDate": "2025-04-10",
                    "completeDate": None,
                    "tags": [ "tag1" ],
                    "fixVersion": "v1.0.0",
                    "linkedTasks": [
                        {
                            "id": 0,
                            "type": "task",
                            "reason": "blocked by"
                        }
                    ],
                    "checklistItems": [
                        {
                            "name": "Checklist Item Name 1",
                            "completed": False
                        }
                    ]
                }
            ]
        }
    ]
}

DEFAULT_PROJECT = {
    "id": -1,
    "title": "",
    "tasks": []
}

DEFAULT_TASK = {
    "id": -1,
    "title": "",
    "type": "story",
    "description": "",
    "acceptanceCriteria": "",
    "priority": "medium",
    "status": "backlog",
    "effort": 0,
    "startDate": "",
    "completeDate": None,
    "tags": [],
    "fixVersion": "",
    "linkedTasks": [],
    "checklistItems": []
}

TASK_OPTIONS = [None, "Title", "Type", "Description", "Acceptance Criteria",
                "Priority", "Status", "Effort", "Start Date", "Complete Date", "Fix Version",
                "Tags", "Linked Tasks", "Checklist"]
TASK_OPTION_KEYS = [None, "title", "type", "description", "acceptanceCriteria",
                "priority", "status", "effort", "startDate", None, "fixVersion",
                "tags", "linkedTasks", "checklistItems"]
TASK_OPTION_TYPES = [None, "str", "type", "str", "str", 
                    "priority", "status", "int", "date", None, "str",
                    "list-str", "list-int"]
TASK_TYPE_OPTIONS = ["story", "bug", "feature", "spike"]
TASK_PRIORITY_TYPE_OPTIONS = ["very low", "low", "medium", "high", "very high", "critical"]
TASK_STATUS_TYPE_OPTIONS = ["backlog", "todo", "doing", "done"]

def write_initial_settings():
    """
    Called when there is no settings.json, this function
    will create the initial settings inside of a newly
    created settings.json file. For whatever reason,
    if the settings.json file is tampered with, a
    suggestion to reset to default will be available
    and will call this function.
    """
    settings_dir = SETTINGS_PATH.parent
    settings_dir.mkdir(parents=True, exist_ok=True)
    
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(INITIAL_SETTINGS, f, indent=4)
    print("Initial settings.json file created.")

def update_settings(settings):
    """
    Updates the settings.json file with an updated
    settings object.
    """
    try:
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)
        print(f"\n{ansi.GREEN}{ansi.BOLD}Settings updated successfully.{ansi.RESET}")
    except Exception as e:
        print(f"{ansi.RED}{ansi.BOLD}Error updating settings: {e}{ansi.RESET}")

def load_settings():
    """
    Reads settings from $HOME/Documents/narlock/kb/settings.json.
    If any of the directories or paths do not exist, we will run
    write_initial_settings function, and then reload our settings.
    """
    if not SETTINGS_PATH.exists():
        print("Settings file not found. Creating initial settings.")
        write_initial_settings()
    
    try:
        with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}. Resetting to default.")
        write_initial_settings()
        return INITIAL_SETTINGS
    
def generate_task_map_for_project(settings, project_title):
    """
    Given the settings object and a title of a project, this function
    will return a map of each of the tasks within the todo, doing
    and done columns respectively.

    This function will be called and recalled to display updates
    to the kanban view of the program.
    """
    task_map = {
        "todo": [],
        "doing": [],
        "done": []
    }

    for project in settings.get("projects", []):
        if project.get("title") == project_title:
            for task in project.get("tasks", []):
                status = task.get("status", "").lower()
                if status in task_map:
                    task_map[status].append((task["id"], task["title"]))
                else:
                    task_map.setdefault(status, []).append((task["id"], task["title"]))
            break  # Found the project, no need to keep looping

    return task_map

def move_kanban_item_by_id(user_settings, project_title, item_id: int, column: str = None):
    """
    Moves the respective kanban item to the next or defined column.

    If `column` is None, it moves the task to the next column in the flow.
    Valid columns are: "backlog", "todo", "doing", "done".

    Returns:
        str: error message if something goes wrong
        None: on successful move
    """
    valid_columns = ["backlog", "todo", "doing", "done"]
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)

    if not project:
        return "Project not found."

    task = next((t for t in project["tasks"] if t["id"] == item_id), None)

    if not task:
        return f"Task with id {item_id} not found."

    current_status = task.get("status", "backlog")

    if column is None:
        try:
            current_index = valid_columns.index(current_status)
            if current_index < len(valid_columns) - 1:
                new_status = valid_columns[current_index + 1]
            else:
                return f"Task is already in the last column '{current_status}'."
        except ValueError:
            return f"Invalid current status '{current_status}' for task."
    else:
        if column not in valid_columns:
            return f"Invalid destination column '{column}'. Valid options: {valid_columns}"
        new_status = column

    task["status"] = new_status
    update_settings(user_settings)

def get_kanban_task_by_id(user_settings, project_title: str, item_id: int):
    """
    Retrieves a kanban task by ID from the specified project.

    Args:
        user_settings (dict): The full user settings data.
        project_title (str): The title of the project.
        item_id (int): The ID of the task to retrieve.

    Returns:
        dict: The task if found.
        str: Error message if the project or task is not found.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."

    # Get task
    task = next((t for t in project["tasks"] if t["id"] == item_id), None)
    if not task:
        return f"Task with id {item_id} not found."
    
    return task

def get_kanban_tasks(user_settings, project_title: str):
    """
    Returns the list of kanban tasks by specified project.

    Returns:
        dict: List of kanban tasks.
        str: Error message if the project is not found.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."
    
    # Get tasks
    return project['tasks']

def get_kanban_tasks_by_status(user_settings, project_title: str, status: str):
    """
    Returns a list of kanban tasks by a specified project. Where
    the list will reference only items that have their status equal to
    the status argument.

    Returns:
        list: List of kanban tasks that are in the specified status.
        str: Error message if the project is not found.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."
    
    # Filter tasks with status 'status'
    status_tasks = [task for task in project["tasks"] if task["status"] == status]
    return status_tasks

def get_backlog_task_ids(user_settings, project_title: str):
    """
    Returns a list of task IDs for tasks in the backlog by specified project.

    Returns:
        list: List of task IDs.
        str: Error message if the project is not found.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."
    
    # Extract IDs of tasks with status 'backlog'
    backlog_ids = [task["id"] for task in project["tasks"] if task["status"] == "backlog"]
    return backlog_ids

def delete_kanban_item_by_id(user_settings, project_title: str, item_id: int):
    """
    Deletes the respective kanban item from the specified project.

    Returns:
        str: error message if something went wrong
        None: on successful delete
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."
    
    # Ensure that the task exists in the project
    task = next((t for t in project["tasks"] if t["id"] == item_id), None)
    if not task:
        return f"Task with id {item_id} not found."

    # Find and delete the task
    for index, task in enumerate(project['tasks']):
        if item_id == task['id']:
            del project['tasks'][index]
    
    # Persist changes to the settings model on disk
    update_settings(user_settings)

def add_kanban_task(user_settings, project_title: str, kanban_task):
    """
    Adds the kanban task to the user settings.
    Assigns a unique ID based on project["nextTaskId"].
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."
    
    # Assign a unique ID to the new task
    kanban_task["id"] = project.get("nextTaskId", 0)
    project["nextTaskId"] = kanban_task["id"] + 1

    # Add task to the project
    project["tasks"].append(kanban_task)

    # Persist changes to disk or wherever your update_settings function goes
    update_settings(user_settings)

def archive_completed_kanban_tasks(user_settings, project_title: str):
    """
    Used for the "complete" operation, this function deletes
    all of the tasks for the specified project where the 
    status attribute is 'done'.

    Returns:
        str: Error message if the project is not found.
        None: On successful deletion of tasks.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."

    # Filter out tasks that are not done
    for task in project["tasks"]:
        if task["status"] == "done":
            task["status"] = "archived"

    # Persist changes to disk or user settings
    update_settings(user_settings)

def get_next_task_id(user_settings, project_title: str):
    """
    Retrieves the next task id given the user_settings and
    project title as arguments.

    Returns:
        str: Error message if the project is not found.
        int: The next task ID.
    """
    # Get project
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return "Project not found."

    return project['nextTaskId']

def kanban_project_exists(user_settings, project_title: str):
    """
    Returns True if the Kanban project already exists within user settings.
    Returns False if the project does not exist.
    """
    project = next((p for p in user_settings["projects"] if p["title"] == project_title), None)
    if not project:
        return False
    
    return True

def get_project_ids(user_settings):
    """
    Returns a list of project ids as they appear in user settings.
    Used for determining the selected index.
    """
    return [project['id'] for project in user_settings['projects']]

def delete_project_by_title(user_settings, project_title: str):
    """
    Deletes a kanban project given its project_title.

    Returns False if unable to delete by the title, meaning it does not exist.
    Returns True if the operation was successful.
    """
    project_index = next((i for i, p in enumerate(user_settings["projects"]) if p["title"] == project_title), None)
    if project_index is None:
        return False

    # Delete the project
    del user_settings["projects"][project_index]
    update_settings(user_settings)
    return True