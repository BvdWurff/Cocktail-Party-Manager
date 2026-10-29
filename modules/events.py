# ==============================
# FUNCTION IMPORTS
# ==============================

import datetime

from utils.utils import (
    get_input,
    load_data,
    display_table,
    print_message,
    save_data,
    get_menu_choice,
    display_page, update_record,
)

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    INVALID_INPUT,
)


def get_current_event():
    events = load_data("events")

    for event_id, event in events.items():
        if event["current"]:
            return event, event_id

    event, event_id = select_event()
    if event is None:
        return None, None

    return event, event_id


def show_event(event=None, event_id=None):
    if event is None:
        event, event_id = get_current_event()
        if event is None:
            return

    while True:
        orders = load_data("orders")

        content = f"""Here you can find all relevant event information.\n
Event name:         [blue]{event["name"]}[/]
Event date:         [blue]{event["date"]}[/]"""

        guests, guest_ids = get_event_guests(event)
        if len(guests) > 0:
            content = f"{content}\nNumber of guests:   [blue]{len(guests)}[/]"

        cocktail_counter = 0

        for order in orders.values():
            if order["event"] == event_id and order["status"] == "served":
                cocktail_counter += 1

        if cocktail_counter > 0:
            content = f"{content}\nCocktails serverd:  [blue]{cocktail_counter}[/]"

        display_page(location="Events",
                     title="Event details",
                     content=content
                     )

        guests, guest_ids = get_event_guests(event)
        served_cocktails = []

        for guest_id in guest_ids:
            cocktail_counter = 0
            for order in orders.values():
                if order["event"] == event_id and order["status"] == "served" and order["person"] == str(guest_id):
                    cocktail_counter += 1
            served_cocktails.append(str(cocktail_counter))

        columns = {
            "Guest": guests,
            "Served cocktails": served_cocktails,
        }

        display_table(columns)

        cocktail_names, cocktail_servings = get_event_cocktails(event_id)

        if cocktail_names:
            columns = {
                "Cocktail": cocktail_names,
                "Times served": cocktail_servings,
            }

            display_table(columns)

        today = datetime.datetime.now()
        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")

        if event_date.date() >= today.date():
            columns = {
                "Action": ["Add guest",  "Cancel event", "", "Back to event menu"]
            }

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

            if menu_choice == 1:
                _ = add_guest_to_event(event, event_id)
                continue

            elif menu_choice == 2:
                if event["current"]:
                    print_message("You cannot cancel the current event.","red")
                    print()
                    get_input()
                    continue

                update_record("events", event_id, "active", False)
                update_record("events", event_id, "current", False)
                print_message("The event was successfully canceled", "green")
                print()
                get_input()
                break

        else:
            get_input()

        break

    return


def show_all_events(event_filter):
    while True:
        content = f"Here you find an overview of all {event_filter} events."

        display_page(
            location="Events",
            title=f"All {event_filter} events",
            content=content
        )

        today = datetime.date.today()
        events = load_data("events")

        event_ids = []

        columns = {
            "Event": [],
            "Date": []
        }

        for event_id, event in sorted(events.items(), key=lambda item: datetime.datetime.strptime(item[1]["date"], "%d-%m-%Y"), reverse=event_filter == "past"):
            event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y").date()

            if event_filter == "upcoming":
                include_event = event["active"] and event_date > today
            else:
                include_event = event_date < today

            if include_event:
                event_ids.append(event_id)
                columns["Event"].append(event["name"])
                columns["Date"].append(event["date"])

        columns["Event"].extend(["", "Back to event menu"])
        columns["Date"].extend(["", ""])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Event"]) - 1))
        event_id = event_ids[menu_choice - 1]

        if menu_choice == 0:
            break

        else:
            show_event(events[event_id], event_id)
            break

    return


def new_event(trigger=""):
    content = """Here you can create a new event.

Type [blue]Stop[/] to exit the registration process."""

    display_page(location="Events",
                 title="Create event",
                 content=content
                 )

    events = load_data("events")
    today = datetime.date.today().strftime("%d-%m-%Y")

    while True:
        current = False

        event_name = get_input("What is the name of the event? ")

        if event_name.lower() == "stop":
            return None, None

        if trigger == "new_order":
            event_date = today
            current = True

        else:
            while True:
                event_date = get_input("What is the date of the event? (dd-mm-yyyy or today) ").lower()

                if event_date == "stop":
                    return None, None

                elif event_date == "today":
                    event_date = today
                    current = True

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

                return None, None

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

        columns = {
            "Name": []
        }

        guest_ids = []

        for person_id, person_name in sorted(options.items(), key=lambda item: item[1].casefold()):
            guest_ids.append(person_id)
            columns["Name"].append(person_name)

        columns["Name"].extend(["", "Continue"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

        if menu_choice == 0:
            break

        guest_id = guest_ids[menu_choice - 1]
        guests.append(str(guest_id))

    event = {
        "id": str(len(events) + 1),
        "name": event_name,
        "date": event_date,
        "current": current,
        "active": True,
        "guests": guests
    }

    save_data("events", event)

    return event, event["id"]


def select_event():
    events = load_data("events")
    today = datetime.datetime.now()
    current_event: dict | None = None
    current_event_id: str | None = None

    for event_id, event in events.items():
        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")
        if event_date.date() == today.date():
            current_event_id = event_id
            current_event = event

    if current_event is None:
        content = "[red]There is no event available for today.[/]"

        display_page(location="Events",
                     title="Select event",
                     content=content
                     )

        while True:
            create_event = get_input("Would you like to create a new event? (Yes/No) ").lower()

            if create_event not in ["yes", "no"]:
                print_message(INVALID_INPUT)
                continue

            break

        if create_event == "yes":
            current_event, current_event_id = new_event("new_order")

            if current_event is None:
                print()
                get_input("No event was created. Press [blue]Enter[/] to return to the orders menu.")
                return None, None

        else:
            return None, None

    if current_event is None or current_event_id is None:
        return None, None

    current_event["current"] = True
    update_record("events", current_event_id, "current", True)

    return current_event, current_event_id


def get_event_guests(event=None):
    if event is None:
        event, _ = get_current_event()

    persons = load_data("persons")
    options = {}

    for guest_id in event["guests"]:
        guest = persons[guest_id]

        if guest["active"]:
            name = f"{guest['first_name']} {guest['surname']}"
            options[int(guest_id)] = name

    guest_names = []
    guest_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guest_ids.append(guest_id)
        guest_names.append(guest_name)

    return guest_names, guest_ids


def get_event_cocktails(event_id=None):
    if event_id is None:
        _, event_id = get_current_event()

    orders = load_data("orders")
    cocktails = load_data("cocktails")
    cocktail_dict = {}

    for order in orders.values():
        if order["event"] == event_id and order["status"] == "served":
            cocktail_name = cocktails[order["cocktail"]]["name"]

            if cocktail_name in cocktail_dict:
                cocktail_dict[cocktail_name] += 1
            else:
                cocktail_dict[cocktail_name] = 1

    cocktail_names = []
    cocktail_servings = []

    for cocktail, number in sorted(cocktail_dict.items(), key=lambda item: item[0].casefold()):
        cocktail_names.append(cocktail)
        cocktail_servings.append(str(number))

    return cocktail_names, cocktail_servings


def add_guest_to_event(event=None, event_id=None):
    from persons import new_person

    if event is None:
        event, event_id = get_current_event()
        if event is None:
            return None

    persons = load_data("persons")
    options = {}

    for person_id, person in persons.items():
        if person_id not in event["guests"]:
            guest = persons[person_id]

            if guest["active"]:
                name = f"{guest["first_name"]} {guest["surname"]}"
                options[int(person_id)] = name

    guest_names = []
    guests_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guests_ids.append(guest_id)
        guest_names.append(guest_name)

    if len(guest_names) == 0:
        guest_id = new_person("new_order")

        if guest_id is None:
            return None

    else:
        guest_names.append("")
        guest_names.append("Guest not on list")

        content = f"Select the guest you want to add to the event."

        display_page(location="Events",
                     title="Add guests",
                     content=content
                     )

        columns = {
            "Name": guest_names
        }

        print()
        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))
        guest_id = guests_ids[menu_choice - 1]

        if menu_choice == 0:
            guest_id = new_person("new_order")

            if guest_id is None:
                return None

    event["guests"].append(str(guest_id))

    save_data("events", event, record_id=str(event_id))

    return guest_id
