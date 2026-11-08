# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.cocktails import (
    select_cocktail,
    show_cocktail,
)

from modules.events import (
    get_current_event,
)

from modules.guests import (
    select_guest,
    get_guest_full_name,
)

from modules.inventory import check_cocktail_availability

from modules.unit_converter import unit_converter

from utils.utils import (
    get_input,
    load_data,
    display_table,
    print_message,
    save_data,
    get_menu_choice,
    display_page,
    update_record,
    confirm_action,
)


# ==============================
# ORDER CREATION
# ==============================

def new_order(cocktail_id=None, guest_id=None):
    """
    Creates a new cocktail order for the current event.

    Allows the user to select a guest and cocktail when these are
    not provided. Guests are added to the current event if necessary.
    After saving an order, the user can choose to place another order.

    Args:
        cocktail_id (str, optional): The ID of the cocktail to order.
        guest_id (str, optional): The ID of the guest placing the order.

    Returns:
        None: Returns after the order process is completed or cancelled.
    """
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
                     title="Order Placed",
                     content=content
                     )

        columns = {
            "Action": ["Place Another Order", "", "Back"]
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


# ==============================
# ORDER RETRIEVAL AND SELECTION
# ==============================

def get_next_order():
    """
    Retrieves the oldest open order for the current event.

    Orders are checked in ascending numerical order of their IDs.
    Only orders with the status "ordered" are considered.

    Returns:
        tuple: The order ID and its corresponding order dictionary.
            Returns (None, None) when no matching order is found.
    """
    orders = load_data("orders")
    event, event_id = get_current_event()

    for order_id in sorted(orders.keys(), key=int):
        if orders[order_id]["status"] == "ordered" and orders[order_id]["event"] == event_id:
            return order_id, orders[order_id]

    return None, None


def all_open_orders():
    """
    Displays all open orders for the current event and allows
    the user to select an order for processing.

    The overview includes the guest name and cocktail name
    associated with each open order.

    Returns:
        tuple: The selected order ID and its corresponding order
            dictionary, or (None, None) when no order is selected.
    """
    current_event, current_event_id = get_current_event()
    if current_event_id is None:
        return None, None
    orders = load_data("orders")
    guests = load_data("guests")
    cocktails = load_data("cocktails")

    content = "Here you can find an overview of all open orders."

    display_page(location="Orders",
                 title="All Open Orders",
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

            guest_id = order["guest"]
            guest_name = get_guest_full_name(guests[guest_id])

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


# ==============================
# ORDER PROCESSING
# ==============================

def process_order(order_id):
    """
    Displays the details of an existing order and provides options
    to prepare, serve, or cancel the order.

    When preparing a cocktail, the recipe and required ingredients
    are displayed. The user can also access the unit converter.

    Args:
        order_id (str): The ID of the order to process.

    Returns:
        None: Returns after processing or leaving the order.
    """
    orders = load_data("orders")
    order = orders[order_id]

    guests = load_data("guests")
    cocktails = load_data("cocktails")

    guest_id = guests[order["guest"]]
    guest_name = get_guest_full_name(guest_id)
    cocktail_name = cocktails[order["cocktail"]]["name"]

    content = f"Guest:      [blue]{guest_name}[/]\n"
    content += f"Cocktail:   [blue]{cocktail_name}[/]\n"
    content += f"Status:     [blue]{str(order["status"]).capitalize()}"

    display_page(
        location="Orders",
        title="Process Order",
        content=content
    )

    if order["status"] == "ordered":

        columns = {
            "Action": ["Prepare Cocktail", "Cancel Order", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 0:
            return

        elif menu_choice == 1:
            while True:
                show_cocktail(order["cocktail"], trigger="process_order")

                columns = {
                    "Action": ["Cocktail Served", "Order Cancelled", "Unit Converter", "", "Back"]
                }

                display_table(columns, auto_number=True)

                menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

                if menu_choice == 1:
                    if serve_order(order_id):
                        print_message("Order successfully updated.\n", "green")
                        get_input()
                        break

                    else:
                        print_message("Not all ingredients are available or the order cannot be served.\n", "red")
                        get_input()
                        continue

                elif menu_choice == 2:
                    if not confirm_action("cancel", "order"):
                        continue

                    update_record("orders", order_id, "status", "cancelled")
                    print_message("Order successfully cancelled.\n", "green")
                    get_input()

                elif menu_choice == 3:
                    unit_converter()
                    continue

                break

        elif menu_choice == 2:
            if not confirm_action("cancel", "order"):
                return

            update_record("orders", order_id, "status", "cancelled")
            print_message("Order successfully cancelled.\n", "green")
            get_input()

    else:
        get_input()

    return


def serve_order(order_id):
    """
    Serves an existing order and updates the inventory and order status.

    Validates that the order exists, has the status "ordered",
    and has sufficient ingredients available before deducting
    one unit of each required ingredient.

    Args:
        order_id (str or int): The ID of the order to serve.

    Returns:
        bool: True if the order is successfully served,
            or False if validation fails.
    """
    orders = load_data("orders")
    order_id = str(order_id)

    # Validate that the order exists and has not already been processed.
    if order_id not in orders:
        print_message("Order was not found.\n", "red")
        get_input()

        return False

    order = orders[order_id]

    if order["status"] != "ordered":
        print_message(f"Order cannot be processed, status is {order["status"]}.\n", "red")
        get_input()
        return False

    cocktail_id = order["cocktail"]
    cocktails = load_data("cocktails")
    ingredients = cocktails[cocktail_id]["ingredients"]

    # Check ingredient availability while accounting for the current order.
    if check_cocktail_availability(cocktail_id, for_existing_order=True):
        print_message(f"Order cannot be processed, not all ingredients are available.\n", "red")
        get_input()
        return False

    inventory = load_data("inventory")

    # Validate all quantities before changing the inventory.
    for ingredient_id in ingredients:
        if ingredient_id not in inventory:
            print_message(f"Order cannot be processed, not all ingredients are available.\n", "red")
            get_input()
            return False

        if inventory[ingredient_id]["quantity"] <= 0:
            print_message(f"Order cannot be processed, not all ingredients are available.\n", "red")
            get_input()
            return False

    # Deduct one unit of each ingredient.
    for ingredient_id in ingredients:
        quantity = inventory[ingredient_id]["quantity"] - 1
        update_record("inventory", ingredient_id, "quantity", quantity)

    # Mark the order as served after updating the inventory.
    update_record("orders", order_id, "status", "served")

    return True


# ==============================
# ORDER CANCELLATION
# ==============================

def cancel_order(cocktail_id="", guest_id="", event_id=""):
    """
    Cancels open orders matching a specified cocktail, guest, or event.

    The first supplied identifier determines which field is used
    to filter orders. Only orders with the status "ordered" are cancelled.

    Args:
        cocktail_id (str, optional): The cocktail ID used to filter orders.
        guest_id (str, optional): The guest ID used to filter orders.
        event_id (str, optional): The event ID used to filter orders.

    Returns:
        None: Returns after processing all matching orders.
    """
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


# ==============================
# GUEST ORDER HISTORY
# ==============================

def show_guest_orders(guest_id):
    """
    Displays the order history of a specific guest.

    The overview includes the cocktail, associated event, and order
    status. Users can select an order to view or process its details.

    Args:
        guest_id (str): The ID of the guest whose orders are displayed.

    Returns:
        None: Returns when the user leaves the order overview.
    """
    guests = load_data("guests")
    guest = guests[guest_id]
    guest_name = f"{guest["first_name"]} {guest["surname"]}"

    while True:
        content = f"A list of all orders placed by [blue]{guest_name}[/]."

        display_page(location="Orders",
                     title="Placed Orders",
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