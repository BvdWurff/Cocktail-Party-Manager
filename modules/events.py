# ==============================
# LIBRARY IMPORTS
# ==============================

import datetime


# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    INVALID_INPUT,
)


# ==============================
# FUNCTION IMPORTS
# ==============================

from utils.utils import (
    confirm_action,
    display_page,
    display_panel,
    display_table,
    get_input,
    get_menu_choice,
    load_data,
    print_message,
    save_data,
    update_record,
)


# ==============================
# EVENT CREATION
# ==============================

def new_event(trigger=""):
    """
    Creates a new event and allows guests to be assigned to it.

    Validates the event name and date, prevents duplicate event dates,
    and allows the user to select registered guests.

    When triggered by a new order, the event date is automatically
    set to today.

    Args:
        trigger (str): When set to "new_order", creates an event for today.

    Returns:
        tuple: The created event dictionary and its ID, or
            (None, None) if event creation is cancelled.
    """
    content = """Here you can create a new event.

Type [blue]Stop[/] to exit the registration process."""

    display_page(location="Events",
                 title="Create Event",
                 content=content
                 )

    events = load_data("events")
    today = datetime.date.today().strftime("%d-%m-%Y")

    event_date = today
    current = False

    while True:

        event_name = get_input("What is the name of the event? ").strip()

        if not event_name:
            print_message(INVALID_INPUT)
            continue

        if event_name.lower() == "stop":
            return None, None

        if trigger == "new_order":
            event_date = today

        else:
            while True:
                event_date = get_input("What is the date of the event? (dd-mm-yyyy or today) ").lower()

                if event_date == "stop":
                    return None, None

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

        current = event_date == today

        # Allow only one registered event per date.
        for event in events.values():
            if event["date"] == event_date:
                print()
                print_message(f"An event is already registered for {event_date}.", "red")
                print()
                get_input("Press [blue]Enter[/] to return to the events menu.")

                return None, None

        break

    guests_list = []

    # Allow registered, active guests to be added to the new event.
    while True:
        content = f"Here you can select the guests you want to add to the event."

        display_page(location="Events",
                     title="Add Guests",
                     content=content
                     )

        guests = load_data("guests")

        options = {}

        for guest in guests.keys():
            if guest not in guests_list and guests[guest]["active"] == True:
                name = f"{guests[guest]["first_name"]} {guests[guest]["surname"]}"
                options[int(guest)] = name

        columns = {
            "Name": []
        }

        guest_ids = []

        for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
            guest_ids.append(guest_id)
            columns["Name"].append(guest_name)

        columns["Name"].extend(["", "Continue"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))

        if menu_choice == 0:
            break

        guest_id = guest_ids[menu_choice - 1]
        guests_list.append(str(guest_id))

    event = {
        "id": str(len(events) + 1),
        "name": event_name,
        "date": event_date,
        "current": current,
        "active": True,
        "guests": guests_list
    }

    save_data("events", event)

    return event, event["id"]


# ==============================
# EVENT SELECTION
# ==============================

def select_event():
    """
    Selects an active event scheduled for today.

    If no event is available, the user can create a new event
    for the current date.

    Returns:
        tuple: The selected event dictionary and its ID, or
            (None, None) if no event is selected or created.
    """
    events = load_data("events")
    today = datetime.datetime.now()
    current_event: dict | None = None
    current_event_id: str | None = None

    for event_id, event in events.items():
        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")
        if event_date.date() == today.date() and event["active"]:
            current_event_id = event_id
            current_event = event

    if current_event is None:
        content = "[red]There is no event available for today.[/]"

        display_page(location="Events",
                     title="Select Event",
                     content=content
                     )

        print_message("Would you like to create a new event?\n", "bright_white")

        columns = {
            "Action": ["Yes", "No"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

        if menu_choice == 1:
            current_event, current_event_id = new_event("new_order")

            if current_event is None:
                print()
                get_input("No event was created. Press [blue]Enter[/] to return to the previous menu.")

                return None, None

        return None, None

    if current_event is None or current_event_id is None:
        return None, None

    # current_event["current"] = True
    update_record("events", current_event_id, "current", True)

    return current_event, current_event_id


def get_current_event():
    """
    Retrieves the active event marked as current.

    If no active current event exists, starts the event selection
    process to find or create an event for today.

    Returns:
        tuple: The current event dictionary and its ID, or
            (None, None) if no event is available.
    """
    events = load_data("events")

    for event_id, event in events.items():
        if event["current"] and event["active"]:
            return event, event_id

    event, event_id = select_event()
    if event is None:
        return None, None

    return event, event_id


# ==============================
# EVENT OVERVIEWS
# ==============================

def show_all_events(event_filter):
    """
    Displays an overview of upcoming or past events.

    Events are sorted chronologically, with past events displayed
    in reverse order. Users can select an event to view its details.

    Args:
        event_filter (str): The event filter, either "upcoming" or "past".

    Returns:
        None: Returns when the user leaves the event overview.
    """
    while True:
        content = f"Here you can find an overview of all {event_filter} events."

        display_page(
            location="Events",
            title=f"All {event_filter} Events",
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

        columns["Event"].extend(["", "Back"])
        columns["Date"].extend(["", ""])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Event"]) - 1))

        if menu_choice == 0:
            break

        else:
            event_id = event_ids[menu_choice - 1]
            show_event(events[event_id], event_id)
            break

    return


def show_event(event=None, event_id=None, trigger=None):
    """
    Displays detailed information and statistics for an event.

    Shows event details, registered guests, cocktails served per guest,
    and total servings per cocktail.

    For current or future events, provides options to add guests
    and, where permitted, cancel the event.

    Args:
        event (dict, optional): The event record to display.
        event_id (str, optional): The ID of the event.
        trigger (str, optional): Controls the available event actions.

    Returns:
        None: Returns when the user leaves the event details.
    """
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
            content = f"{content}\nCocktails served:   [blue]{cocktail_counter}[/]"

        display_page(location="Events",
                     title="Event Details",
                     content=content
                     )

        guests, guest_ids = get_event_guests(event)
        served_cocktails = []

        # Count served orders for each registered guest.
        for guest_id in guest_ids:
            cocktail_counter = 0
            for order in orders.values():
                if order["event"] == event_id and order["status"] == "served" and order["guest"] == str(guest_id):
                    cocktail_counter += 1
            served_cocktails.append(str(cocktail_counter))

        columns = {
            "Guest": guests,
            "Served cocktails": served_cocktails,
        }

        if columns["Guest"]:
            display_table(columns)

        else:
            panel_content = "[red]No guests have been added to this event.[/]"
            display_panel(panel_content, title="Guest Servings")


        cocktail_names, cocktail_servings = get_event_cocktails(event_id)

        if cocktail_names:
            columns = {
                "Cocktail": cocktail_names,
                "Times served": cocktail_servings,
            }

            display_table(columns)

        else:
            panel_content = "[red]No cocktails have been served at this event yet.[/]"
            display_panel(panel_content, title="Cocktail Servings")

        today = datetime.datetime.now()
        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y")

        if event_date.date() >= today.date():
            columns = {
                "Action": ["Add Guest"]
            }

            if trigger != "current_event":
                columns["Action"].append("Cancel Event")

            columns["Action"].extend(["", "Back"])

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

            if menu_choice == 1:
                _ = add_guest_to_event(event, event_id)
                continue

            elif menu_choice == 2:
                if event["current"]:
                    print_message("You cannot cancel the current event.", "red")
                    print()
                    get_input()
                    continue

                if not confirm_action("cancel", "event"):
                    continue

                from modules.orders import cancel_order
                cancel_order(event_id=event_id)

                update_record("events", event_id, "active", False)
                update_record("events", event_id, "current", False)
                print_message("The event was successfully cancelled.", "green")
                print()
                get_input()
                break

        else:
            get_input()

        break

    return


# ==============================
# EVENT GUEST MANAGEMENT
# ==============================

def get_event_guests(event=None):
    """
    Retrieves and alphabetically sorts the guests assigned to an event.

    Active events include only active guests. Inactive events include
    all registered guests associated with the event.

    Args:
        event (dict, optional): The event whose guests are requested.
            Defaults to the current event.

    Returns:
        tuple: Two lists containing guest names and corresponding
            numerical guest IDs.
    """
    from modules.guests import get_guest_full_name

    if event is None:
        event, _ = get_current_event()

    guests = load_data("guests")
    options = {}

    for guest_id in event["guests"]:
        guest = guests[guest_id]

        if not event["active"]:
            name = get_guest_full_name(guests[guest_id])
            options[int(guest_id)] = name

        else:
            if guest["active"]:
                name = get_guest_full_name(guests[guest_id])
                options[int(guest_id)] = name

    guest_names = []
    guest_ids = []

    for guest_id, guest_name in sorted(options.items(), key=lambda item: item[1].casefold()):
        guest_ids.append(guest_id)
        guest_names.append(guest_name)

    return guest_names, guest_ids


def add_guest_to_event(event=None, event_id=None, guest_id=None):
    """
    Adds a guest to an event and saves the updated guest list.

    When no guest is specified, displays available registered guests
    and provides an option to register a new guest.

    Args:
        event (dict, optional): The event to update.
        event_id (str, optional): The ID of the event.
        guest_id (str, optional): The ID of the guest to add.

    Returns:
        str or None: The selected or added guest ID, or None if
            no event or guest is available.
    """
    from modules.guests import new_guest
    from modules.guests import get_guest_full_name

    if event is None:
        event, event_id = get_current_event()

    if event is None or event_id is None:
        get_input("No event was selected.", color="red")
        return None

    if guest_id is None:
        guests = load_data("guests")
        options = {}

        for guest_id, guest in guests.items():
            if guest_id not in event["guests"] and guest["active"]:
                name = get_guest_full_name(guests[guest_id])
                options[guest_id] = name

        guest_ids = sorted(options, key=lambda option_id: options[option_id].casefold())

        if not guest_ids:
            guest_id = new_guest("new_order")

        else:
            columns = {
                "Name": [options[guest_id] for guest_id in guest_ids]
            }

            columns["Name"].extend(["", "Guest not on list"])

            display_page(
                location="Events",
                title="Add Guests",
                content="Select the guest you want to add to the event."
            )

            print()
            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(guest_ids) + 1))

            if menu_choice == 0:
                guest_id = new_guest("new_order")
            else:
                guest_id = guest_ids[menu_choice - 1]

    if guest_id is None:
        return None

    guest_id = str(guest_id)

    if guest_id in event["guests"]:
        return guest_id

    event["guests"].append(guest_id)
    save_data("events", event, record_id=str(event_id))

    return guest_id


# ==============================
# EVENT COCKTAIL STATISTICS
# ==============================

def get_event_cocktails(event_id=None):
    """
    Retrieves the number of times each cocktail was served at an event.

    Only orders with the status "served" are included.
    Results are sorted alphabetically by cocktail name.

    Args:
        event_id (str, optional): The event ID. Defaults to the current event.

    Returns:
        tuple: Two lists containing cocktail names and their
            corresponding serving counts as strings.
    """
    if event_id is None:
        _, event_id = get_current_event()

    orders = load_data("orders")
    cocktails = load_data("cocktails")
    cocktail_dict = {}

    # Count served orders per cocktail.
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


# ==============================
# EVENT STATUS MANAGEMENT
# ==============================

def update_events():
    """
    Updates event statuses based on the current date.

    Marks today's events as current, keeps future events active,
    and deactivates past events. Open orders belonging to inactive
    or expired events are cancelled.

    Returns:
        None: Returns after all event records have been checked.
    """
    from modules.orders import cancel_order

    events = load_data("events")
    today = datetime.date.today()

    for event_id, event in events.items():
        if not event["active"]:
            cancel_order(event_id=event_id)
            continue

        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y").date()

        current = event_date == today
        active = event_date >= today

        event_update = {
            "id": event_id,
            "name": event["name"],
            "date": event["date"],
            "current": current,
            "active": active,
            "guests": event["guests"]
        }

        if event["current"] != current or event["active"] != active:
            save_data("events", event_update)

            if not active:
                cancel_order(event_id=event_id)

    return