# ==============================
# FUNCTION IMPORTS
# ==============================

from rich.console import Console
from rich.padding import Padding
from rich.table import Table
from rich import box

from inventory import (
    check_cocktail_availability,
)

from persons import select_guest
from events import select_event

from cocktails import (
    select_cocktail,
    show_cocktail,
)

from utils.utils import (
    get_input,
    load_data,
    display_table,
    print_message,
    clear_terminal,
    save_data,
    get_menu_choice,
    display_page,
    update_record,
    unit_converter,
)


# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    CONTINUE_PROMPT,
)


# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)

def get_next_order():
    orders = load_data("orders")

    for order_id in sorted(orders.keys()):
        if orders[order_id]["status"] == "ordered":
            return order_id, orders[order_id]

    return 0, {}


def all_open_orders():
    orders = load_data("orders")
    persons = load_data("persons")
    cocktails = load_data("cocktails")

    content = "Here you can find an overview of all open orders."

    display_page(location="Orders",
                 title="All open orders",
                 content=content
                 )

    options_column_1 = []
    options_column_2 = []
    options_column_3 = []
    order_ids = []
    order_lists = []

    counter = 0

    for order_id, order in orders.items():
        if orders[order_id]["status"] == "ordered":
            order_ids.append(order_id)
            order_lists.append(order)

            counter += 1
            options_column_1.append(counter)

            guest_name = f"{persons[order["person"]]["first_name"]} {persons[order["person"]]["surname"]}"
            options_column_2.append(guest_name)

            cocktail_name = cocktails[order["cocktail"]]["name"]
            options_column_3.append(cocktail_name)

    options_column_1.append("")
    options_column_2.append("")
    options_column_3.append("")
    options_column_1.append(0)
    options_column_2.append("Terug")
    options_column_3.append("-")

    table = Table(
        box=box.SQUARE,
        expand=True,
        header_style="bold bright_white",
        border_style="bright_yellow",
        padding=(0, 1),
        width=70
    )

    table.add_column("Option", min_width=4)
    table.add_column("Name")
    table.add_column("Cocktail")

    for option_c1, option_c2, option_c3 in zip(options_column_1, options_column_2, options_column_3):
        table.add_row(str(option_c1), option_c2, option_c3)

    console.print(
    Padding(table, (0, 0, 1, 5))
    )

    menu_choice = get_menu_choice(range(0, len(options_column_1) -1))
    order_id = order_ids[menu_choice - 1]

    if menu_choice == 0:
        return order_id, {}

    else:
        return order_id, orders[order_id]


def process_order(order_id, order):
    if not order:
        return

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

    options_column_2 = ["Prepare cocktail", "Cancel order", "", "Back to order menu"]

    console.print(
        Padding(display_table(options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))

    if menu_choice == 1:
        while True:
            ingredients = cocktails[order["cocktail"]]["ingredients"]
            instructions = cocktails[order["cocktail"]]["instructions"]
            show_cocktail(cocktail_name, ingredients, instructions)

            options_column_2 = ["Cocktail served", "Order cancelled", "Unit converter", "", "Back to order menu"]

            console.print(
                Padding(display_table(options_column_2=options_column_2, width=70), (0, 0, 1, 5))
            )

            menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))

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
                get_input(CONTINUE_PROMPT)
                return

            elif menu_choice == 3:
                unit_converter()
                continue


    elif menu_choice == 2:
        update_record("order", order_id, "status", "cancelled")
        print_message("Order successfully cancelled", "green")
        print()
        get_input(CONTINUE_PROMPT)

    return


def new_order():
    current_event, current_event_id = select_event()
    if not current_event:
        return


    while True:
        person_id = select_guest(current_event, current_event_id)
        if not person_id:
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

            options_column_2 = ["Place another order", "Back to orders menu"]

            console.print(
                Padding(display_table(options_column_2 = options_column_2, width=70), (0, 0, 1, 5))
            )

            menu_choice = get_menu_choice(range(1, 3))

            if menu_choice == 1:
                order.clear()
                continue

            break
    return