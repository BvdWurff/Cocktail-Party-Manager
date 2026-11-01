from utils.utils import (
    load_data,
    save_data,
    display_page,
    display_table,
    get_input,
    get_menu_choice,
)

from utils.constants import PARAM_ITEM_DESCRIPTION


def check_cocktail_availability(cocktail_id):
    cocktails = load_data("cocktails")
    orders = load_data("orders")

    low_on_stock = []

    ingredients = cocktails[cocktail_id]["ingredients"]

    for ingredient in ingredients:
        inventory = load_data("inventory")
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
            add_item_to_inventory(ingredient)
            low_on_stock.append(ingredient)

    return low_on_stock


def add_item_to_inventory(ingredient):
    inventory = load_data("inventory")
    from modules.cocktail_api import get_ingredient_description

    if not any(item["name"] == ingredient for item in inventory.values()):

        description = get_ingredient_description(PARAM_ITEM_DESCRIPTION)

        item = {
            "id": str(len(inventory) + 1),
            "name": ingredient,
            "description": description,
            "quantity": 0,
            "minimum_quantity": 10
        }

        save_data("inventory", item)


def show_inventory():
    while True:

        inventory = load_data("inventory")

        content = f"An overview of the current inventory"

        display_page(location="Admin",
                     title="Inventory",
                     content=content
                     )

        item_ids = []

        columns = {
            "Name": [],
            "Quantity": [],
            "Minimum Quantity": []
        }

        for item_id, item in sorted(inventory.items(), key=lambda entry: entry[1]["name"].casefold()):
            item_ids.append(item_id)
            columns["Name"].append(item["name"])
            columns["Minimum Quantity"].append(item["minimum_quantity"])

            quantity = item["quantity"]
            minimum_quantity = item["minimum_quantity"]

            if quantity < minimum_quantity:
                columns["Quantity"].append(f"[red]{quantity}[/red]")
            else:
                columns["Quantity"].append(str(quantity))

        columns["Name"].extend(["", "Back to admin menu"])
        columns["Quantity"].extend(["", ""])
        columns["Minimum Quantity"].extend(["", ""])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

        if menu_choice == 0:
            break

        item_id = item_ids[menu_choice - 1]
        show_inventory_item(item_id)

    return


def show_inventory_item(item_id):
    inventory = load_data("inventory")
    item = inventory.get(item_id)

    content = f"Inventory details of [blue]{item["name"]}[/]."

    display_page(location="Inventory",
                 title=item["name"],
                 content=content
                 )

    get_input()



