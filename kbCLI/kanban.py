import shutil, os, textwrap, sys, ansi

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

# demo
todo  = [(1, "Write spec"), (2, "Set up repo")]
doing = [(3, "Implement core logic with a really long description")]
done  = [(4, "Kick-off"), (5, "Brainstorm"), (6, "Sign-off")]

print_kanban_columns(todo, doing, done, project_title="My First Project")
input("\n>> ")  # room for input commands
