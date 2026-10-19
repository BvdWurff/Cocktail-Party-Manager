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
    register_new_guest,
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


def get_cocktails_by_name(api_key, url, cocktail):

    url = url + f"{api_key}/search.php?s={cocktail}"

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        print_message("Fout: kan geen verbinding maken met TheCocktailDB.", "red")
        return None

    except requests.exceptions.Timeout:
        print_message("Fout: TheCocktailDB reageert niet op tijd.", "red")
        return None

    if response.ok:
        data = response.json()

        cocktails = {}

        if data["drinks"]:
            for drink in data["drinks"]:
                if "strDrink" in drink:
                    cocktails[drink["strDrink"]] = drink["idDrink"]

        else:
            print_message(f"Fout: No cocktails with that name were found", "red")
            return None

        return cocktails

    else:
        print_message(f"Fout: {response.status_code} - {response.text}", "red")
        return None

def get_cocktail_by_id(api_key, url, cocktail_id):

    url = url + f"{api_key}/lookup.php?i={cocktail_id}"

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        print_message("Fout: kan geen verbinding maken met TheCocktailDB.", "red")
        return None, None

    except requests.exceptions.Timeout:
        print_message("Fout: TheCocktailDB reageert niet op tijd.", "red")
        return None, None

    instructions = ""
    ingredients = {}

    if response.ok:
        data = response.json()

        if data["drinks"]:
            for drink in data["drinks"]:
                if "strInstructions" in drink:
                    instructions = drink["strInstructions"]
                else:
                    instructions = "No instructions found"

                counter = 1
                while True:
                    ingredient = drink[f"strIngredient{counter}"]
                    if ingredient:
                        measure = drink[f"strMeasure{counter}"]
                        ingredients[ingredient] = measure
                        counter += 1

                    else:
                        break

        else:
            print_message(f"Fout: Cocktail not found", "red")
            return None, None

        return instructions, ingredients

    else:
        print_message(f"Fout: {response.status_code} - {response.text}", "red")
        return None, None


def get_order():
    guest = get_input("Who is the cocktail for? ").lower()
    cocktail = get_input("what cocktail do they want?  ").lower()



def main():
    """
        Controls the main program flow.
    """
    clear_terminal()

    load_dotenv()
    api_key = os.getenv("API_KEY")
    url = "https://www.thecocktaildb.com/api/json/v1/"

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

        location = "Cocktails"
        title = cocktail
        content = f"Ingredients and instructions for a [blue]{cocktail}[/]"

        display_page(location, title, content)

        table = Table(
            box=box.SQUARE,
            expand=True,
            header_style="bold bright_white",
            border_style="bright_yellow",
            padding=(0, 1),
            width=70
        )

        table.add_column("Number")
        table.add_column("Ingredient")
        table.add_column("Measure")

        counter = 1
        for ingredient, measure in ingredients.items():
            if measure is None:
                measure = ""

            table.add_row(
                Text(str(counter)),
                Text(ingredient),
                Text(measure),
            )
            counter += 1

        console.print(
            Padding(
                table,
                (0, 0, 1, 5),
            )
        )

        content = "- " + instructions.replace(". ", ".\n- ")

        display_panel(content, title="instructions")

        clear_terminal()

        register_new_guest()


if __name__ == "__main__":
    main()