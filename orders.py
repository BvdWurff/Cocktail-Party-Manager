# ==============================
# FUNCTION IMPORTS
# ==============================

import datetime

from rich.console import Console
from rich.padding import Padding

from utils.utils import (
    get_input,
    load_data,
    display_table,
    print_message,
    clear_terminal,
    save_data,
    display_panel,
    get_menu_choice,
)

from inventory import check_cocktail_availability

from cocktails import select_cocktail
from persons import select_person
from events import select_event


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


def new_order():
    current_event, current_event_id = select_event()

    while True:
        person_id = select_person(current_event, current_event_id)
        cocktail_id = select_cocktail()
        orders = load_data("orders")

        order = {
            "id": str(len(orders) + 1),
            "event": current_event_id,
            "person": person_id,
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
            get_input("Click Enter to select another cocktail.")
            continue

        else:
            save_data("orders", order)

            print()
            print_message("New order successfully placed.", color="green")
            print()

            options_column_2 = ["New order", "Back to orders menu"]

            console.print(
                Padding(display_table(options_column_2 = options_column_2, width=70), (0, 0, 1, 5))
            )

            menu_choice = get_menu_choice(range(1, 2))

            if menu_choice == 1:
                order.clear()
                continue

            else:
                return


def prepare_order():
    pass

def cancel_order():
    pass

