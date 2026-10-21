import requests

from utils.utils import (
    get_input,
    print_message,
    save_data, clear_terminal,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    API_KEY,
    URL,
)


def new_cocktail(cocktail_id, cocktail_name):

    url = URL + f"{API_KEY}/lookup.php?i={cocktail_id}"

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        get_input("Error: Cannot connect to TheCocktailDB.", "red")
        return

    except requests.exceptions.Timeout:
        get_input("Error: TheCocktailDB response timeout.", "red")
        return

    instructions = ""
    ingredients = {}

    if response.ok:
        data = response.json()

        if data["drinks"]:
            for drink in data["drinks"]:
                if "strInstructions" in drink:
                    instructions = drink["strInstructions"]
                else:
                    instructions = "No instructions found."

                counter = 1
                while True:
                    ingredient = drink[f"strIngredient{counter}"]
                    if ingredient:
                        measure = drink[f"strMeasure{counter}"]
                        ingredients[ingredient] = measure
                        counter += 1

                    else:
                        break

            cocktail = {
                "id": cocktail_id,
                "name": cocktail_name,
                "Instructions": instructions,
                "ingredients": ingredients,
                "active": True
            }

            save_data("cocktails", cocktail)


        else:
            get_input(f"Fout: Cocktail not found", "red")

    else:
        get_input(f"Fout: {response.status_code} - {response.text}", "red")

    return


def get_cocktails_by_name():
    clear_terminal()

    cocktail = get_input("Which cocktail would you like to search for? ").lower()

    url = URL + f"{API_KEY}/search.php?s={cocktail}"

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



