# ==============================
# LIBRARY IMPORTS
# ==============================

import json
import logging
import os
import subprocess

from pathlib import Path

from rich import box
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT,
    CONTINUE_PROMPT,
)


# ==============================
# LOGGING
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ==============================
# DATA MANAGEMENT
# ==============================

def load_data(data_type):
    """
    Loads data from the specified JSON file.

    Args:
        data_type (str): The name of the JSON file, without its extension.

    Returns:
        dict: The data loaded from the JSON file.
    """

    file_path = DATA_DIR / f"{data_type}.json"

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (OSError, ValueError, UnicodeError):
        logger.exception("Failed to load JSON file: %s", file_path)
        raise


def save_data(data_type, data, record_id=""):
    """
    Adds or updates a record in the specified JSON file.

    Existing fields are updated with the supplied values, while
    unspecified fields remain unchanged.

    Args:
        data_type (str): The name of the JSON file, without its extension.
        data (dict): The record data to be saved.
        record_id (str): Optional ID of the record to update. If omitted,
            the ID is retrieved from the supplied data.
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

    except (OSError, TypeError, ValueError):
        logger.exception("Failed to save JSON file: %s", file_path)
        raise

    finally:
        try:
            temporary_path.unlink(missing_ok=True)

        except OSError:
            logger.warning("Could not remove temporary file: %s", temporary_path, exc_info=True)


def update_record(data_type, record_id, key, new_value):
    """
    Updates a single field of an existing record.

    Args:
        data_type (str): The name of the JSON file, without its extension.
        record_id (str): The ID of the record to update.
        key (str): The field to update.
        new_value: The value to assign to the specified field.
    """
    data = load_data(data_type)
    record = data[record_id]
    record[key] = new_value

    save_data(data_type, record, record_id)

    return


# ==============================
# USER INPUT AND VALIDATION
# ==============================

def get_input(message=CONTINUE_PROMPT, data_type: type | str = str, color="bright_white"):
    """
    Requests user input using a formatted Rich prompt and converts
    the input to the specified data type.

    Args:
        message (str): The message displayed to the user.
        data_type (type or str): The expected input type, or "enter" to
            wait for user input without returning a value.
        color (str): The Rich color used for the input prompt.

    Returns:
        str, int, float, or None: The converted input value, or None
        when data_type is "enter".
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


def get_menu_choice(valid_choices):
    """
    Requests a numeric menu choice and validates it against
    the supplied collection of allowed choices.

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


def get_non_negative_integer(message):
    """
    Requests an integer from the user and ensures it is not negative.

    Args:
        message (str): The input prompt displayed to the user.

    Returns:
        int: The validated non-negative integer.
    """
    while True:
        value = int(get_input(message, int))

        if value >= 0:
            return value

        print_message(INVALID_INPUT, "red")


def confirm_action(action, record_type):
    """
    Requests confirmation before performing an action on a record.

    Args:
        action (str): The action described in the confirmation prompt.
        record_type (str): The type of record affected by the action.

    Returns:
        bool: True if the user confirms, or False if the user declines.
    """

    print_message(f"Are you sure you want to {action} the {record_type}?\n", "bright_white")

    columns = {
        "Action": ["Yes", "No"]
    }

    display_table(columns, auto_number=True)

    menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

    if menu_choice == 1:
        return True

    return False

# ==============================
# TERMINAL AND MESSAGE UTILITIES
# ==============================

def clear_terminal():
    """
    Clears the terminal using the command appropriate
    for the operating system.
    """
    command = "cls" if os.name == "nt" else "clear"
    subprocess.run(command, shell=True, check=False)


def print_message(message, color="", end="\n", indent=5):
    """
    Displays a formatted message with optional styling and indentation.

    Args:
        message (str): The message to display.
        color (str): The optional Rich style applied to the message.
        end (str): The string appended after the message.
        indent (int): The number of spaces used for left indentation.
    """

    console.print(
        f"{' ' * indent}{message}",
        style=f"{color}",
        end=end
    )


# ==============================
# DISPLAY UTILITIES
# ==============================

def display_page(location, title, content, color="bright_yellow"):
    """
    Clears the terminal and displays a formatted page using a Rich Panel.

    Args:
        location (str): The location displayed in the panel title.
        title (str): The title of the current page.
        content (str or Rich renderable): The content to display.
        color (Rich renderable): The color of the border.
    """
    clear_terminal()

    console.print(
        Padding(
            Panel(
                content,
                title=f"[bold bright_yellow]{location}[/] [bold bright_white]- {title}[/]",
                title_align="left",
                border_style=color,
                padding=(1, 2),
            ),
            (1, 5))
    )


def display_panel(content, border_style="bright_yellow", title_color="bright_white", title="", top_padding=0):
    """
    Displays content in a formatted Rich Panel with optional
    title, styling, and top padding.

    Args:
        content (str or Rich renderable): The content to display.
        border_style (str): The color or style of the panel border.
        title_color (str): The color of the panel title.
        title (str): The optional panel title.
        top_padding (int): The amount of padding above the panel.
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
            (top_padding, 0, 0, 5)
        )
    )
    print()


def display_table(columns: dict, auto_number=False):
    """
    Creates and displays a Rich Table using dynamically defined columns.

    Optionally generates numbered menu choices based on the values
    in the first supplied column.

    Args:
        columns (dict): Dictionary containing column names and their values.
        auto_number (bool): Whether to generate a numbered option column.
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