# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import subprocess
import datetime
import json
import copy

from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box
from rich.text import Text

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT,
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
    with open(f"data/{data_type}.json", "r", encoding="utf-8") as file:
        return json.load(file)


def save_data(data_type, data):
    """
    Saves data to the specified JSON file.

    Args:
        data_type (str): The name of the JSON file that needs to be updated.
        data (dict): The dictionary with data that has to be saved
    """
    stored_data = load_data(data_type)

    record_id = data["id"]

    if record_id not in stored_data:
        stored_data[record_id] = {}

    for field in data:
        if field == "id":
            continue
        stored_data[record_id][field] = data[field]

    with open(f"data/{data_type}.json", "w", encoding="utf-8") as file:
        json.dump(stored_data, file, indent=4, ensure_ascii=False)

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
        try:
            menu_choice = int(get_input(f"{SELECT_OPTION}"))

        except ValueError:
            print_message(INVALID_INPUT, "red")
            continue

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


def get_input(message, color="bright_white"):
    """
    Requests user input using a formatted Rich prompt.

    Args:
        message (str): The message displayed to the user.
        color (str): The color of the input prompt.

    Returns:
        str: The user's input.
    """
    return console.input(f"{' ' * 5}[{color}]{message}[/]")


def display_panel(content, border_style="bright_yellow", title_color="bright_white", title=""):
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
                title=f"[bold {title_color}]{title}[/]",
                title_align="left",
                padding=(1, 2),
            ),
            (0, 5)
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

    counter = 0
    if not options_column_1:
        for option in options_column_2:
            counter += 1

            if option == "":
                counter = -1

            table.add_row(
                Text(f"{str(counter)}.") if option else Text(""),
            )
        else:
            table.add_row(
                Text(str(option)),
            )

    for option in options_column_2:
        table.add_row(
            Text(str(option)),
        )

    return table

def register_new_guest():
    guests = load_data("guests")

    first_name = get_input("What is the first name of the guest? ")
    surname = get_input("What is the surname of the guest? ")

    for guest in guests.values():
        if guest["first_name"].lower() == first_name.lower() and guest["surname"].lower() == surname.lower():
            print()
            print_message(f"A guest named {first_name} {surname} already exists.", "red")

            while True:
                print()
                confirmation_choice = get_input("Are you sure you want to create another guest? (Yes/No) ").lower()

                if confirmation_choice not in ("yes", "no"):
                    print_message(INVALID_INPUT, "red")
                    continue

                if confirmation_choice == "yes":
                    break

                else:
                    return None

    guest = {
        "id": str(len(guests) + 1),
        "first_name": first_name,
        "surname": surname,
        "active": True
    }

    save_data("guests", guest)

    return guest["id"]


def register_new_event():
    events = load_data("events")

    while True:
        name = get_input("What is the name of the event? (STOP to return) ")
        date = get_input("What is the date of the event? (dd/mm/yyyy or today) ").lower()

        if name.lower() == "stop":
            return None

        if date == "today":
            date = datetime.datetime.now()

        for event in events.values():
            if event["date"] == date:
                print()
                print_message(f"An event is already registered for {date}.", "red")
                print()
                continue
        break

    guests = load_data("guests")

    options_column_1 = []
    options_column_2 = []

    for guest in sorted(guests.keys()):
        options_column_1.append(str(guest))
        name = f"{guest["first_name"]} {guest["surname"]}"
        options_column_2.append(guest[""])

    console.print(
        Padding(display_table(name_column_1="ID", options_column_1=options_column_1, name_column_2= "Name", options_column_2=options_column_2, width = 70), (0, 0, 1, 5))
    )

    guests = []

    while True:
        guest = str(get_input("Type the ID of the guest you want to add to the event: (type 0 to continue) "))
        print()
        if guest == "0":
            continue
        else:
            guests.append(guest)

    event = {
        "id": str(len(events) + 1),
        "name": name,
        "date": date,
        "guests": guests
    }

    save_data("events", event)

    return event["id"]





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