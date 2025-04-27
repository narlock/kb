'''
Kanban CLI - main.py
author: narlock

This is the main file for the Kanban CLI
'''

import kbutils
import ansi
import sys
import os
import json
import tty, termios  # For keypress detection on Unix
import settings
import time
import kanban

# Development information
DEV_NAME = "narlock"
GITHUB_LINK = "https://github.com/narlock"
REPO_LINK = "https://github.com/narlock/kb"
TITLE = f"{ansi.ORANGE}{ansi.BOLD}Kanban CLI"
CONTROLS = f"{ansi.BLUE}←↑↓→ Navigate, ENTER to Confirm, Type for New Board, Ctrl+C to Exit"

# Command information
HELP_CMD = "-help"
EXIT_CMD = "\x03"  # Ctrl+Q

# Board data storage location
BOARDS_DIR = os.path.expanduser("~/Documents/narlock/kb")

# Keybindings
KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"
KEY_ENTER = ('\r', '\n')
KEY_BACKSPACE = ('\x08', '\x7f')

# Default board structure
def default_board_structure(name):
    return {
        "board": {
            "name": name,
            "columns": ["todo", "doing", "done"],
            "column_colors": ["WHITE", "CYAN", "GREEN"]
        },
        "items": []
    }

# Interactive menu with continuous loop
def interactive_menu(user_settings):
    selected_index = 0
    input_text = ""
    displayable_error = ""

    while True:
        os.system('clear')
        colored_message = get_title_text(user_settings, selected_index)

        # Print centered
        lines = []
        lines.append(colored_message)
        kbutils.print_centered("\n".join(lines))

        
        # Move cursor to the bottom of the screen
        kbutils.print_bottom_input_with_error(input_text, displayable_error)
        
        key = kbutils.get_keypress()
        
        if key == EXIT_CMD:  # Ctrl+C to exit
            print(f"{ansi.RED}Exiting Kanban CLI...{ansi.RESET}")
            os.system('clear')
            sys.exit(0)
        elif key == KEY_UP:  # Up arrow
            selected_index = (selected_index - 1) % 5
            displayable_error = ""
        elif key == KEY_DOWN:  # Down arrow
            selected_index = (selected_index + 1) % 5
            displayable_error = ""
        elif key in KEY_ENTER:  # Enter key
            if selected_index == 0:
                if user_settings['recentProjectTitle'] is None:
                    # Open the project interactive interface
                    display_project_interactive_menu(user_settings)
                else:
                    kanban.display_interactive_kanban(user_settings, user_settings['recentProjectTitle'])
                    return
            elif selected_index == 1:
                display_project_interactive_menu(user_settings)
            elif selected_index == 2:
                """
                Creating a kanban project is intuitive... Simply just type
                the name of the project you want to create, then go under
                this option on the main menu. It will create a new project
                where the input_text is the project.
                """
                # Strip the text to get rid of unneeded whitespace
                input_text = input_text.strip()

                # Ensure that input_text is not blank
                if not input_text:
                    displayable_error = "Please enter a Kanban title for creation!"
                    continue
                
                # Ensure that the input_text is a unique Kanban title - it doesn't already exist
                if settings.kanban_project_exists(user_settings, input_text):
                    displayable_error = "Project already exists!"
                    continue

                # Create new project with the project title and save
                project = {
                    "id": user_settings['nextProjectId'],
                    "title": input_text,
                    "nextTaskId": 0,
                    "tasks": []
                }
                user_settings['nextProjectId'] = user_settings['nextProjectId'] + 1
                user_settings['projects'].append(project)
                user_settings['recentProjectTitle'] = project['title']
                settings.update_settings(user_settings)
                kanban.display_interactive_kanban(user_settings, user_settings['recentProjectTitle'])
                return
            elif selected_index == 4:
                os.system('clear')
                sys.exit(0)
        elif key.isalnum() or key in (' ', '-', '_'):
            input_text += key
            displayable_error = ""
        elif key in KEY_BACKSPACE:  # Backspace
            input_text = input_text[:-1]
            displayable_error = ""

def get_title_text(user_settings, selected_index: int) -> str:
    """Return the banner + menu, with the selected line in bright-green bold."""
    
    # Static banner
    lines = [
        f"{ansi.ORANGE}kb - Kanban Command Line Tool{ansi.RESET}",
        "",
        "version 0.0.1",
        "by narlock",
        "",
        "",
    ]

    # Menu definitions (index order matters)
    menu_items = [
        f"Open recent project: {ansi.RESET}{user_settings['recentProjectTitle']}",
        "Open existing project",
        "Create new project",
        "Open Settings",
        "Quit kb",
    ]

    # Build menu with conditional styling
    for i, item in enumerate(menu_items):
        if i == selected_index:
            # highlighted (bright green + bold)
            lines.append(f"{ansi.BRIGHT_GREEN}{ansi.BOLD}→ {item}{ansi.RESET}")
        else:
            # normal (plain green)
            lines.append(f"{ansi.GREEN}{item}{ansi.RESET}")

    return "\n".join(lines)

def display_project_interactive_menu(user_settings):
    """
    Displays the project selection interface and allows the user
    to choose which project they want to open.

    When a user selects a project, the recentProjectTitle will be
    updated based on the project that is opened.
    """
    project_ids = settings.get_project_ids(user_settings)
    if len(project_ids) == 0:
        return

    input_message = ""
    selected_index = 0
    current_project_title = ""

    while True:
        os.system('clear')
        print(f"{ansi.ORANGE}{ansi.BOLD}Projects\n")

        for project in user_settings['projects']:
            if project_ids[selected_index] == project['id']:
                print(f"{ansi.BRIGHT_GREEN}{ansi.BOLD}→ {project['title']}{ansi.RESET}")
                current_project_title = project['title']
            else:
                print(f"{ansi.GREEN}{project['title']}{ansi.RESET}")

        # Await user input
        kbutils.print_bottom_input(input_message)
        key = kbutils.get_keypress()

        if key == kbutils.EXIT_CMD:
            return
        elif key in kbutils.KEY_ENTER:
            if "Delete project" in input_message:
                # Delete the current project by current project title
                input_message = ""
                settings.delete_project_by_title(user_settings, current_project_title)

                # Ensure that deletion does not cause recentProject conflicts
                if user_settings['recentProjectTitle'] == current_project_title:
                    user_settings['recentProjectTitle'] = None
                    settings.update_settings(user_settings)

                # Update the current interface
                project_ids = settings.get_project_ids(user_settings)
                selected_index = 0

                # Exit if there are no projects
                if len(project_ids) == 0:
                    return
                
                continue
            else:
                # Open the kanban project
                user_settings['recentProjectTitle'] = current_project_title
                settings.update_settings(user_settings)
                kanban.display_interactive_kanban(user_settings, user_settings['recentProjectTitle'])
                return
        elif key == kbutils.KEY_DOWN:
            selected_index = (selected_index - 1) % len(project_ids)
            input_message = ""
        elif key == kbutils.KEY_UP:
            selected_index = (selected_index + 1) % len(project_ids)
            input_message = ""
        elif key in kbutils.KEY_BACKSPACE:
            input_message = f"{ansi.RED}Delete project {current_project_title}? {ansi.GREY}Press ENTER to confirm...{ansi.RESET}"

# Display help information
def show_help():
    """Displays the available commands."""
    print(f"{TITLE}{ansi.RESET}")
    print(f"Usage: kb [options]\n")
    print(f"Where options include:\n")
    print(f"\t-help         Show this help message")
    print(f"\t<board_name>  Open directly to a board view")
    print(f"\nNo arguments will open the main menu.\n")

# Main function
def main():
    args = sys.argv[1:]
    user_settings = settings.load_settings()

    if not args:
        interactive_menu(user_settings)
    elif args[0] == HELP_CMD:
        show_help()
    else:
        interactive_menu(user_settings)

if __name__ == '__main__':
    main()