from datetime import datetime, date

from utils.utils import (
    display_table,
    load_data,
    save_data,
    get_input,
    print_message,
    get_menu_choice,
    display_page,
    update_record,
    display_panel,
    confirm_action,
)

from modules.events import (
    get_current_event,
    add_guest_to_event,
    get_event_guests,
)

from modules.cocktails import rank_a_cocktail

from modules.ratings import calculate_average_ratings

from utils.constants import (
    INVALID_INPUT,
)


def new_guest(trigger=""):
    created_guests_ids = []
    while True:
        guests = load_data("guests")
        surname = ""

        while True:
            content = f"""Here you can register new guests.
        
Type [red]Stop[/] to exit the registration process."""

            confirmation_choice = ""

            display_page(location="Guests",
                         title="Register guest",
                         content=content
                         )

            first_name = get_input("What is the first name of the guest? ").strip()

            if not first_name:
                print_message(INVALID_INPUT)
                continue

            if first_name.lower() == "stop":
                print()
                get_input("Press [blue]Enter[/] to exit the registration process.")
                return None

            surname = get_input("What is the surname of the guest? ").strip()

            if not surname:
                print_message(INVALID_INPUT)
                continue

            if surname.lower() == "stop":
                print()
                get_input("Press [blue]Enter[/] to exit the registration process.")
                return None

            duplicate = False

            for guest in guests.values():
                if guest["first_name"].lower() == first_name.lower() and guest["surname"].lower() == surname.lower():
                    duplicate = True
                    print()
                    print_message(f"A guest named {first_name} {surname} already exists.", "red")

                    while True:
                        print()
                        confirmation_choice = get_input("Are you sure you want to create another guest with this name? (Yes/No) ").strip().casefold()

                        if confirmation_choice not in ("yes", "no"):
                            print_message(INVALID_INPUT, "red")
                            continue

                        break


            if confirmation_choice == "yes" or not duplicate:
                break

            continue

        guest = {
            "id": str(len(guests) + 1),
            "first_name": first_name,
            "surname": surname,
            "active": True
        }

        save_data("guests", guest)
        print()
        print_message("Guest successfully registered.", "green")

        if trigger == "new_order":
            print()
            get_input("Press [blue]Enter[/] to return to the order process.")

            return guest["id"]

        else:
            created_guests_ids.append(guest["id"])

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

        display_page(location="Guests",
                     title="Available guests",
                     content=content
                     )

    else:
        print_message("Select a guest:")

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


def show_all_guests():
    while True:

        guests = load_data("guests")

        content = f"A list off all the active guests in the cocktail party manager app."

        display_page(location="Guests",
                     title="Active guests",
                     content=content
                     )

        people_ids = []

        columns = {
            "Name": []
        }

        for guest_id, guest in sorted(guests.items(), key=lambda entry: entry[1]["first_name"].casefold()):
            if guest["active"]:
                people_ids.append(guest_id)
                name = get_guest_full_name(guests[guest_id])
                columns["Name"].append(name)

        columns["Name"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Name"]) - 1))
        if menu_choice == 0:
            break

        else:
            guest_id = people_ids[menu_choice - 1]
            show_guest(guest_id)

    return


def get_guest_activity(guest_id):
    """Retrieves the events, served orders, and rankings for a guest."""
    orders_list = [order for order in load_data("orders").values()
        if order["guest"] == guest_id and order["status"] == "served"
    ]

    events_list = [{"id": event_id, **event} for event_id, event in load_data("events").items()
        if guest_id in event["guests"]
        and datetime.strptime(event["date"], "%d-%m-%Y").date() <= date.today()
        and (not event["active"] or event["current"])
    ]

    rankings_list = [ranking for ranking in load_data("rankings").values()
        if ranking["guest"] == guest_id
    ]

    return events_list, orders_list, rankings_list


def display_guest_summary(name, events_list, orders_list, rankings_list):
    """Displays the general activity statistics for a guest."""
    content = f"""Here you can find all information about [blue]{name}[/].\n
Events attended:    [blue]{len(events_list)}[/]
Cocktails served:   [blue]{len(orders_list)}[/]
Ranking votes:      [blue]{len(rankings_list)}[/]"""

    display_page(
        location="Guests",
        title=name,
        content=content
    )


def display_guest_events(name, events_list, orders_list):
    """Displays the events attended by a guest."""
    if not events_list:
        display_panel(
            f"[red]{name} did not attend any events.[/]",
            title="Events"
        )
        return

    columns = {
        "Event": [],
        "Date": [],
        "Cocktails": []
    }

    for event in events_list:
        cocktail_counter = sum(1 for order in orders_list if order["event"] == event["id"])

        event_name = event["name"]
        event_date = event["date"]
        cocktail_count = str(cocktail_counter)

        if event["current"]:
            event_name = f"[blue]{event_name}[/]"
            event_date = f"[blue]{event_date}[/]"
            cocktail_count = f"[blue]{cocktail_count}[/]"

        columns["Event"].append(event_name)
        columns["Date"].append(event_date)
        columns["Cocktails"].append(cocktail_count)

    display_table(columns)


def display_guest_cocktails(name, orders_list, cocktails):
    """Displays how often each cocktail was served to a guest."""
    if not orders_list:
        display_panel(f"[red]No cocktails were served to {name}.[/]", title="Serving")
        return

    cocktail_counts = {}

    for order in orders_list:
        cocktail_id = order["cocktail"]
        cocktail_counts[cocktail_id] = cocktail_counts.get(cocktail_id, 0) + 1

    columns = {
        "Cocktail": [],
        "Served": []
    }

    for cocktail_id, count in sorted(cocktail_counts.items(), key=lambda item: item[1], reverse=True):
        columns["Cocktail"].append(cocktails[cocktail_id]["name"])
        columns["Served"].append(count)

    display_table(columns)


def display_guest_rankings(name, rankings_list, cocktails):
    """Displays the average cocktail ratings submitted by a guest."""
    if not rankings_list:
        display_panel(f"[red]{name} did not rank any cocktails.[/]", title="Ranking")
        return

    average_ratings = calculate_average_ratings(rankings_list)

    columns = {
        "Place": [],
        "Cocktail": [],
        "Rating": []
    }

    for place, (cocktail_id, rating) in enumerate(sorted(average_ratings.items(), key=lambda item: item[1]["average"], reverse=True), start=1):
        columns["Place"].append(place)
        columns["Cocktail"].append(cocktails[cocktail_id]["name"])
        columns["Rating"].append(rating["average"])

    display_table(columns)


def add_guest_to_current_event(guest_id, name):
    """Adds a guest to the current event if not already attending."""
    event, event_id = get_current_event()

    if event is None or event_id is None:
        print_message("No current event.", "red")
        print()
        get_input()
        return

    guests = event["guests"]

    if guests is None:
        print_message("The event has no guests.", "red")
        print()
        get_input()
        return

    if guest_id in guests:
        print_message(f"{name} is already added to the current event.", "red")
        print()
        get_input()
        return

    add_guest_to_event(event=event, event_id=event_id, guest_id=guest_id)

    print_message(f"{name} successfully added to the current event.", "green")
    print()
    get_input()


def show_guest(guest_id):
    """Displays guest information and handles the available guest actions."""
    guest_id = str(guest_id)
    guests = load_data("guests")
    name = get_guest_full_name(guests[guest_id])

    while True:
        cocktails = load_data("cocktails")

        events_list, orders_list, rankings_list = get_guest_activity(guest_id)

        display_guest_summary(name, events_list, orders_list, rankings_list)
        display_guest_events(name, events_list, orders_list)
        display_guest_cocktails(name, orders_list, cocktails)
        display_guest_rankings(name, rankings_list, cocktails)

        columns = {
            "Action": ["Rank a cocktail", "Add to current event", "Order a cocktail", "Show orders", "Deactivate guest", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            rank_a_cocktail(guest_id=guest_id, trigger="show_guest")
            continue

        elif menu_choice == 2:
            add_guest_to_current_event(guest_id, name)
            continue


        elif menu_choice == 3:
            selected_guest_id = add_guest_to_event(guest_id=guest_id)

            if selected_guest_id is not None:
                from modules.orders import new_order

                new_order(guest_id=selected_guest_id)

            continue

        elif menu_choice == 4:
            from modules.orders import show_guest_orders
            show_guest_orders(guest_id)
            continue

        elif menu_choice == 5:
            deactivate_guest(guest_id)


        break

    return


def deactivate_guest(guest_id):
    if not confirm_action("deactivate", "guest"):
        return

    from modules.orders import cancel_order
    cancel_order(guest_id=guest_id)

    update_record("guests", guest_id, "active", False)

    print_message("Guest successfully deactivated.", "green")
    print()
    get_input()


def get_guest_full_name(guest):
    return f"{guest['first_name']} {guest['surname']}"





