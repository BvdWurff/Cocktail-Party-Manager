from utils.utils import (
    load_data,
    save_data,
    display_page,
    display_table,
    get_input,
    get_menu_choice,
    display_panel,
    update_record,
    print_message,
)

from utils.constants import INVALID_INPUT


def check_cocktail_availability(cocktail_id, for_existing_order=False):
    cocktails = load_data("cocktails")
    orders = load_data("orders")
    inventory = load_data("inventory")

    low_on_stock = []
    ingredients = cocktails[cocktail_id]["ingredients"]

    for ingredient_id in ingredients:

        # Add missing ingredients to the inventory.
        if ingredient_id not in inventory:
            if add_item_to_inventory(ingredient_id):
                inventory = load_data("inventory")

        # Check whether the ingredient is available.
        item = inventory.get(ingredient_id)

        if item is None:
            low_on_stock.append(ingredient_id)
            continue

        quantity = item["quantity"]

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


def add_item_to_inventory(ingredient_id):
    inventory = load_data("inventory")
    from modules.cocktail_api import get_ingredient

    # Ingredient already exists in the inventory.
    if ingredient_id in inventory:
        return True

    # Retrieve ingredient details from TheCocktailDB.
    item_id, item_name, item_description = get_ingredient("id", ingredient_id)

    if not item_id or not item_name:
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


def show_inventory(trigger=None):
    while True:
        inventory = load_data("inventory")

        if trigger == "full_inventory":
            content = "An overview of the full inventory."
            title = "Inventory overview"

        elif trigger == "below_min_quantity":
            content = "An overview of the items in the inventory below the minimum quantity."
            title = "Below minimum quantity"

        elif trigger == "shopping_list":
            content = "An overview of the items in the shopping list"
            title = "Shopping list"

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

            if quantity == 0:
                color = "red"
            elif quantity < minimum_quantity:
                color = "orange1"
            else:
                color = "green"

            columns["Name"].append(item["name"])
            columns["Quantity"].append(f"[{color}]{quantity}[/]")
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
    while True:
        inventory = load_data("inventory")
        cocktails = load_data("cocktails")
        item = inventory[item_id]
        shopping_list = item["shopping_list"]

        if item["quantity"] == 0:
            quantity = f"[red]{item["quantity"]}[/]"

        elif item["quantity"] < item["minimum_quantity"]:
            quantity = f"[orange1]{item["quantity"]}[/]"

        else:
            quantity = f"[green]{item["quantity"]}[/]"

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
            panel_content = "[red]No description available for this ingredient[/]"

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
            while True:
                quantity = int(get_input("What is the new quantity? ", int))

                if quantity >= 0:
                    break
                else:
                    print_message(INVALID_INPUT)
                    continue

            print()
            update_record("inventory", item_id, "quantity", quantity)
            continue

        elif menu_choice == 2:
            while True:
                min_quantity = int(get_input("What is the new minimum quantity? ", int))

                if min_quantity >= 0:
                    break
                else:
                    print_message(INVALID_INPUT)
                    continue

            print()
            update_record("inventory", item_id, "minimum_quantity", min_quantity)
            continue

        elif menu_choice == 3:
            update_record("inventory", item_id, "shopping_list", not shopping_list)
            get_input(f"Ingredient successfully {action} the shopping list.", color="green")
            continue

        break

    return



