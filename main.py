# ==============================
# LIBRARY IMPORTS
# ==============================

import logging

from pathlib import Path


# ==============================
# FUNCTION IMPORTS
# ==============================

from menus import main_menu

from modules.events import update_events

from utils.utils import (
    display_page,
    display_table,
    get_menu_choice,
    get_input,
    print_message,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import CONTINUE_PROMPT


# ==============================
# LOGGING
# ==============================

class SpacedFormatter(logging.Formatter):
    def format(self, record):
        return super().format(record) + "\n\n"

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

handler = logging.FileHandler(
    LOG_DIR / "cocktail_party_manager.log",
    encoding="utf-8"
)

handler.setFormatter(SpacedFormatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
))

logging.basicConfig(
    level=logging.WARNING,
    handlers=[handler]
)


# ==============================
# MAIN APPLICATION FLOW
# ==============================

def main():
    """
    Initializes the application, displays the welcome screen,
    and manages the main menu and exit confirmation.
    """
    update_events()

    content = """Welcome to [bright_yellow]the Cocktail Party Manager[/]!

For the best experience, it is recommended to run the program
in a [green]terminal[/] or to enable [green]Emulate terminal in output console[/]
in PyCharm."""


    display_page(location="Cocktail Party Manager",
                 title="Welcome",
                 content=content
                 )

    get_input(CONTINUE_PROMPT)

    while True:
        main_menu()

        content = "Are you sure you want to exit [bright_yellow]the Cocktail Party Manager[/]?"

        display_page(location="Cocktail Party Manager",
                     title="Exit Confirmation",
                     content=content
                     )

        columns = {
            "Action": ["Yes", "No"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

        if menu_choice == 2:
            continue

        else:
            content = "Thank you for using [bright_yellow]the Cocktail Party Manager[/].\n\n"
            content += "[blue]Until we drink again![/]"

            display_page(location="Cocktail Party Manager",
                         title="Exit",
                         content=content
                         )
            break


if __name__ == "__main__":
    try:
        main()

    except (OSError, ValueError, UnicodeError, TypeError):
        logging.exception("The application encountered a critical error.")

        print()
        print_message("A critical error occurred. Please check the application log.", "red")
        print()
        get_input("Press Enter to close the application.")
        print()
