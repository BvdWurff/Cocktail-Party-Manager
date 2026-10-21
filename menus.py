# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import requests
from dotenv import load_dotenv

from rich import box
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.console import Console

from orders import (
    new_order,
    prepare_order,
    cancel_order,
)

from persons import new_person
from events import new_event




from utils.utils import (
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    clear_terminal,
    display_page,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    CONTINUE_PROMPT,
)


# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)

def main_menu():
    while True:
        clear_terminal()
        content = f"""Welcome to the Cocktail Party Manager!

For the best experience, it is recommended to run the program 
in a [bright_white i]terminal[/] or to enable [bright_white i]Emulate terminal in output console[/] 
in PyCharm."""

        display_page(location="Cocktail Party Manager",
                     title="Main menu",
                     content=content
                     )

        menu_options = ["Cocktails", "Orders", "Events", "Admin", "Statistics", "", "Stop"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 6))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        elif menu_choice == 4:
            admin_menu()

        elif menu_choice == 5:
            stats_menu()

        else:
            break

    return

def cocktail_menu():
    while True:
        content = "Here you can find your favorite cocktails and get recipes."

        display_page(location="Cocktail Party Manager",
                     title="Cocktails",
                     content=content
                     )

        menu_options = ["Search by name", "Search by ingredient", "Lucky 'shot'", "Rank a cocktail", "All time favorites", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 6))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        elif menu_choice == 4:
            admin_menu()

        elif menu_choice == 5:
            stats_menu()

        else:
            break

    return


def orders_menu():
    while True:
        content = "Here you can manage your orders."

        display_page(location="Cocktail Party Manager",
                     title="Orders",
                     content=content
                     )

        menu_options = ["New order", "Prepare order", "Cancel order", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 4))

        if menu_choice == 1:
            new_order()

        elif menu_choice == 2:
            prepare_order()

        elif menu_choice == 3:
            cancel_order()

        else:
            break

    return

def events_menu():
    while True:
        content = "Here you can manage your events."

        display_page(location="Cocktail Party Manager",
                     title="Events",
                     content=content
                     )

        menu_options = ["New event", "Add guest", "Switch event", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 4))

        if menu_choice == 1:
            new_event()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        else:
            break

    return


def admin_menu():
    while True:
        content = "Here you can manage your settings and data."

        display_page(location="Cocktail Party Manager",
                     title="Admin",
                     content=content
                     )

        menu_options = ["Inventory", "Guests", "Events", "Cocktails", "Shopping lists", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 5))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            new_person(trigger="admin_menu")

        elif menu_choice == 3:
            events_menu()

        elif menu_choice == 4:
            admin_menu()

        elif menu_choice == 5:
            stats_menu()

        else:
            break

    return


def stats_menu():
    while True:
        content = "Here you can look into statistics"

        display_page(location="Cocktail Party Manager",
                     title="Statistics",
                     content=content
                     )

        menu_options = ["Guests", "Events", "Cocktails", "", "Back"]

        console.print(
            Padding(display_table(options_column_2=menu_options, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 5))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        else:
            break

    return
