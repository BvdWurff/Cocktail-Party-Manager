# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import subprocess
import json

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.text import Text

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT, CONTINUE_PROMPT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


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

    file_path = os.path.join("data", data_type)

    with open(f"{file_path}.json", "r", encoding="utf-8") as file:
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

    file_path = os.path.join("data", data_type)

    with open(f"{file_path}.json", "w", encoding="utf-8") as file:
        json.dump(stored_data, file, indent=4, ensure_ascii=False)


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
            print_message(INVALID_INPUT, "red")
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


def get_input(message=CONTINUE_PROMPT, data_type=str, color="bright_white"):
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

        if data_type == float:
            str(value)
            value = value.replace(",",".")
            value = round(float(value), 1)

        try:
            if data_type != "enter":
                return data_type(value)

            else:
                return ""

        except (ValueError, TypeError):
            print_message(INVALID_INPUT, "red")




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

def display_table(name_column_1: str = "option", options_column_1="", name_column_2: str = "action", options_column_2="", width=64):
    """
    Creates a formatted Rich Table containing numbered menu options.

    Args:
        name_column_1 (int): Display name of column 1
        options_column_1 (list): Options to display in column 1
        name_column_2 (int): Display name of column 2
        options_column_2 (list): Options to display in column 2
        width (int): The width of the table.

    Returns:
        Table: The formatted Rich menu table.
    """
    table = Table(
        box=box.SQUARE,
        expand=True,
        header_style="bold bright_white",
        border_style="bright_yellow",
        padding=(0, 1),
        width=width
    )

    table.add_column(name_column_1, min_width=4)
    table.add_column(name_column_2)

    if not options_column_1:

        counter = 0

        for option in options_column_2:
            counter += 1

            if option  == "":
                counter = -1

            table.add_row(
                Text(f"{str(counter)}.") if option else Text(""),
                Text(str(option)),
            )

    else:
        for option_c1, option_c2 in zip(options_column_1, options_column_2):
            table.add_row(str(option_c1), option_c2)



    return table


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

def unit_converter():
    while True:
        content = "Convert different units of measurement to milliliters (ml)."

        display_page(location="Cocktail Party Manager",
                     title="Unit converter",
                     content=content
                     )

        print_message("Select the unit you would like to convert:\n")

        options_column_2 = ["oz (fl oz)", "cup", "liter (L)", "centiliter (cl)", "teaspoon (tsp)", "tablespoon (tbsp)", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))
        if menu_choice == 0:
            break

        factor = float(0)

        match menu_choice:
            case 1:
                factor = 29.5735
            case 2:
                factor = 236.5882
            case 3:
                factor = 1000
            case 4:
                factor = 10
            case 5:
                factor = 4.9289
            case 6:
                factor = 14.7868

        volume = float(get_input("What is the volume of the unit you want to convert? ", float))
        print()
        volume_ml = int(volume * factor)
        print_message(f"[purple]{volume} {options_column_2[menu_choice -1]}[/] is [blue]{volume_ml} ml[/]")
        print()
        get_input()
        continue

    return








