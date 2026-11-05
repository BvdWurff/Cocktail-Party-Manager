# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.guests import select_guest
from modules.events import (
    get_current_event,
)

from modules.cocktails import (
    select_cocktail,
    show_cocktail,
)

from modules.inventory import check_cocktail_availability

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
    event, event_id = get_current_event()

    for order_id in sorted(orders.keys(), key=int):
        if orders[order_id]["status"] == "ordered" and orders[order_id]["event"] == event_id:
            return order_id, orders[order_id]

    return None, None


def all_open_orders():
    current_event, current_event_id = get_current_event()
    if current_event_id is None:
        return None, None
    orders = load_data("orders")
    guests = load_data("guests")
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
        if order["status"] == "ordered" and order["event"] == current_event_id:
            order_ids.append(order_id)

            guest = guests[order["guest"]]
            guest_name = f"{guest['first_name']} {guest['surname']}"

            columns["Name"].append(guest_name)
            columns["Cocktail"].append(cocktails[order["cocktail"]]["name"])

    columns["Name"].extend(["", "Back"])
    columns["Cocktail"].extend(["", ""])

    display_table(columns, auto_number=True)

    menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

    if menu_choice == 0:
        return None, None

    order_id = order_ids[menu_choice - 1]

    return order_id, orders[order_id]


def process_order(order_id):
    orders = load_data("orders")
    order = orders[order_id]

    guests = load_data("guests")
    inventory = load_data("inventory")
    cocktails = load_data("cocktails")
    cocktail = cocktails[order["cocktail"]]

    guest_name = f"{guests[order["guest"]]["first_name"]} {guests[order["guest"]]["surname"]}"
    cocktail_name = cocktails[order["cocktail"]]["name"]

    content = f"Guest:      [blue]{guest_name}[/]\n"
    content += f"Cocktail:   [blue]{cocktail_name}[/]\n"
    content += f"Status:     [blue]{str(order["status"]).capitalize()}"

    display_page(location="Orders",
                 title="Process order",
                 content=content
                 )

    if order["status"] == "ordered":

        columns = {
            "Action": ["Prepare cocktail", "Cancel order", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 0:
            return

        elif menu_choice == 1:
            while True:
                show_cocktail(order["cocktail"], trigger="process_order")

                columns = {
                    "Action": ["Cocktail served", "Order cancelled", "Unit converter", "", "Back"]
                }

                display_table(columns, auto_number=True)

                menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

                if menu_choice == 1:
                    low_on_stock = check_cocktail_availability(order["cocktail"])

                    if low_on_stock:
                        print_message("Not all ingredients are available", "red")
                        print()
                        get_input()
                        continue

                    else:
                        for ingredient in cocktail["ingredients"].keys():
                            for item_id, item in inventory.items():
                                if ingredient == item_id:
                                    quantity = item["quantity"] - 1
                                    update_record("inventory", item_id, "quantity", quantity)

                        update_record("orders", order_id, "status", "served")

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

    else:
        get_input()

    return


def new_order(cocktail_id=None, guest_id=None):
    current_event, current_event_id = get_current_event()
    if current_event is None:
        return

    while True:
        if guest_id is None:
            guest_id = select_guest("new_order")
            if guest_id is None:
                return
        else:
            if guest_id not in current_event["guests"]:
                guests = current_event["guests"]
                guests.append(guest_id)
                update_record("events", current_event_id, "guests", guests)

        if cocktail_id is None:
            cocktail_id = select_cocktail("new_order")
            if cocktail_id is None:
                return

        orders = load_data("orders")

        order = {
            "id": str(len(orders) + 1),
            "event": current_event_id,
            "guest": str(guest_id),
            "cocktail": cocktail_id,
            "status": "ordered"
        }

        save_data("orders", order)

        content = "[green]Order successfully placed.[/]"

        display_page(location="Orders",
                     title="Order placed",
                     content=content
                     )

        columns = {
            "Action": ["Place another order", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            guest_id = None
            cocktail_id = None
            order.clear()
            continue

        break
    return


def cancel_order(cocktail_id="", guest_id="", event_id=""):
    orders = load_data("orders")

    if cocktail_id:
        key = "cocktail"
        value = cocktail_id

    elif guest_id:
        key = "guest"
        value = guest_id

    elif event_id:
        key = "event"
        value = event_id

    else:
        return

    for order_id, order in orders.items():
        if order[key] == str(value) and order["status"] == "ordered":
            update_record("orders", order_id, "status", "cancelled")

    return

def show_guest_orders(guest_id):
    guests = load_data("guests")
    guest = guests[guest_id]
    guest_name = f"{guest["first_name"]} {guest["surname"]}"

    while True:
        content = f"A list of all orders placed by [blue]{guest_name}[/]."

        display_page(location="Orders",
                     title="Placed orders",
                     content=content
                     )

        orders = load_data("orders")
        cocktails = load_data("cocktails")
        events = load_data("events")

        order_ids = []

        columns = {
            "Cocktail": [],
            "Event": [],
            "Status": [],
        }

        for order_id, order in orders.items():
            if order["guest"] == guest_id:
                order_ids.append(order_id)
                columns["Cocktail"].append(cocktails[order["cocktail"]]["name"])
                columns["Event"].append(events[order["event"]]["name"])
                columns["Status"].append(str(order["status"]).capitalize())

        columns["Cocktail"].extend(["", "Back"])
        columns["Event"].extend(["", ""])
        columns["Status"].extend(["", ""])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))

        if menu_choice == 0:
            break

        order_id = order_ids[menu_choice - 1]
        process_order(order_id)

    return



