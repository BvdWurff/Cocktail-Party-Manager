from rich import box
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.padding import Padding

from cocktail_api import (
    new_cocktail,
    get_cocktails_by_name,
)

from utils.utils import (
    load_data,
    save_data,
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    clear_terminal,
    display_page,
)

from utils.constants import (
    INVALID_INPUT,
    SELECT_OPTION,
    CONTINUE_PROMPT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


def check_cocktail_availability(cocktail_id):
    cocktails = load_data("cocktails")
    inventory = load_data("inventory")
    orders = load_data("orders")

    low_on_stock = []

    ingredients = cocktails[cocktail_id]["ingredients"]

    for ingredient in ingredients:
        found = False

        for item in inventory:
            if inventory[item]["name"] == ingredient:
                quantity = inventory[item]["quantity"]

                for order in orders:
                    if orders[order]["status"] == "ordered":
                        ordered_cocktail_id = str(orders[order]["cocktail"])
                        cocktail_ingredients = cocktails[ordered_cocktail_id]["ingredients"]

                        if ingredient in cocktail_ingredients:
                            quantity -= 1

                if quantity <= 0:
                    low_on_stock.append(ingredient)

                found = True
                break

        if not found:
            item = {
                "id": str(len(inventory) + 1),
                "name": ingredient,
                "quantity": 0,
                "minimum_quantity": 10
            }

            save_data("inventory", item)
            inventory[item["id"]] = item
            low_on_stock.append(ingredient)

    return low_on_stock

def update_inventory(item_id, key, new_value):
    inventory = load_data("inventory")
    item = inventory[item_id]
    item[key] = new_value

    save_data("inventory", item)



