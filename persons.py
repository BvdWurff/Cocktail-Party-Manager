from utils.utils import (
    display_table,
    load_data,
    save_data,
    get_input,
    print_message,
    get_menu_choice,
    display_page,
)

from events import (
    get_current_event,
    add_guest_to_event,
    get_event_guests,
)

from utils.constants import (
    INVALID_INPUT,
)


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

            columns = {
                "Name": ["Create another account", "Back"]
            }

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(1, len(columns["Name"]) + 1))

            if menu_choice == 1:
                continue

            break

    return created_guests_ids


def select_guest(trigger=""):
    current_event, current_event_id = get_current_event()
    if current_event is None:
        return None

    if trigger == "new_order":
        content = "Select the guest you want to place an order for."

    else:
        content = f"A list off all the guests, linked to the current event."

    display_page(location="Guests",
                 title="Available guests",
                 content=content
                 )

    guest_names, guest_ids = get_event_guests()

    guest_names.append("")
    guest_names.append("Guest not on list")

    columns = {
        "Name": guest_names
    }

    display_table(columns, auto_number=True)

    menu_choice = get_menu_choice(range(0, len(columns["Name"]) -1))
    guest_id = guest_ids[menu_choice - 1]

    if menu_choice == 0:
        guest_id = add_guest_to_event()
        if guest_id is None:
            return None

    return str(guest_id)