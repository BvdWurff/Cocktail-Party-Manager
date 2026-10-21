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


from utils.utils import (
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    clear_terminal,
    display_page,
)

from menus import main_menu

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



def main():
    """
        Controls the main program flow.
    """
    clear_terminal()

    load_dotenv()
    api_key = os.getenv("API_KEY")
    url = "https://www.thecocktaildb.com/api/json/v1/"



    main_menu()

    if not api_key:
        print_message("Fout: geen API Key gevonden", "red")
        print()
        get_input("Druk op Enter om terug te keren naar de lobby")

    print()
    cocktail = get_input("Which cocktail would you like to search for? ").lower()

    cocktails = get_cocktails_by_name(api_key, url, cocktail)

    if cocktails:

        print()
        print_message("The following cocktails were found:", "bright_white")

        options_column_1 = []
        options_column_2 = []

        for cocktail in sorted(cocktails.keys()):
            options_column_2.append(str(cocktail))

        console.print(
            Padding(display_table(name_column_1="Options", options_column_1=options_column_1, name_column_2= "Cocktails", options_column_2=options_column_2, width = 70), (0, 0, 1, 5))

        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) + 1)) - 1
        cocktail = options_column_2[menu_choice]
        cocktail_id = cocktails.get(cocktail)

        instructions, ingredients = get_cocktail_by_id(api_key, url, cocktail_id)
        get_input(CONTINUE_PROMPT)

        # ingredients = oz_to_ml(ingredients)



        clear_terminal()


if __name__ == "__main__":
    main()