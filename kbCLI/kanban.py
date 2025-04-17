import shutil, os, textwrap, sys, ansi
import settings
import signal
import kbutils

def print_kanban_columns(
    todo,
    doing,
    done,
    project_title: str = "",
    *,
    min_col_width: int = 15,
    reserve_rows: int = 2,      # free rows for your prompt
    clear_screen: bool = True
):
    """
    Clear the screen and print a color‑coded, boxed Kanban board.

    • Lines  : red          (ansi.GREY)
    • Todo   : bright blue  (ansi.BRIGHT_BLUE)
    • Doing  : orange       (ansi.ORANGE)
    • Done   : green        (ansi.GREEN)
    """
    line_color = ansi.GREY

    # ── 0. Clear screen ────────────────────────────────────────────────────
    if clear_screen:
        os.system("cls" if os.name == "nt" else "clear")

    # ── 1. Terminal geometry ──────────────────────────────────────────────
    term_cols, term_rows = shutil.get_terminal_size(fallback=(80, 24))
    usable_cols = max(term_cols - 4, min_col_width * 3)           # 4 borders (┌││┐)
    base, extra = divmod(usable_cols, 3)
    col_widths = [max(min_col_width, base + (1 if i < extra else 0)) for i in range(3)]
    board_width = sum(col_widths) + 4                             # 3 inner + 2 outer bars

    # ── 2. Column metadata ────────────────────────────────────────────────
    cols = [
        ("Todo",  list(todo),  ansi.BRIGHT_BLUE),
        ("Doing", list(doing), ansi.ORANGE),
        ("Done",  list(done),  ansi.GREEN),
    ]

    def fmt(task):
        tid, tname = (task["id"], task["name"]) if isinstance(task, dict) else task
        return f"[{tid}] {tname}"

    # ── 3. Box‑drawing helpers (all red) -----------------------------------
    V = lambda ch="│": f"{line_color}{ch}{ansi.RESET}"
    H = lambda n:       f"{line_color}{'─'*n}{ansi.RESET}"
    def join_h(parts, mid):
        return f"{line_color}{mid}{ansi.RESET}".join(parts)

    # Top border: ┌──┬──┬──┐
    top_border = (
        V("┌") +
        join_h([H(w) for w in col_widths], "┬") +
        V("┐")
    )

    # Mid border (under header): ├──┼──┼──┤
    mid_border = (
        V("├") +
        join_h([H(w) for w in col_widths], "┼") +
        V("┤")
    )

    # Vertical separator used inside rows
    V_SEP = V("│")

    # ── 4. Collect all lines ------------------------------------------------
    lines = []

    # 4a. Project title + full‑width red rule
    if project_title:
        centered_title = project_title.center(board_width)
        lines.append(f"{ansi.RED}{ansi.BOLD}{centered_title}{ansi.RESET}")
        lines.append(top_border)
    else:
        # still draw top border even if no title
        lines.append(top_border)

    # 4b. Header row (column titles)
    header_cells = [
        f"{color}{title.center(w)}{ansi.RESET}"
        for (title, _tasks, color), w in zip(cols, col_widths)
    ]
    header_row = V_SEP + V_SEP.join(header_cells) + V_SEP
    lines.extend([header_row, mid_border])

    # 4c. Task rows (wrapped, color‑safe)
    wrapped_cols = []
    for (_title, tasks, _color), w in zip(cols, col_widths):
        cell_lines = []
        for t in tasks:
            cell_lines.extend(textwrap.wrap(fmt(t), width=w) or [""])
        wrapped_cols.append(cell_lines)

    max_rows = max(len(c) for c in wrapped_cols)
    for i in range(max_rows):
        row_cells = []
        for col_idx, (_title, _tasks, color) in enumerate(cols):
            raw = wrapped_cols[col_idx][i] if i < len(wrapped_cols[col_idx]) else ""
            raw = raw[:col_widths[col_idx]]
            padding = " " * (col_widths[col_idx] - len(raw))
            row_cells.append(f"{raw}{ansi.RESET}{padding}")
        lines.append(V_SEP + V_SEP.join(row_cells) + V_SEP)

    # 4d. Blank padding rows so borders reach bottom
    visible = len(lines)
    pad_needed = max(0, term_rows - reserve_rows - visible - 1)   # -1 for bottom border
    blank_cells = [" " * w for w in col_widths]
    empty_row = V_SEP + V_SEP.join(blank_cells) + V_SEP
    lines.extend([empty_row] * pad_needed)

    # 4e. Bottom border: └──┴──┴──┘
    bottom_border = (
        V("└") +
        join_h([H(w) for w in col_widths], "┴") +
        V("┘")
    )
    lines.append(bottom_border)

    # 5. Print in one shot
    sys.stdout.write("\n".join(lines))
    sys.stdout.flush()

def display_kanban(user_settings, project_title: str):
    """
    Displays the kanban board based on the input project_title
    """

    # Obtain task map
    task_map = settings.generate_task_map_for_project(user_settings, project_title)
    todo = task_map['todo']
    doing = task_map['doing']
    done = task_map['done']

    # Print kanban to screen
    print_kanban_columns(todo, doing, done, project_title)

def display_interactive_kanban(user_settings, project_title):
    displayable_error = ""
    mode = "CMD"
    input_text = ""

    while True:
        display_kanban(user_settings, project_title)
        
        kbutils.print_bottom_input_with_mode_and_error(input_text, mode, displayable_error)
        key = kbutils.get_keypress()

        # TODO once more modes are implemented, add checks, but for now it is just CMD
        """
        In CMD mode, the user can type the operations that they want to do:
        Example:    "move 0" will move task with index 0 over a column.
                    "move 0 doing" will move task with index 0 to the doing column.
                    "delete 0" will delete the task with index 0.
                    "0" will open the view interface for the task with index 0. (changes the view)
                    "edit 0" will open the edit interface for task with index 0. (changes the view)
                        - You can update different attributes of the task here.
                        - You can create subtasks for the task.
                    "create" will open the create task interface.
                    "backlog" will show a list of backlog items (those not in the view)
                    "complete" will delete all items that are in the done column.
        """
        if key == kbutils.EXIT_CMD:
            print(f"{ansi.RED}Exiting Kanban CLI...{ansi.RESET}")
            os.system('clear')
            sys.exit(0)
        elif key.isalnum() or key in (' ', '-', '_'):
            input_text += key
            displayable_error = ''
        elif key in kbutils.KEY_BACKSPACE:  # Backspace
            input_text = input_text[:-1]
            displayable_error = ''
        elif key in kbutils.KEY_ENTER:
            command_parts = input_text.strip().split()
            if not command_parts:
                return

            cmd = command_parts[0]
            args = command_parts[1:]

            if cmd == "move" or cmd == "mv":
                if len(args) < 1 or not args[0].isdigit():
                    displayable_error = "Usage: move <index> [column]"
                else:
                    task_index = int(args[0])
                    destination = args[1] if len(args) > 1 else None

                    error = settings.move_kanban_item_by_id(user_settings, project_title, task_index, destination)
                    if error:
                        displayable_error = error
            elif cmd == "delete" or cmd == "del" or cmd == "remove":
                if len(args) < 1 or not args[0].isdigit():
                    continue
                else:
                    task_index = int(args[0])
                    # TODO: call your delete_task(task_index) logic here
                    pass
            elif cmd == "edit":
                if len(args) < 1 or not args[0].isdigit():
                    continue
                else:
                    task_index = int(args[0])
                    # TODO: switch to edit view for task_index
                    pass
            elif cmd == "create" or cmd == "new":
                # TODO: open create task interface
                pass
            elif cmd == "backlog" or cmd == "bl":
                # TODO: show backlog
                pass
            elif cmd == "complete":
                # TODO: delete all items in the done column
                pass
            elif cmd == "home":
                # TODO: go back to the main menu
                pass
            elif cmd == "quit":
                # TODO: exit the program
                pass
            elif cmd.isdigit():
                # TODO: open view for this task
                task_index = int(cmd)
                pass

            # Reset input text
            input_text = ''

def handle_exit(signum, frame):
    """
    Handles exit signals (SIGINT, SIGHUP, SIGTERM) and ensures proper cleanup.
    """
    os.system("cls" if os.name == "nt" else "clear")
    sys.exit(0)

# Register signal handlers to handle_exit function
signal.signal(signal.SIGHUP, handle_exit)   # Handle terminal close (Unix)
signal.signal(signal.SIGTERM, handle_exit)  # Handle kill command
