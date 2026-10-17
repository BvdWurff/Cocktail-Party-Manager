# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import subprocess
import time

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

def display_menu_table(menu_options, column_2="actie", width=64):
    """
    Creates a formatted Rich Table containing numbered menu options.

    Args:
        menu_options (list): The menu options to display.
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

    table.add_column("Option", min_width=4)
    table.add_column(column_2)

    counter = 0

    for menu_option in menu_options:
        counter += 1

        if menu_option == "":
            counter = -1

        table.add_row(
            Text(f"{str(counter)}.") if menu_option else Text(""),
            Text(str(menu_option)),
        )

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