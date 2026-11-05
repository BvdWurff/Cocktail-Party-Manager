import requests
from urllib.parse import quote

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
    PARAM_COCKTAIL_BY_ID,
)


def add_cocktail_to_local_db(cocktail_id):
    url = URL + API_KEY + PARAM_COCKTAIL_BY_ID + cocktail_id
    data = trigger_api(url)

    if not isinstance(data, dict) or not data.get("drinks"):
        print()
        get_input("Cocktail was not found.", color="red")
        return False

    drink = data["drinks"][0]

    cocktail_name = drink["strDrink"]
    instructions = drink.get("strInstructions") or "No instructions found."
    ingredients = {}

    # Retrieve and validate all ingredients.
    for counter in range(1, 16):
        ingredient = drink.get(f"strIngredient{counter}")

        if not ingredient:
            break

        ingredient_id, ingredient_name, _ = get_ingredient("name", ingredient)

        if not ingredient_id or not ingredient_name:
            get_input(f"Could not retrieve ingredient: {ingredient}. Cocktail was not saved.", color="red")
            return False

        measure = drink.get(f"strMeasure{counter}")
        ingredients[ingredient_id] = measure

    # Ensure all ingredients are available in the local inventory.
    for ingredient_id in ingredients:
        if not add_item_to_inventory(ingredient_id):
            get_input("Could not update the inventory. Cocktail was not saved.", color="red")
            return False

    # Save the cocktail only after all ingredients have been processed.
    cocktail = {
        "id": cocktail_id,
        "name": cocktail_name,
        "instructions": instructions,
        "ingredients": ingredients,
        "active": True
    }

    save_data("cocktails", cocktail)

    return True



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

    url = URL + API_KEY + param + quote(ingredient, safe="")

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
        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        get_input("Error: Cannot connect to TheCocktailDB.", color="red")

    except requests.exceptions.Timeout:
        get_input("Error: TheCocktailDB response timeout.", color="red")

    except ValueError:
        get_input("Error: Invalid API response.", color="red")

    except requests.exceptions.RequestException as error:
        get_input(f"API error: {error}", color="red")

    return None

