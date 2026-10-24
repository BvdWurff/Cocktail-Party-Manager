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
    get_menu_choice,
    display_page,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    SELECT_OPTION,
    INVALID_INPUT,
    CONTINUE_PROMPT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


# ==============================
# LOAD DATA
# ==============================


def show_todays_event():
    events = load_data("events")
    today = datetime.date.today().strftime("%d-%m-%Y")
    todays_event = ""

    for event_id in events.values():
        if event_id["date"] == today:
            return event_id, events[event_id]
        print("No even created for today.")

    get_input(CONTINUE_PROMPT)



def show_all_events():
    pass


def new_event(trigger=""):
    content = """Here you can create a new event.

Type [red]Stop[/] to exit the registration process."""

    display_page(location="Events",
                 title="Create event",
                 content=content
                 )

    events = load_data("events")
    today = datetime.date.today().strftime("%d-%m-%Y")

    while True:
        event_name = get_input("What is the name of the event? ")

        if event_name.lower() == "stop":
            return None

        if trigger == "new_order":
            event_date = today

        else:
            while True:
                event_date = get_input("What is the date of the event? (dd-mm-yyyy or today) ").lower()

                if event_date == "stop":
                    return None

                elif event_date == "today":
                    event_date = today

                else:
                    try:
                        parsed_date = datetime.datetime.strptime(event_date, "%d-%m-%Y")

                        if parsed_date.date() < datetime.date.today():
                            print()
                            print_message("The event date cannot be in the past.", "red")
                            print()
                            continue

                        event_date = parsed_date.strftime("%d-%m-%Y")

                    except ValueError:
                        print_message(INVALID_INPUT, "red")
                        continue

                break

        for event in events.values():
            if event["date"] == event_date:
                print()
                print_message(f"An event is already registered for {event_date}.", "red")
                print()
                get_input("Press [blue]Enter[/] to return to the events menu")

                return None

        break

    guests = []

    while True:
        content = f"Here you can select guests you want to add the event."

        display_page(location="Events",
                     title="Add guests",
                     content=content
                     )

        persons = load_data("persons")

        options = {}

        for person in persons.keys():
            if person not in guests and persons[person]["active"] == True:
                name = f"{persons[person]["first_name"]} {persons[person]["surname"]}"
                options[int(person)] = name

        options_column_2 = []
        guests_ids = []

        for person_id, person_name in sorted(options.items(), key=lambda item: item[1].casefold()):
            guests_ids.append(person_id)
            options_column_2.append(person_name)

        options_column_2.append("")
        options_column_2.append("Continue")

        console.print(
            Padding(display_table(name_column_2="Name", options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))
        guest_id = guests_ids[menu_choice - 1]

        if menu_choice == 0:
            break
        else:
            guests.append(str(guest_id))

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
                    get_input("No event was created. Press [blue]Enter[/] to return to the orders menu.")
                    return {}, ""

                continue

            else:
                print()
                get_input("Press [blue]Enter[/] to return to the orders menu.")
                return {}, ""

        return current_event, current_event_id