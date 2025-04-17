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
    "projects": [
        {
            "id": 0,
            "title": "kb",
            "description": "This is the project description",
            "status": "todo",
            "tags": [ "tag1" ],
            "startDate": "2025-04-10",
            "completeDate": None,
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
