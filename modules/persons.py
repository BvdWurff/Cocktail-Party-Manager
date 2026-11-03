from utils.utils import (
    display_table,
    load_data,
    save_data,
    get_input,
    print_message,
    get_menu_choice,
    display_page,
)

from modules.events import (
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
    if menu_choice == 0:
        guest_id = add_guest_to_event()
        if guest_id is None:
            return None

    else:
        guest_id = guest_ids[menu_choice - 1]

    return str(guest_id)


def show_all_persons():
    while True:

        persons = load_data("persons")

        content = f"A list off all the active persons in the cocktail party manager app."

        display_page(location="Persons",
                     title="Active persons",
                     content=content
                     )

        people_ids = []

        columns = {
            "Name": []
        }

        for person_id, person in sorted(persons.items(), key=lambda entry: entry[1]["first_name"].casefold()):
            if person["active"]:
                people_ids.append(person_id)
                name = f"{person["first_name"]} {person["surname"]}"
                columns["Name"].append(name)

        columns["Name"].extend(["", "Back to main menu"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))
        if menu_choice == 0:
            break

        else:
            person_id = people_ids[menu_choice - 1]
            show_person(person_id)

    return


def show_person(person_id):
    persons = load_data("persons")
    person = persons[person_id]
    name = f"{person["first_name"]} {person["surname"]}"

    while True:
        cocktails = load_data("cocktails")
        orders = load_data("orders")
        order_counter = 0
        orders_list = []

        for order_id, order in orders.items():
            if person_id == order["person"] and order["status"] == "served":
                orders_list.append({"id": order_id, **order})
                order_counter += 1

        events = load_data("events")
        event_counter = 0
        events_list = []

        for event_id, event in events.items():
            if person_id in event["guests"] and not event["active"]:
                events_list.append({"id": event_id, **event})
                event_counter += 1

        rankings = load_data("rankings")
        ranking_counter = 0
        rankings_list = []

        for ranking_id, ranking in rankings.items():
            if person_id == ranking["person"]:
                rankings_list.append({"id": ranking_id, **ranking})
                ranking_counter += 1

        content = f"""Here you can find all information about [blue]{name}[/].\n
Events attended:     [blue]{event_counter}[/]
Cocktails ordered:   [blue]{order_counter}[/]
Ranking votes:       [blue]{ranking_counter}[/]"""

        display_page(location="Persons",
                     title=name,
                     content=content
                     )

        columns = {
            "Event": [],
            "Date": [],
            "Cocktails": []
        }

        for event in events_list:
            columns["Event"].append(event["name"])
            columns["Date"].append(event["date"])
            cocktail_counter = 0
            for order in orders_list:
                if order["event"] == event["id"]:
                    cocktail_counter += 1
            columns["Cocktails"].append(cocktail_counter)

        display_table(columns)

        columns = {
            "Cocktail": [],
            "Ordered": [],
        }

        cocktails_list = {}

        for order in orders_list:
            cocktail_id = order["cocktail"]
            cocktails_list[cocktail_id] = cocktails_list.get(cocktail_id, 0) + 1

        for cocktail_id, counter in sorted(cocktails_list.items(), reverse=True, key=lambda item: item[1]):
            columns["Cocktail"].append(cocktails[cocktail_id]["name"])
            columns["Ordered"].append(counter)

        display_table(columns)

        get_input()

        # cocktail_names, cocktail_servings = get_event_cocktails(event_id)
        #
        # if cocktail_names:
        #     columns = {
        #         "Cocktail": cocktail_names,
        #         "Times served": cocktail_servings,
        #     }
        #
        #     display_table(columns)
        #
        # today = datetime.datetime.now()
        # event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")
        #
        # if event_date.date() >= today.date():
        #     columns = {
        #         "Action": ["Add guest", "Cancel event", "", "Back to event menu"]
        #     }
        #
        #     display_table(columns, auto_number=True)
        #
        #     menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))
        #
        #     if menu_choice == 1:
        #         _ = add_guest_to_event(event, event_id)
        #         continue
        #
        #     elif menu_choice == 2:
        #         if event["current"]:
        #             print_message("You cannot cancel the current event.", "red")
        #             print()
        #             get_input()
        #             continue
        #
        #         from modules.orders import cancel_order
        #         cancel_order(event_id=event_id)
        #
        #         update_record("events", event_id, "active", False)
        #         update_record("events", event_id, "current", False)
        #         print_message("The event was successfully canceled", "green")
        #         print()
        #         get_input()
        #         break
        #
        # else:
        #     get_input()
        #
        # break

    return





