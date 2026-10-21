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
)

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
    while True:
        current_event, current_event_id = select_event()

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

        save_data("orders", order)

        get_input("New order successfully placed.", "green")
        order.clear()


def prepare_order():
    pass

def cancel_order():
    pass

