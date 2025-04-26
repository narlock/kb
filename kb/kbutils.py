import shutil
import sys
import termios
import tty
import re
import os
import ansi

# Regex to remove ANSI escape sequences
ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')


STR_REGEX = r'^[A-Za-z0-9\s\-\_\.\$\{\}\!\@\#\%\^\&\*\(\)]+$'

# Keybindings
KEY_UP = "\x1b[A"
KEY_DOWN = "\x1b[B"
KEY_ENTER = ('\r', '\n')
KEY_BACKSPACE = ('\x08', '\x7f')
EXIT_CMD = "\x03"  # Ctrl+C

def strip_ansi(text):
    return ANSI_ESCAPE.sub('', text)

def print_centered(text):
    columns, rows = shutil.get_terminal_size()

    # Split into lines
    lines = text.splitlines()
    line_count = len(lines)

    # Calculate vertical padding
    y_padding = max(0, (rows // 2) - (line_count // 2))

    # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Print vertical padding
    print("\n" * y_padding, end="")

    # Print each line centered
    for line in lines:
        visible_line = strip_ansi(line)
        x_padding = max(0, (columns // 2) - (len(visible_line) // 2))
        print(" " * x_padding + line)

def print_bottom_input(input_text):
    # Get terminal size
    columns, height = shutil.get_terminal_size()

    # Move to the bottom row, column 1
    print(f"\033[{height};1H", end="")  # Position cursor
    print(f"{ansi.RESET}>> {input_text}{ansi.RESET}", end="", flush=True)

def print_bottom_input_with_error(input_text, error):
    # Get terminal size
    columns, height = shutil.get_terminal_size()

    # Add space to error if applicable
    if error:
        error = f"{error} "

    # Move to the bottom row, column 1
    print(f"\033[{height};1H", end="")  # Position cursor
    print(f"{ansi.RED}{error}{ansi.RESET}>> {input_text}{ansi.RESET}", end="", flush=True)


def print_bottom_input_with_mode_and_error(input_text, mode, error):
    # Get terminal size
    columns, height = shutil.get_terminal_size()

    # Add space to error if applicable
    if error:
        error = f"{error} "

    # Move to the bottom row, column 1
    print(f"\033[{height};1H", end="")  # Position cursor
    print(f"{ansi.RED}{error}{ansi.RESET}{mode} >> {input_text}{ansi.RESET}", end="", flush=True)

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