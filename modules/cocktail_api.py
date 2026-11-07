# ==============================
# LIBRARY IMPORTS
# ==============================

import logging
import requests

from urllib.parse import quote


# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.inventory import add_item_to_inventory

from utils.utils import (
    get_input,
    print_message,
    save_data,
)


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


# ==============================
# LOGGING
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# API REQUEST HANDLING
# ==============================

def trigger_api(url):
    """
    Sends an HTTP GET request to TheCocktailDB API.

    Validates the HTTP response and converts its JSON content into
    a Python object. Displays an error message if the request fails,
    times out, or returns an invalid response.

    Args:
        url (str): The complete API endpoint URL.

    Returns:
        dict, list, or None: The parsed JSON response, or None
            if an error occurs.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.json()

    except requests.exceptions.ConnectionError:
        logger.exception("Could not connect to TheCocktailDB.")
        print()
        print_message("Error: Cannot connect to TheCocktailDB.\n", "red")
        get_input()

    except requests.exceptions.Timeout:
        logger.warning("TheCocktailDB request timed out.", exc_info=True)
        print()
        print_message("Error: The request to TheCocktailDB timed out.\n", "red")
        get_input()

    except ValueError:
        logger.exception("TheCocktailDB returned an invalid JSON response.")
        print()
        print_message("Error: Invalid API response.\n", "red")
        get_input()

    except requests.exceptions.RequestException:
        logger.exception("TheCocktailDB request failed.")
        print()
        print_message("Error: TheCocktailDB request failed.\n", "red")
        get_input()

    return None


# ==============================
# COCKTAIL API SEARCH
# ==============================

def search_cocktails_in_db(params, search_type):
    """
    Searches TheCocktailDB for cocktails using a specified API endpoint.

    Returns matching cocktail names and IDs, or a single cocktail ID
    when performing a random cocktail search.

    Args:
        params (str): The API endpoint and query parameters.
        search_type (str): The search type, such as "name",
            "ingredient", or "lucky_shot".

    Returns:
        dict, str, or None: A dictionary mapping cocktail names to IDs,
            a single cocktail ID for a random search, or None if
            no matching cocktails are found.
    """
    url = URL + API_KEY + params
    data = trigger_api(url)

    # API request failed. Error has already been handled.
    if data is None:
        return None

    # API returned an unexpected response structure.
    if not isinstance(data, dict):
        logger.error("Unexpected response structure from TheCocktailDB.")
        print()
        print_message("Error: Invalid API response.\n", "red")
        get_input()
        return None

    # API request succeeded, but no cocktails were found.
    if not data.get("drinks"):
        print()
        print_message(f"No cocktails matching that {search_type} were found.\n", "red")
        get_input()
        return None

    cocktails = {}

    for drink in data["drinks"]:
        if search_type == "lucky_shot":
            return drink["idDrink"]

        elif "strDrink" in drink:
            cocktails[drink["strDrink"]] = drink["idDrink"]

    return cocktails


# ==============================
# INGREDIENT API LOOKUP
# ==============================

def get_ingredient(trigger, ingredient):
    """
    Retrieves ingredient information from TheCocktailDB.

    Supports ingredient searches by name or unique ingredient ID.
    Returns the ingredient's ID, name, and description.

    Args:
        trigger (str): The lookup method, either "name" or "id".
        ingredient (str): The ingredient name or ID to search for.

    Returns:
        tuple: The ingredient ID, name, and description, or
            (None, None, None) if the lookup fails.
    """
    if trigger == "name":
        param = PARAM_ITEM_BY_NAME
    elif trigger == "id":
        param = PARAM_ITEM_BY_ID
    else:
        return None, None, None

    url = URL + API_KEY + param + quote(ingredient, safe="")
    data = trigger_api(url)

    # API request failed. Error has already been handled.
    if data is None:
        return None, None, None

    # API returned an unexpected response structure.
    if not isinstance(data, dict):
        logger.error("Unexpected response structure from TheCocktailDB.")
        print()
        print_message("Error: Invalid API response.\n", "red")
        get_input()
        return None, None, None

    # API request succeeded, but no ingredient was found.
    if not data.get("ingredients"):
        print()
        print_message("The ingredient was not found.\n", "red")
        get_input()
        return None, None, None


    for ingredient in data["ingredients"]:
        ingredient_id = ingredient["idIngredient"]
        ingredient_name = ingredient["strIngredient"]
        ingredient_description = ingredient["strDescription"]

        return ingredient_id, ingredient_name, ingredient_description

    return None, None, None


# ==============================
# LOCAL COCKTAIL MANAGEMENT
# ==============================

def add_cocktail_to_local_db(cocktail_id):
    """
    Retrieves a cocktail from TheCocktailDB and saves it locally.

    Fetches the cocktail's details, preparation instructions, and
    ingredients. Each ingredient is resolved to its unique API ID
    and registered in the local inventory when necessary.

    The cocktail is saved only after all required ingredients
    have been successfully retrieved and processed.

    Args:
        cocktail_id (str): The unique cocktail ID from TheCocktailDB.

    Returns:
        bool: True if the cocktail is successfully saved,
            or False if retrieval or validation fails.
    """
    url = URL + API_KEY + PARAM_COCKTAIL_BY_ID + cocktail_id
    data = trigger_api(url)

    # API request failed. Error has already been handled.
    if data is None:
        return False

    # API returned an unexpected response structure.
    if not isinstance(data, dict):
        logger.error("Unexpected response structure from TheCocktailDB.")
        print()
        print_message("Error: Invalid API response.\n", "red")
        get_input()
        return False

    # API request succeeded, but no cocktail was found.
    if not data.get("drinks"):
        print()
        print_message("Cocktail was not found.\n", "red")
        get_input()
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
            print_message(f"Could not retrieve ingredient: {ingredient}. The cocktail was not saved.\n", "red")
            get_input()
            return False

        measure = drink.get(f"strMeasure{counter}")
        ingredients[ingredient_id] = measure

    # Ensure all ingredients are available in the local inventory.
    for ingredient_id in ingredients:
        if not add_item_to_inventory(ingredient_id):
            print_message("Could not update the inventory. The cocktail was not saved.\n", "red")
            get_input()
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