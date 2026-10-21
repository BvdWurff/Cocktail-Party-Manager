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
    while True:
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

        for guest_id, guest_name in sorted(options.items()):
            options_column_1.append(guest_id)
            options_column_2.append(guest_name)

        options_column_1.append("")
        options_column_1.append(0)
        options_column_2.append("")
        options_column_2.append("Guest not on list")

        console.print(
            Padding(display_table(name_column_1="ID", options_column_1=options_column_1, name_column_2="Name",
                                  options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        guest_id = int(get_input("Select the ID of the guest you want to order a cocktail for: "))

        if guest_id == 0:
            add_guest_to_event(current_event, current_event_id)
            continue

        break

    return str(guest_id)


def add_guest_to_event(current_event, current_event_id):

    clear_terminal()

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

    for guest_id, guest_name in sorted(options.items()):
        options_column_1.append(guest_id)
        options_column_2.append(guest_name)

    options_column_1.append("")
    options_column_1.append(0)
    options_column_2.append("")
    options_column_2.append("Guest not on list")

    console.print(
        Padding(display_table(name_column_1="ID", options_column_1=options_column_1, name_column_2="Name",
                              options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    for_guest = int(get_input("Select the ID of the guest you want to order a cocktail for: "))

    if for_guest == 0:
        for_guest = new_person("new_order")

        if for_guest is None:
            return

    current_event["guests"].append(str(for_guest))

    save_data("events", current_event, record_id=str(current_event_id))

    return