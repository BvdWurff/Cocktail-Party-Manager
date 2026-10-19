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
    register_new_event,
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


def new_order():
    events = load_data("events")
    today = datetime.datetime.now()

    current_event = {}

    for event in events:
        event_date = datetime.datetime.strptime(events[event]["date"], "%d-%m-%Y")
        if (event_date.day, event_date.month, event_date.year) == (today.day, today.month, today.year):
            current_event = events[event]

    if not current_event:
        print_message("There is no event for today.", "red")
        print()
        create_event = get_input("Would you like to create a new event? (Yes/No) ").lower()

        if create_event == "yes":
            current_event = register_new_event()

            if not current_event:
                print()
                get_input("No event was created. Press Enter to return to the orders menu.")
                return

        else:
            print()
            get_input("Press Enter to return to the orders menu.")
            return

    persons = load_data("persons")

    options = {}

    for guest_id in current_event["guests"]:
        guest = persons.get(str(guest_id))

        if guest:
            name = f"{guest['first_name']} {guest['surname']}"
            options[int(guest_id)] = name

    options_column_1 = []
    options_column_2 = []

    for guest_id, guest_name in sorted(options.items()):
        print(guest_id)
        options_column_1.append(guest_id)
        options_column_2.append(guest_name)

    console.print(
        Padding(display_table(name_column_1="ID", options_column_1=options_column_1, name_column_2="Name",
                              options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    get_input("""Select the guest you want to order a cocktail for.
     (Select 0 if the guest is not on the list.) """)