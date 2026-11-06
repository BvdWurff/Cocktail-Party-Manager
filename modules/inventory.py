# ==============================
# LIBRARY IMPORTS
# ==============================

import logging


# ==============================
# FUNCTION IMPORTS
# ==============================

from utils.utils import (
    display_page,
    display_panel,
    display_table,
    get_input,
    get_menu_choice,
    get_non_negative_integer,
    load_data,
    print_message,
    save_data,
    update_record,
)


# ==============================
# LOGGING
# ==============================

logger = logging.getLogger(__name__)


# ==============================
# INVENTORY MANAGEMENT
# ==============================

def add_item_to_inventory(ingredient_id):
    """
    Adds an ingredient from TheCocktailDB to the local inventory.

    Retrieves ingredient details from the API and creates a new inventory
    record with zero stock, a default minimum quantity of 10 units,
    and an inactive shopping list flag.

    Args:
        ingredient_id (str): The unique ingredient ID from TheCocktailDB.

    Returns:
        bool: True if the ingredient already exists or is successfully
            added, or False if the ingredient details cannot be retrieved.
    """
    inventory = load_data("inventory")
    from modules.cocktail_api import get_ingredient

    # Skip creation if the ingredient is already registered.
    if ingredient_id in inventory:
        return True

    # Retrieve ingredient details from TheCocktailDB.
    item_id, item_name, item_description = get_ingredient("id", ingredient_id)

    if not item_id or not item_name:
        logger.warning("Ingredient %s could not be retrieved or added to inventory.", ingredient_id)
        return False

    item = {
        "id": item_id,
        "name": item_name,
        "description": item_description,
        "quantity": 0,
        "minimum_quantity": 10,
        "shopping_list": False
    }

    save_data("inventory", item)

    return True


# ==============================
# COCKTAIL AVAILABILITY
# ==============================

def check_cocktail_availability(cocktail_id, for_existing_order=False):
    """
    Checks whether the required ingredients are available for a cocktail.

    Each ingredient requires one inventory unit. When checking a new
    order, units reserved by existing open orders are deducted from
    the available stock.

    Args:
        cocktail_id (str): The ID of the cocktail to check.
        for_existing_order (bool): Whether the check is performed for
            an existing order rather than a new one.

    Returns:
        list: Ingredient IDs with insufficient or missing inventory.
            An empty list indicates that all ingredients are available.
    """
    cocktails = load_data("cocktails")
    orders = load_data("orders")
    inventory = load_data("inventory")

    low_on_stock = []
    ingredients = cocktails[cocktail_id]["ingredients"]

    for ingredient_id in ingredients:

        # Check whether the ingredient is available.
        if ingredient_id not in inventory:
            low_on_stock.append(ingredient_id)
            continue

        quantity = inventory[ingredient_id]["quantity"]

        # Subtract quantities reserved by open orders.
        for order in orders.values():
            if not for_existing_order and order["status"] == "ordered":
                ordered_cocktail_id = str(order["cocktail"])
                cocktail_ingredients = cocktails[ordered_cocktail_id]["ingredients"]

                if ingredient_id in cocktail_ingredients:
                    quantity -= 1

        if quantity <= 0:
            low_on_stock.append(ingredient_id)

    return low_on_stock


# ==============================
# INVENTORY DISPLAY
# ==============================

def show_inventory(trigger=None):
    """
    Displays an inventory overview based on the selected filter.

    Supports the full inventory, ingredients below their minimum
    quantity, and ingredients included in the shopping list.
    Users can select an ingredient to view or update its details.

    Args:
        trigger (str, optional): Determines which inventory overview
            to display: "full_inventory", "below_min_quantity",
            or "shopping_list".

    Returns:
        None: Returns when the user leaves the inventory overview.
    """
    while True:
        inventory = load_data("inventory")

        if trigger == "full_inventory":
            content = "An overview of all ingredients in your inventory."
            title = "Inventory Overview"

        elif trigger == "below_min_quantity":
            content = "An overview of ingredients with quantities below their minimum stock levels."
            title = "Below Minimum Quantity"

        elif trigger == "shopping_list":
            content = "An overview of the ingredients on your shopping list."
            title = "Shopping List"

        else:
            break

        display_page(location="Inventory",
                     title=title,
                     content=content
                     )

        item_ids = []

        columns = {
            "Name": [],
            "Quantity": [],
            "Shopping list": []
        }

        for item_id, item in sorted(inventory.items(), key=lambda entry: entry[1]["name"].casefold()):
            quantity = item["quantity"]
            minimum_quantity = item["minimum_quantity"]
            shopping_list = item["shopping_list"]

            if trigger == "below_min_quantity" and quantity >= minimum_quantity:
                continue

            if trigger == "shopping_list" and not shopping_list:
                continue

            item_ids.append(item_id)

            columns["Name"].append(item["name"])
            columns["Quantity"].append(format_stock_quantity(quantity, minimum_quantity))
            columns["Shopping list"].append("Yes" if shopping_list else "No")

        if not item_ids:
            print_message("No items found.", "red")
            print()
            get_input("Press [blue]Enter[/] to return to the inventory menu.")
            break

        columns["Name"].extend(["", "Back"])
        columns["Quantity"].extend(["", ""])
        columns["Shopping list"].extend(["", ""])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

        if menu_choice == 0:
            break

        item_id = item_ids[menu_choice - 1]
        show_inventory_item(item_id)

    return


def show_inventory_item(item_id):
    """
    Displays detailed information for an inventory ingredient.

    Shows the current quantity, minimum quantity, shopping list
    status, ingredient description, and cocktails using the ingredient.

    Allows the user to update quantities or toggle shopping list status.

    Args:
        item_id (str): The ID of the ingredient to display.

    Returns:
        None: Returns when the user leaves the ingredient details.
    """
    while True:
        inventory = load_data("inventory")
        cocktails = load_data("cocktails")
        item = inventory[item_id]
        shopping_list = item["shopping_list"]

        quantity = format_stock_quantity(item["quantity"], item["minimum_quantity"])

        if shopping_list:
            add_to_shopping_list = "Yes"
        else:
            add_to_shopping_list = "No"

        content = f"""These are the inventory details for the ingredient [blue]{item["name"]}[/]:\n
Quantity:                 {quantity}
Minimum Quantity:         {item["minimum_quantity"]}
Added to shopping list:   {add_to_shopping_list}"""

        display_page(location="Inventory",
                     title=item["name"],
                     content=content
                     )

        if item["description"]:
            panel_content = item["description"]

        else:
            panel_content = "[red]No description available for this ingredient.[/]"

        display_panel(panel_content, title="Description")

        columns = {
            "Cocktail": [],
        }

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda entry: entry[1]["name"].casefold()):
            if cocktail["active"] and item_id in cocktail["ingredients"]:
                columns["Cocktail"].append(cocktail["name"])

        display_table(columns)

        columns = {
            "Action": ["Update quantity", "Update minimum quantity"]
        }

        if shopping_list:
            columns["Action"].extend(["Remove from shopping list"])
            action = "removed from"

        else:
            columns["Action"].extend(["Add to shopping list"])
            action = "added to"

        columns["Action"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            quantity = get_non_negative_integer("What is the new quantity? ")

            print()
            update_record("inventory", item_id, "quantity", quantity)
            continue

        elif menu_choice == 2:
            minimum_quantity = get_non_negative_integer("What is the new minimum quantity? ")

            print()
            update_record("inventory", item_id, "minimum_quantity", minimum_quantity)
            continue

        elif menu_choice == 3:
            update_record("inventory", item_id, "shopping_list", not shopping_list)
            get_input(f"Ingredient successfully {action} the shopping list.", color="green")
            continue

        break

    return


# ==============================
# INVENTORY FORMATTING
# ==============================

def format_stock_quantity(quantity, minimum_quantity):
    """
    Formats an inventory quantity using Rich color markup.

    Quantities are displayed in red when empty, orange when below
    the minimum quantity, and green when sufficient.

    Args:
        quantity (int): The available inventory quantity.
        minimum_quantity (int): The configured minimum stock level.

    Returns:
        str: The quantity formatted with Rich color markup.
    """
    if quantity == 0:
        color = "red"
    elif quantity < minimum_quantity:
        color = "orange1"
    else:
        color = "green"

    return f"[{color}]{quantity}[/]"


# ==============================
# SHOPPING LIST MANAGEMENT
# ==============================

def add_low_stock_items_to_shopping_list():
    """
    Adds all ingredients below their minimum stock level to the shopping list.

    Only ingredients not already included are updated. A confirmation
    message is displayed indicating whether any ingredients were added.

    Returns:
        None: Returns after the shopping list has been updated.
    """
    inventory = load_data("inventory")

    counter = 0

    for item_id, item in inventory.items():
        if item["quantity"] < item["minimum_quantity"] and not item["shopping_list"]:
            update_record("inventory", item_id, "shopping_list", True)
            counter += 1

    if counter == 0:
        print_message("All low-stock ingredients are already on the shopping list.", "red")

    else:
        print_message("Low-stock ingredients successfully added to the shopping list.", "green")

    print()
    get_input()

    return