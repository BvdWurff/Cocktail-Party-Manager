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
    save_data,
    clear_terminal,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


# ==============================
# LOAD DATA
# ==============================

def new_event(trigger=""):
    events = load_data("events")
    today = datetime.datetime.now()

    while True:
        print()
        event_name = get_input("What is the name of the event? (Type STOP to return) ")

        if event_name.lower() == "stop":
            return None

        if trigger == "new_order":
            event_date = today

        else:
            event_date = get_input("What is the date of the event? (dd/mm/yyyy or today) ").lower()

            if event_date == "today":
                event_date = today

            else:
                event_date = datetime.datetime.strptime(event_date, "%d-%m-%Y")

            for event in events.values():
                if event["date"] == event_date:
                    print()
                    print_message(f"An event is already registered for {event_date}.", "red")
                    print()
                    continue
        break


    persons = load_data("persons")

    options = {}

    for person in persons.keys():
        name = f"{persons[person]["first_name"]} {persons[person]["surname"]}"
        options[int(person)] = name

    options_column_1 = []
    options_column_2 = []

    for person_id, person_name in sorted(options.items()):
        options_column_1.append(person_id)
        options_column_2.append(person_name)

    console.print(
        Padding(display_table(name_column_1="ID", options_column_1=options_column_1, name_column_2= "Name", options_column_2=options_column_2, width = 70), (0, 0, 1, 5))
    )

    guests = []

    while True:
        guest = get_input("Type the ID of the guest you want to add to the event: (type 0 to continue) ")
        print()
        if guest == "0":
            break
        else:
            guests.append(guest)

    event = {
        "id": str(len(events) + 1),
        "name": event_name,
        "date": event_date,
        "guests": guests
    }

    save_data("events", event)

    return event["id"]



def select_event():
    clear_terminal()

    while True:
        events = load_data("events")
        today = datetime.datetime.now()
        current_event_id = ""

        current_event = {}

        for event_id, event in events.items():
            event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")
            if event_date.date() == today.date():
                current_event_id = event_id
                current_event = event

        if not current_event:
            print_message("There is no event for today.", "red")
            print()
            create_event = get_input("Would you like to create a new event? (Yes/No) ").lower()

            if create_event == "yes":
                current_event = new_event("new_order")

                if not current_event:
                    print()
                    get_input("No event was created. Press Enter to return to the orders menu.")
                    return

                continue

            else:
                print()
                get_input("Press Enter to return to the orders menu.")
                return

        return current_event, current_event_id