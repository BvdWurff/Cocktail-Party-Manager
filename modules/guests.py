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
)

from modules.events import (
    get_current_event,
    add_guest_to_event,
    get_event_guests,
)

from modules.cocktails import rank_a_cocktail

from utils.constants import (
    INVALID_INPUT,
)


def new_guest(trigger=""):
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

            guests = load_data("guests")
            duplicate = False

            for guest in guests.values():
                if guest["first_name"].lower() == first_name.lower() and guest["surname"].lower() == surname.lower():
                    duplicate = True
                    print()
                    print_message(f"A guest named {first_name} {surname} already exists.", "red")

                    while True:
                        print()
                        confirmation_choice = get_input("Are you sure you want to create another guest with this name? (Yes/No) ").lower()

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
                name = f"{guest["first_name"]} {guest["surname"]}"
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


def show_guest(guest_id):
    guests = load_data("guests")
    guest = guests[guest_id]
    name = f"{guest["first_name"]} {guest["surname"]}"

    while True:
        cocktails = load_data("cocktails")
        orders = load_data("orders")
        order_counter = 0
        orders_list = []

        for order_id, order in orders.items():
            if guest_id == order["guest"] and order["status"] == "served":
                orders_list.append({"id": order_id, **order})
                order_counter += 1

        events = load_data("events")
        event_counter = 0
        events_list = []

        for event_id, event in events.items():
            if guest_id in event["guests"] and (not event["active"] or event["current"]):
                events_list.append({"id": event_id, **event})
                event_counter += 1

        rankings = load_data("rankings")
        ranking_counter = 0
        rankings_list = []

        for ranking_id, ranking in rankings.items():
            if guest_id == ranking["guest"]:
                rankings_list.append({"id": ranking_id, **ranking})
                ranking_counter += 1

        content = f"""Here you can find all information about [blue]{name}[/].\n
Events attended:     [blue]{event_counter}[/]
Cocktails served:   [blue]{order_counter}[/]
Ranking votes:       [blue]{ranking_counter}[/]"""

        display_page(location="Guests",
                     title=name,
                     content=content
                     )

        if events_list:

            columns = {
                "Event": [],
                "Date": [],
                "Cocktails": []
            }

            for event in events_list:
                cocktail_counter = 0
                for order in orders_list:
                    if order["event"] == event["id"]:
                        cocktail_counter += 1

                if event["current"]:
                    columns["Event"].append(f"[blue]{event["name"]}[/]")
                    columns["Date"].append(f"[blue]{event["date"]}[/]")
                    columns["Cocktails"].append(f"[blue]{cocktail_counter}[/]")
                else:
                    columns["Event"].append(event["name"])
                    columns["Date"].append(event["date"])
                    columns["Cocktails"].append(cocktail_counter)

            display_table(columns)

        else:
            panel_content = f"[red]{name} did not attend any events.[/]"
            display_panel(panel_content, title="Events")

        if orders_list:
            columns = {
                "Cocktail": [],
                "Served": [],
            }

            cocktails_list = {}

            for order in orders_list:
                cocktail_id = order["cocktail"]
                cocktails_list[cocktail_id] = cocktails_list.get(cocktail_id, 0) + 1

            for cocktail_id, counter in sorted(cocktails_list.items(), reverse=True, key=lambda item: item[1]):
                columns["Cocktail"].append(cocktails[cocktail_id]["name"])
                columns["Served"].append(counter)

            display_table(columns)

        else:
            panel_content = f"[red]No cocktails were serverd to {name}.[/]"
            display_panel(panel_content, title="Serving")


        if rankings_list:
            total_scores = {}
            number_of_ratings = {}
            average_scores = {}

            for ranking in rankings_list:
                cocktail = cocktails[ranking["cocktail"]]["name"]
                total_scores[cocktail] = total_scores.get(cocktail, 0) + ranking["score"]
                number_of_ratings[cocktail] = number_of_ratings.get(cocktail, 0) + 1

            for cocktail, score in total_scores.items():
                number = number_of_ratings[cocktail]
                average_score = round(score / number, 1)
                average_scores[cocktail] = average_score

            columns = {
                "Place": [],
                "Cocktail": [],
                "Score": [],
            }

            for place, (cocktail, score) in enumerate(
                    sorted(average_scores.items(), key=lambda item: item[1], reverse=True), start=1):
                columns["Place"].append(place)
                columns["Cocktail"].append(cocktail)
                columns["Score"].append(score)

            display_table(columns)

        else:
            panel_content = f"[red]{name} did not rank any cocktails.[/]"
            display_panel(panel_content, title="Ranking")

        columns = {
            "Action": ["Rank a cocktail", "Add to current event", "Order a cocktail", "Show orders", "Deactivate guest", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            rank_a_cocktail(guest_id=guest_id, trigger="show_guest")
            continue

        elif menu_choice == 2:
            event, event_id = get_current_event()
            if event is None:
                print_message("No current event.", "red")
                print()
                get_input()
                continue

            guests = event["guests"]
            if guests is None:
                print_message("The event has no guests.", "red")
                print()
                get_input()
                continue

            if guest_id in guests:
                print_message(f"{name} is already added to the current event.", "red")
                print()
                get_input()
                continue

            guests.append(guest_id)

            update_record("events", event_id, "guests", guests)

            print_message(f"{name} successfully added to the current event.", "green")
            print()
            get_input()

            continue

        elif menu_choice == 3:
            add_guest_to_event(guest_id=guest_id)
            from modules.orders import new_order
            new_order(guest_id=guest_id)
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
    from modules.orders import cancel_order
    cancel_order(guest_id=guest_id)

    update_record("guests", guest_id, "active", False)

    print_message("Guest successfully deactivated.", "green")
    print()
    get_input()





