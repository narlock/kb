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