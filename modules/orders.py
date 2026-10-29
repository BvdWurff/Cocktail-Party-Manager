# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.inventory import (
    check_cocktail_availability,
)

from modules.persons import select_guest
from modules.events import (
    get_current_event,
)

from modules.cocktails import (
    select_cocktail,
    show_cocktail,
)

from utils.utils import (
    get_input,
    load_data,
    display_table,
    print_message,
    save_data,
    get_menu_choice,
    display_page,
    update_record,
    unit_converter,
)


def get_next_order():
    orders = load_data("orders")

    for order_id in sorted(orders.keys()):
        if orders[order_id]["status"] == "ordered":
            return order_id, orders[order_id]

    return None, None


def all_open_orders():
    orders = load_data("orders")
    persons = load_data("persons")
    cocktails = load_data("cocktails")

    content = "Here you can find an overview of all open orders."

    display_page(location="Orders",
                 title="All open orders",
                 content=content
                 )

    columns = {
        "Name": [],
        "Cocktail": []
    }

    order_ids = []

    for order_id, order in orders.items():
        if order["status"] == "ordered":
            order_ids.append(order_id)

            person = persons[order["person"]]
            guest_name = f"{person['first_name']} {person['surname']}"

            columns["Name"].append(guest_name)
            columns["Cocktail"].append(cocktails[order["cocktail"]]["name"])

    columns["Name"].extend(["", "Back to orders menu"])
    columns["Cocktail"].extend(["", ""])

    display_table(columns, auto_number=True)

    menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

    if menu_choice == 0:
        return None, None

    order_id = order_ids[menu_choice - 1]

    return order_id, orders[order_id]


def process_order(order_id, order):

    persons = load_data("persons")
    cocktails = load_data("cocktails")
    inventory = load_data("inventory")

    guest_name = f"{persons[order["person"]]["first_name"]} {persons[order["person"]]["surname"]}"
    cocktail_name = cocktails[order["cocktail"]]["name"]

    content = f"""Guest:      [blue]{guest_name}[/]
Cocktail:   [blue]{cocktail_name}[/]"""

    display_page(location="Orders",
                 title="Process order",
                 content=content
                 )

    columns = {
        "Action": ["Prepare cocktail", "Cancel order", "", "Back to order menu"]
    }

    display_table(columns, auto_number=True)

    menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

    if menu_choice == 0:
        return

    elif menu_choice == 1:
        while True:
            ingredients = cocktails[order["cocktail"]]["ingredients"]
            instructions = cocktails[order["cocktail"]]["instructions"]
            show_cocktail(cocktail_name, ingredients, instructions)

            columns = {
                "Action": ["Cocktail served", "Order cancelled", "Unit converter", "", "Back to order menu"]
            }

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

            if menu_choice == 1:
                for ingredient in ingredients.keys():
                    for item_id, item in inventory.items():
                        if ingredient == item["name"]:
                            quantity = item["quantity"]
                            quantity -= 1

                            update_record("inventory", item_id, "quantity", quantity)

                update_record("order", order_id, "status", "served")

                print_message("Order successfully served", "green")
                print()
                get_input()

            elif menu_choice == 2:
                update_record("orders", order_id, "status", "cancelled")
                print_message("Order successfully cancelled", "green")
                print()
                get_input()

            elif menu_choice == 3:
                unit_converter()

                continue

            break

    elif menu_choice == 2:
        update_record("orders", order_id, "status", "cancelled")
        print_message("Order successfully cancelled", "green")
        print()
        get_input()

    return


def new_order():
    current_event, current_event_id = get_current_event()
    if current_event is None:
        return

    while True:
        person_id = select_guest("new_order")
        if person_id is None:
            return

        cocktail_id = select_cocktail()
        orders = load_data("orders")

        order = {
            "id": str(len(orders) + 1),
            "event": current_event_id,
            "person": str(person_id),
            "cocktail": cocktail_id,
            "status": "ordered"
        }
        low_on_stock = check_cocktail_availability(cocktail_id)

        if low_on_stock:
            print_message("Cocktail cannot be ordered.", "red")
            print()
            print_message(f"The following ingredients are low on stock:")
            for ingredient in low_on_stock:
                print_message(f" - {ingredient}")

            print()
            get_input("Click [blue]Enter[/] to select another cocktail.")
            continue

        else:
            save_data("orders", order)

            content = "[green]Order successfully placed.[/]"

            display_page(location="Orders",
                         title="Order placed",
                         content=content
                         )

            columns = {
                "Action": ["Place another order", "Back to orders menu"]
            }

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

            if menu_choice == 1:
                order.clear()
                continue

            break
    return