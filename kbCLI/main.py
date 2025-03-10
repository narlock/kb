'''
Kanban CLI - main.py
author: narlock

This is the main file for the Kanban CLI
'''

import ansi
import sys
import os
import json
import tty, termios  # For keypress detection on Unix

# Development information
DEV_NAME = "narlock"
GITHUB_LINK = "https://github.com/narlock"
REPO_LINK = "https://github.com/narlock/kbCLI"
TITLE = f"{ansi.ORANGE}{ansi.BOLD}Kanban CLI - By: {ansi.ansi_link(GITHUB_LINK, DEV_NAME)}{ansi.ORANGE}{ansi.BOLD}. ⭐️ on {ansi.ansi_link(REPO_LINK, "GitHub")}{ansi.ORANGE}!"
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

# Get list of board files
def get_boards():
    if not os.path.exists(BOARDS_DIR):
        os.makedirs(BOARDS_DIR)
    return sorted([f for f in os.listdir(BOARDS_DIR) if f.endswith(".kb")])

# Create a new board
def create_board(board_name):
    board_filename = f"{board_name}.kb"
    board_path = os.path.join(BOARDS_DIR, board_filename)
    if not os.path.exists(board_path):
        board_data = default_board_structure(board_name)
        with open(board_path, 'w') as f:
            json.dump(board_data, f, indent=4)
        print(f"{ansi.GREEN}Board '{board_name}' created successfully!{ansi.RESET}")
    else:
        print(f"{ansi.RED}Board '{board_name}' already exists!{ansi.RESET}")

# Get a single keypress
def get_keypress():
    """
    Reads a single keypress from the user without requiring Enter.
    
    This function temporarily sets the terminal to raw mode so that it
    can capture keypresses directly, including special keys like arrow keys.
    
    Steps:
    1. Get the file descriptor for standard input (`sys.stdin.fileno()`).
    2. Store the current terminal settings (`termios.tcgetattr`).
    3. Switch the terminal to raw mode (`tty.setraw`), allowing key-by-key input.
    4. Read a single character (`sys.stdin.read(1)`).
    5. If the first character is the escape character (`\x1b`), read two more characters
       to capture full arrow key sequences.
    6. Restore the terminal to its original settings (`termios.tcsetattr`).
    7. Return the captured key.
    
    Returns:
        str: The captured key sequence as a string.
    """
    try:
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        key = sys.stdin.read(1)
        if key == '\x1b':  # Handle escape sequence (arrow keys)
            key += sys.stdin.read(2)  # Read the next two characters
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

# Interactive menu with continuous loop
def interactive_menu():
    selected_index = 0
    new_board_name = ""
    
    while True:
        boards = get_boards()
        os.system('clear')
        height = len(boards[:10]) + 4  # Space for menu and instructions
        print(f"{TITLE}\n{CONTROLS}{ansi.RESET}\n")
        
        for i, board in enumerate(boards[:10]):
            display_name = board.replace(".kb", "")
            if i == selected_index:
                prefix = f"{ansi.GREEN}-> {ansi.UNDERLINE}{display_name}{ansi.RESET}"
            else:
                prefix = f"   {display_name}"
            print(prefix)
        
        # Move cursor to the bottom of the screen
        print(f"\033[{height}B", end="")  # Move cursor down
        print(f"\r{ansi.YELLOW}>> {new_board_name}{ansi.RESET}", end="", flush=True)
        
        key = get_keypress()
        
        if key == EXIT_CMD:  # Ctrl+Q to exit
            print(f"{ansi.RED}Exiting Kanban CLI...{ansi.RESET}")
            os.system('clear')
            sys.exit(0)
        elif key == KEY_UP:  # Up arrow
            selected_index = (selected_index - 1) % len(boards)
        elif key == KEY_DOWN:  # Down arrow
            selected_index = (selected_index + 1) % len(boards)
        elif key in KEY_ENTER:  # Enter key
            if new_board_name:
                create_board(new_board_name)
                new_board_name = ""
            else:
                print(f"{ansi.GREEN}Opening board: {boards[selected_index]}{ansi.RESET}")
        elif key.isdigit() and 0 <= int(key) < min(10, len(boards)):
            print(f"{ansi.GREEN}Opening board: {boards[int(key)]}{ansi.RESET}")
        elif key.isalnum() or key in (' ', '-', '_'):
            new_board_name += key
        elif key in KEY_BACKSPACE:  # Backspace
            new_board_name = new_board_name[:-1]

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

    if not args:
        interactive_menu()
    elif args[0] == HELP_CMD:
        show_help()
    else:
        interactive_menu()

if __name__ == '__main__':
    main()