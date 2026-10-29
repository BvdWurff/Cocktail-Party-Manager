# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.orders import (
    new_order,
    get_next_order,
    all_open_orders,
    process_order,
)

from modules.persons import new_person
from modules.events import (
    new_event,
    show_event,
    show_all_events,
)

from utils.utils import (
    get_menu_choice,
    display_table,
    display_page,
    unit_converter,
    get_input,
    print_message,
)

from modules.cocktails import (
    all_available_cocktails,
    rank_a_cocktail,
    show_cocktail_ranking,
    search_cocktail,
)


def main_menu():
    while True:
        content = "Discover cocktails, take orders, manage events, keep track of your inventory or see statistics.\n\nSelect an option below to get started."

        display_page(location="Cocktail Party Manager",
                     title="Main menu",
                     content=content
                     )

        columns = {
            "Menu": ["Cocktails", "Orders", "Events", "Admin", "Statistics", "", "Exit"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Menu"]) - 1))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        elif menu_choice == 4:
            admin_menu()

        elif menu_choice == 5:
            stats_menu()

        else:
            break

    return


def cocktail_menu():
    while True:
        content = "Here you can find your favorite cocktails and get recipes."

        display_page(location="Cocktail Party Manager",
                     title="Cocktails",
                     content=content
                     )

        columns = {
            "Action": ["All available cocktails", "Find new cocktails", "Rank a cocktail", "All-time favorites", "", "Back to main menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            all_available_cocktails()

        elif menu_choice == 2:
            find_new_cocktails_menu()

        elif menu_choice == 3:
            rank_a_cocktail()

        elif menu_choice == 4:
            show_cocktail_ranking()

        else:
            break

    return


def orders_menu():
    while True:
        content = "Here you can manage your orders."

        display_page(location="Cocktail Party Manager",
                     title="Orders",
                     content=content
                     )

        columns = {
            "Action": ["New order", "Next open order", "All open orders", "", "Back to main menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            new_order()

        elif menu_choice == 2:
            order_id, order = get_next_order()
            if order_id is None:
                continue

            process_order(order_id, order)

        elif menu_choice == 3:
            order_id, order = all_open_orders()
            if order_id is None:
                continue

            process_order(order_id, order)

        else:
            break

    return

def events_menu():
    while True:
        content = "Here you can manage your events."

        display_page(location="Cocktail Party Manager",
                     title="Events",
                     content=content
                     )

        columns = {
            "Action": ["New event", "Current event", "Upcoming events", "Past events",  "", "Back to main menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            new_event()

        elif menu_choice == 2:
            show_event()

        elif menu_choice == 3:
            show_all_events("upcoming")

        elif menu_choice == 4:
            show_all_events("past")

        else:
            break

    return


def admin_menu():
    while True:
        content = "Here you can manage your settings and data."

        display_page(location="Cocktail Party Manager",
                     title="Admin",
                     content=content
                     )

        columns = {
            "Action": ["Inventory", "Guests", "Events", "Cocktails", "Unit convertor", "Shopping lists", "", "Back to main menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            pass

        elif menu_choice == 2:
            new_person(trigger="admin_menu")

        elif menu_choice == 3:
            pass

        elif menu_choice == 4:
            pass

        elif menu_choice == 5:
            unit_converter()

        elif menu_choice == 6:
            pass

        else:
            break

    return


def stats_menu():
    while True:
        content = "Here you can look into statistics"

        display_page(location="Cocktail Party Manager",
                     title="Statistics",
                     content=content
                     )

        columns = {
            "Action": ["Guests", "Events", "Cocktails", "", "Back to main menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            pass

        elif menu_choice == 2:
            pass

        elif menu_choice == 3:
            pass

        else:
            break

    return


def find_new_cocktails_menu():
    while True:
        content = "Here you can search for new cocktails and get recipes."

        display_page(location="Cocktails",
                     title="Find cocktails",
                     content=content
                     )

        columns = {
            "Action": ["Search by name", "Search by ingredient", "Lucky 'shot'", "", "Back to cocktail menu"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            search_cocktail("name")

        elif menu_choice == 2:
            search_cocktail("ingredient")

        elif menu_choice == 3:
            search_cocktail("lucky_shot")

        else:
            break

    return