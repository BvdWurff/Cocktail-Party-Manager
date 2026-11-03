import requests

from utils.utils import (
    get_input,
    save_data,
)

from modules.inventory import add_item_to_inventory

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    API_KEY,
    URL,
    PARAM_ITEM_BY_ID,
    PARAM_ITEM_BY_NAME,
)


def add_cocktail_to_local_db(cocktail_id):
    url = URL + f"{API_KEY}/lookup.php?i={cocktail_id}"

    data = trigger_api(url)

    if not isinstance(data, dict) or not data.get("drinks"):
        print()
        get_input(f"Cocktail was not found.", color="red")
        return

    else:
        cocktail_name = ""
        instructions = ""
        ingredients = {}


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
                    ingredient_id, _, _ = get_ingredient("name", ingredient)
                    measure = drink[f"strMeasure{counter}"]
                    ingredients[ingredient_id] = measure
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

    return



def search_cocktails_in_db(params, search_type):
    url = URL + API_KEY + params

    data = trigger_api(url)

    if not isinstance(data, dict) or not data.get("drinks"):
        print()
        get_input(f"No cocktails with that {search_type} were found.", color="red")

        return None

    else:
        cocktails = {}

        for drink in data["drinks"]:
            if search_type == "lucky_shot":
                return drink["idDrink"]

            elif "strDrink" in drink:
                cocktails[drink["strDrink"]] = drink["idDrink"]

        return cocktails


def get_ingredient(trigger, ingredient):
    if trigger == "name":
        param = PARAM_ITEM_BY_NAME
    elif trigger == "id":
        param = PARAM_ITEM_BY_ID
    else:
        return None, None, None

    url = URL + API_KEY + param + ingredient

    data = trigger_api(url)

    if not isinstance(data, dict) or not data.get("ingredients"):
        print()
        get_input(f"The ingredient was not found.", color="red")

        return None, None, None

    else:
        for ingredient in data["ingredients"]:
            ingredient_id = ingredient["idIngredient"]
            ingredient_name = ingredient["strIngredient"]
            ingredient_description = ingredient["strDescription"]

            return ingredient_id, ingredient_name, ingredient_description

        return None, None, None


def trigger_api(url):
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
        return data

    else:
        get_input(f"Error: {response.status_code} - {response.text}", "red")
        return None

