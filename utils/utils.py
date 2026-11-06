# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import subprocess
import json

from pathlib import Path

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich import box


# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT,
    CONTINUE_PROMPT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ==============================
# LOAD DATA
# ==============================

def load_data(data_type):
    """
    Loads stored data from the specified JSON file.

    Args:
        data_type (str): The name of the JSON file thas needs to be loaded.

    Returns:
        dict: The stored data of the specified JSON file.
    """

    file_path = DATA_DIR / f"{data_type}.json"

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data_type, data, record_id=""):
    """
    Saves data to the specified JSON file.

    Args:
        data_type (str): The name of the JSON file that needs to be updated.
        data (dict): The dictionary with data that has to be saved
        record_id (str): Value to identify the record that has to be updated
    """
    stored_data = load_data(data_type)

    if not record_id:
        record_id = data["id"]

    if record_id not in stored_data:
        stored_data[record_id] = {}

    for field in data:
        if field == "id":
            continue
        stored_data[record_id][field] = data[field]

    file_path = DATA_DIR / f"{data_type}.json"
    temporary_path = DATA_DIR / f"{data_type}.json.tmp"

    try:
        with open(temporary_path, "w", encoding="utf-8") as file:
            json.dump(stored_data, file, indent=4, ensure_ascii=False)

        os.replace(temporary_path, file_path)

    finally:
        temporary_path.unlink(missing_ok=True)


def update_record(data_type, record_id, key, new_value):
    data = load_data(data_type)
    record = data[record_id]
    record[key] = new_value

    save_data(data_type, record, record_id)

    return

# ==============================
# GENERAL UTILITIES
# ==============================


def clear_terminal():
    """
    Clears the terminal based on the operating system.
    """
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True, check=False)


def get_menu_choice(valid_choices):
    """
    Requests and validates a numeric menu choice.

    Args:
        valid_choices (range or collection): The allowed menu choices.

    Returns:
        int: The validated menu choice.
    """
    while True:
        menu_choice = get_input(f"{SELECT_OPTION}", data_type=int)


        if menu_choice not in valid_choices:
            print_message(INVALID_INPUT)
            continue

        print()
        return menu_choice


def print_message(message, color="", end="\n", indent=5):
    """
    Prints a formatted and indented message using Rich.

    Args:
        message (str): The message to display.
        color (str): The optional Rich style applied to the message.
        end (str): The string appended after the message.
        indent (int): The number of spaces used for left indentation.
    """

    console.print(
        f"{" " * indent}{message}",
        style=f"{color}",
        end=end
    )


def get_input(message=CONTINUE_PROMPT, data_type: type | str = str, color="bright_white"):
    """
    Requests user input using a formatted Rich prompt.

    Args:
        message (str): The message displayed to the user.
        color (str): The color of the input prompt.

    Returns:
        str: The user's input.
    """
    while True:
        value = console.input(f"{' ' * 5}[{color}]{message}[/]")

        try:
            if data_type == float:
                value = value.replace(",", ".")
                value = round(float(value), 1)
                
            if data_type != "enter":
                return data_type(value)

            else:
                return None

        except (ValueError, TypeError):
            print_message(INVALID_INPUT)


def display_panel(content, border_style="bright_yellow", title_color="bright_white", title="", top_padding=0):
    """
    Displays content in a formatted Rich Panel.

    Args:
        content (str or Rich renderable): The content to display.
        border_style (str): The color or style of the panel border.
        title_color (str): The color of the panel title.
        title (str): The optional panel title.
    """
    console.print(
        Padding(
            Panel(
                content,
                border_style=border_style,
                title=f"[bold {title_color}]{title}[/]" if title else None,
                title_align="left",
                padding=(1, 2),
                width=70,
            ),
            (top_padding, 0,0, 5)
        )
    )
    print()


def display_table(columns: dict, auto_number=False):
    """
    Creates and displays a formatted Rich Table with dynamically defined columns.

    Args:
        columns (dict): Dictionary containing column names and their values.
        auto_number (bool): Automatically generate a numbered option column.
    """
    table = Table(
        box=box.SQUARE,
        expand=True,
        header_style="bold bright_white",
        border_style="bright_yellow",
        padding=(0, 1),
        width=70
    )

    if auto_number:
        first_column = next(iter(columns.values()))

        option_numbers = []
        counter = 0

        for option in first_column:
            counter += 1

            if option == "":
                counter = -1

            option_numbers.append(f"{counter}." if option else "")

        columns = {"Option": option_numbers, **columns}

    for column_name in columns:
        table.add_column(column_name)

    for row in zip(*columns.values(), strict=True):
        table.add_row(*(str(value) for value in row))

    console.print(
        Padding(table, (0, 0, 1, 5))
    )


def display_page(location, title, content):
    """
    Clears the terminal and displays a formatted page in a Rich Panel.

    Args:
        location (str): The location displayed in the panel title.
        title (str): The title of the current page.
        content (str or Rich renderable): The content to display.
    """
    clear_terminal()

    console.print(
        Padding(
            Panel(
                content,
                title=f"[bold bright_yellow]{location}[/] [bold bright_white]- {title}[/]",
                title_align="left",
                border_style="bright_yellow",
                padding=(1, 2),
            ),
            (1, 5))
    )




def get_non_negative_integer(message):
    while True:
        value = int(get_input(message, int))

        if value >= 0:
            return value

        print_message(INVALID_INPUT, "red")

def confirm_action(action, record_type):
    while True:
        answer = get_input(f"Are you sure you want to {action} the {record_type}? (Yes/No) ").strip().casefold()

        if answer == "yes":
            return True
        elif answer == "no":
            return False
        else:
            print_message(INVALID_INPUT)





