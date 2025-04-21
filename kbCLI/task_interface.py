"""
task_interface.py
author: narlock

This file controls the interface related to tasks.
"""

import ansi
import os
import kbutils
import settings
import re

def display_task_change_interface(user_settings, task = None):
    """
    Displays the task interface. If a task is passed to this, the
    interface will display the edit interface. Otherwise, it will
    display the creation interface.
    """
    mode = "EDIT"
    task_id = -1

    if task is None:
        mode = "CREATE"
        task = settings.DEFAULT_TASK
        task_id = user_settings['nextId']
        task['id'] = task_id

    while True:
        os.system('clear')
        selected_index = 1

        print(f"{ansi.ORANGE}{ansi.BOLD}{mode} Task\n")

        # TODO display different things for special types:
        # linkedTasks: only display the ID of the task
        # checklistItems: only display the name of the item.
        for index, option in enumerate(task):
            if index == 0:
                # Don't display the ID as the user cannot change it
                continue
            if index == 1:
                print(f"{ansi.BRIGHT_GREEN}{ansi.BOLD}→ {settings.TASK_OPTIONS[index]}: {ansi.RESET}{task[option]}")
            else:
                # TODO uncomment this when everything is implemented
                print(f"{ansi.GREY}{settings.TASK_OPTIONS[index]}: {task[option]}{ansi.RESET}")
            # if index == selected_index:
            #     print(f"{ansi.BRIGHT_GREEN}{ansi.BOLD}→ {settings.TASK_OPTIONS[index]}: {ansi.RESET}{task[option]}")
            # else:
            #     print(f"{ansi.GREEN}{settings.TASK_OPTIONS[index]}: {ansi.RESET}{task[option]}")
        
        input_option = settings.TASK_OPTION_TYPES[selected_index]
        kbutils.print_bottom_input(f"({input_option}) ")
        key = kbutils.get_keypress()
        # TODO Make it so when the arrow keys are pressed, the selected index changes
        if key == kbutils.EXIT_CMD:
            # Return if we decide to exit
            return
        elif input_option == 'str':
            option_string = task[settings.TASK_OPTION_KEYS[selected_index]]
            if key in kbutils.KEY_BACKSPACE:
                # Delete character from string if possible
                option_string = option_string[:-1]
                task[settings.TASK_OPTION_KEYS[selected_index]] = option_string
            elif re.fullmatch(kbutils.STR_REGEX, key):
                # Add character from string
                option_string += key
                task[settings.TASK_OPTION_KEYS[selected_index]] = option_string


        # TODO For lists, we want to highlight the selected item in the list,
        # so that we can freely choose to remove or add wherever in the list
        # For the first version, we won't worry about this since we are only concerned
        # about the id and the title. 
