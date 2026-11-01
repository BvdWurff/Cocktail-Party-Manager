import requests

from utils.utils import (
    get_input,
    print_message,
    save_data,
)

from modules.inventory import add_item_to_inventory

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    API_KEY,
    URL,
)


def add_cocktail_to_local_db(cocktail_id):
    url = URL + f"{API_KEY}/lookup.php?i={cocktail_id}"

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        get_input("Error: Cannot connect to TheCocktailDB.", color="red")
        return

    except requests.exceptions.Timeout:
        get_input("Error: TheCocktailDB response timeout.", color="red")
        return

    cocktail_name = ""
    instructions = ""
    ingredients = {}

    if response.ok:
        data = response.json()

        if data["drinks"]:
            for drink in data["drinks"]:
                cocktail_name = drink["strDrink"]

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
                "instructions": instructions,
                "ingredients": ingredients,
                "active": True
            }

            save_data("cocktails", cocktail)

            for ingredient in ingredients.keys():
                add_item_to_inventory(ingredient)

        else:
            get_input(f"Error: Cocktail not found", color="red")

    else:
        get_input(f"Error: {response.status_code} - {response.text}", color="red")

    return


def search_cocktails_in_db(params, search_type):
    url = URL + API_KEY + params

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        get_input("Error: Cannot connect to TheCocktailDB.", color="red")
        return None

    except requests.exceptions.Timeout:
        get_input("Error: TheCocktailDB response timeout.", color="red")
        return None

    if response.ok:
        data = response.json()

        cocktails = {}

        if data["drinks"]:
            for drink in data["drinks"]:
                if search_type == "lucky_shot":
                    return drink["idDrink"]

                elif "strDrink" in drink:
                    cocktails[drink["strDrink"]] = drink["idDrink"]

            return cocktails

        else:
            print()
            get_input(f"No cocktails with that {search_type} were found.", color="red")
            print()
            return None

    else:
        get_input(f"Error: {response.status_code} - {response.text}", "red")
        return None


def get_ingredient_description(params):
    url = URL + API_KEY + params

    try:
        response = requests.get(url, timeout=10)

    except requests.exceptions.ConnectionError:
        get_input("Error: Cannot connect to TheCocktailDB.", color="red")
        return None

    except requests.exceptions.Timeout:
        get_input("Error: TheCocktailDB response timeout.", color="red")
        return None

    if response.ok:
        data = response.json()

        if data["ingredients"]:
            for ingredient in data["ingredients"]:
                description = ingredient["strDescription"]
                return description

        else:
            print()
            get_input(f"No description for this ingredient was found.", color="red")
            print()
            return None

    else:
        get_input(f"Error: {response.status_code} - {response.text}", "red")
        return None

