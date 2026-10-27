from rich.console import Console
from rich.padding import Padding

from utils.utils import (
    display_table,
    load_data,
    save_data,
    get_input,
    print_message,
    clear_terminal,
    get_menu_choice,
    display_page,
)

from utils.constants import (
    INVALID_INPUT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)



def new_person(trigger=""):
    created_guests_ids = []
    while True:
        while True:
            content = f"""Here you can register new guests.
        
Type [red]Stop[/] to exit the registration process."""

            confirmation_choice = ""

            display_page(location="Guests",
                         title="Register guest",
                         content=content
                         )

            first_name = get_input("What is the first name of the guest? ")

            if first_name.lower() == "stop":
                print()
                get_input("Press [blue]Enter[/] to exit the registration process.")
                return None

            surname = get_input("What is the surname of the guest? ")

            if surname.lower() == "stop":
                print()
                get_input("Press [blue]Enter[/] to exit the registration process.")
                return None

            persons = load_data("persons")
            duplicate = False

            for person in persons.values():
                if person["first_name"].lower() == first_name.lower() and person["surname"].lower() == surname.lower():
                    duplicate = True
                    print()
                    print_message(f"A person named {first_name} {surname} already exists.", "red")

                    while True:
                        print()
                        confirmation_choice = get_input("Are you sure you want to create another person with this name? (Yes/No) ").lower()

                        if confirmation_choice not in ("yes", "no"):
                            print_message(INVALID_INPUT, "red")
                            continue

                        break


            if confirmation_choice == "yes" or not duplicate:
                break

            continue

        person = {
            "id": str(len(persons) + 1),
            "first_name": first_name,
            "surname": surname,
            "active": True
        }

        save_data("persons", person)
        print()
        print_message("Guest successfully registered.", "green")

        if trigger == "new_order":
            print()
            get_input("Press [blue]Enter[/] to return to the order process.")

            return person["id"]

        else:
            created_guests_ids.append(person["id"])
            options_column_2 = ["Create another account", "Back"]

            console.print(
                Padding(display_table(name_column_2="Name", options_column_2=options_column_2, width=70), (1, 0, 1, 5))
            )

            menu_choice = get_menu_choice(range(1, 3))

            if menu_choice == 1:
                continue

            break

    return created_guests_ids


def select_guest(current_event, current_event_id, trigger=""):
    if trigger == "new_order":
        content = "Select the guest you want to place an order for."

    else:
        content = f"A list off all the guests, linked to the current event."

    display_page(location="Guests",
                 title="Available guests",
                 content=content
                 )

    options_column_2, guest_ids = get_guests_event(current_event)

    options_column_2.append("")
    options_column_2.append("Guest not on list")

    console.print(
        Padding(display_table(name_column_2="Name", options_column_2=options_column_2, width=70), (0, 0, 1, 5))
    )

    menu_choice = get_menu_choice(range(0, len(options_column_2) -1))
    guest_id = guest_ids[menu_choice - 1]

    if menu_choice == 0:
        guest_id = add_guest_to_event(current_event, current_event_id, trigger="new_order")

    return str(guest_id)


def add_guest_to_event(current_event, current_event_id, trigger=""):
    clear_terminal()

    persons = load_data("persons")
    options = {}

    for person_id in persons:
        if person_id not in current_event["guests"]:
            guest = persons.get(str(person_id))

            if guest["active"]:
                name = f"{guest['first_name']} {guest['surname']}"
                options[int(person_id)] = name

    options_column_2 = []
    guests_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guests_ids.append(guest_id)
        options_column_2.append(guest_name)

    if len(options_column_2) == 0:
        guest_id = new_person("new_order")

        if guest_id is None:
            return None

    else:
        options_column_2.append("")
        options_column_2.append("Guest not on list")

        if trigger == "new_order":
            content = f"Select the guest you want to add to the event."

            display_page(location="Events",
                         title="Add guests",
                         content=content
                         )

        console.print(
            Padding(display_table(name_column_2="Name", options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))
        guest_id = guests_ids[menu_choice - 1]

        if menu_choice == 0:
            guest_id = new_person("new_order")

            if guest_id is None:
                return None

    current_event["guests"].append(str(guest_id))

    save_data("events", current_event, record_id=str(current_event_id))

    return guest_id


def get_guests_event(current_event):
    persons = load_data("persons")
    options = {}

    for guest_id in current_event["guests"]:
        guest = persons.get(str(guest_id))

        if guest["active"]:
            name = f"{guest['first_name']} {guest['surname']}"
            options[int(guest_id)] = name

    guest_names = []
    guest_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guest_ids.append(guest_id)
        guest_names.append(guest_name)

    return guest_names, guest_ids