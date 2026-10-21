import datetime

from rich.console import Console
from rich.padding import Padding

from utils.utils import (
    display_table,
    load_data,
    save_data,
    get_input,
    print_message,
    clear_terminal,
    display_panel,
    get_menu_choice,
)

from utils.constants import (
    INVALID_INPUT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)



def new_person(trigger=""):
    persons = load_data("persons")

    print()
    first_name = get_input("What is the first name of the guest? ")
    surname = get_input("What is the surname of the guest? ")


    for person in persons.values():
        if person["first_name"].lower() == first_name.lower() and person["surname"].lower() == surname.lower():
            print()
            print_message(f"A person named {first_name} {surname} already exists.", "red")

            while True:
                print()
                confirmation_choice = get_input("Are you sure you want to create another person with this name? (Yes/No) ").lower()

                if confirmation_choice not in ("yes", "no"):
                    print_message(INVALID_INPUT, "red")
                    continue

                if confirmation_choice == "yes":
                    break

                else:
                    return None

    person = {
        "id": str(len(persons) + 1),
        "first_name": first_name,
        "surname": surname,
        "active": True
    }

    save_data("persons", person)

    return person["id"]


def select_person(current_event, current_event_id):
    clear_terminal()

    persons = load_data("persons")
    options = {}

    for guest_id in current_event["guests"]:
        guest = persons.get(str(guest_id))

        if guest["active"]:
            name = f"{guest['first_name']} {guest['surname']}"
            options[int(guest_id)] = name

    options_column_1 = []
    options_column_2 = []
    guests_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guests_ids.append(guest_id)
        options_column_2.append(guest_name)

    options_column_2.append("")
    options_column_2.append("Guest not on list")

    console.print(
        Padding(display_table(name_column_1="Option", options_column_1=options_column_1, name_column_2="Name",
                              options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    menu_choice = get_menu_choice(range(0, len(options_column_2) + 1))
    guest_id = guests_ids[menu_choice - 1]

    if guest_id == 0:
        guest_id = add_guest_to_event(current_event, current_event_id, trigger="new_order")

    return str(guest_id)


def add_guest_to_event(current_event, current_event_id, trigger=""):
    clear_terminal()

    if trigger == "new_order":
        panel_content = ("""The guest was not yet added to the event.
Please select a guest from the list below, to add to the event and order a cocktail for.""")

        display_panel(panel_content, top_padding=1)

    persons = load_data("persons")
    options = {}

    for person_id in persons:
        if person_id not in current_event["guests"]:
            guest = persons.get(str(person_id))

            if guest["active"]:
                name = f"{guest['first_name']} {guest['surname']}"
                options[int(person_id)] = name

    options_column_1 = []
    options_column_2 = []
    guests_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guests_ids.append(guest_id)
        options_column_2.append(guest_name)

    options_column_2.append("")
    options_column_2.append("Guest not on list")

    console.print(
        Padding(display_table(name_column_1="Option", options_column_1=options_column_1, name_column_2="Name",
                              options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    menu_choice = get_menu_choice(range(0, len(options_column_2) + 1))
    guest_id = guests_ids[menu_choice - 1]

    if guest_id == 0:
        guest_id = new_person("new_order")

        if guest_id is None:
            return guest_id

    current_event["guests"].append(str(guest_id))

    save_data("events", current_event, record_id=str(current_event_id))

    return guest_id