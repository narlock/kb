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

# Development information
DEV_NAME = "narlock"
GITHUB_LINK = "https://github.com/narlock"
REPO_LINK = "https://github.com/narlock/kbCLI"
TITLE = f"{ansi.ORANGE}{ansi.BOLD}Kanban CLI"
CONTROLS = f"{ansi.BLUE}←↑↓→ Navigate, ENTER to Confirm, Type for New Board, Ctrl+C to Exit"

# Command information
HELP_CMD = "-help"
EXIT_CMD = "\x03"  # Ctrl+Q

# Board data storage location
BOARDS_DIR = os.path.expanduser("~/Documents/narlock/kbCLI")

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
def interactive_menu():
    selected_index = 0
    input_text = ""
    
    colored_message = (
        f"{ansi.ORANGE}kb - Kanban Command Line Tool{ansi.RESET}\n\n"
        "version 0.0.1\n"
        "by narlock\n"
    )

    while True:
        os.system('clear')
        kbutils.print_centered(colored_message)
        
        # for i, board in enumerate(boards):
        #     display_name = board.replace(".kb", "")
        #     if i == selected_index:
        #         prefix = f"{ansi.GREEN}-> {ansi.UNDERLINE}{display_name}{ansi.RESET}"
        #     else:
        #         prefix = f"   {display_name}"
        #     print(prefix)
        
        # Move cursor to the bottom of the screen
        kbutils.print_bottom_input(input_text)
        
        key = kbutils.get_keypress()
        
        if key == EXIT_CMD:  # Ctrl+Q to exit
            print(f"{ansi.RED}Exiting Kanban CLI...{ansi.RESET}")
            os.system('clear')
            sys.exit(0)
        # elif key == KEY_UP:  # Up arrow
        #     selected_index = (selected_index - 1) % len(boards)
        # elif key == KEY_DOWN:  # Down arrow
        #     selected_index = (selected_index + 1) % len(boards)
        # elif key in KEY_ENTER:  # Enter key
        #     if input_text:
        #         create_board(input_text)
        #         input_text = ""
        #     else:
        #         print(f"{ansi.GREEN}Opening board: {boards[selected_index]}{ansi.RESET}")
        # elif key.isdigit() and 0 <= int(key) < min(10, len(boards)):
        #     print(f"{ansi.GREEN}Opening board: {boards[int(key)]}{ansi.RESET}")
        elif key.isalnum() or key in (' ', '-', '_'):
            input_text += key
        elif key in KEY_BACKSPACE:  # Backspace
            input_text = input_text[:-1]

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
        interactive_menu()
    elif args[0] == HELP_CMD:
        show_help()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()