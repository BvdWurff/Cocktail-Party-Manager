# ==============================
# FUNCTION IMPORTS
# ==============================

from modules.cocktails import (
    all_available_cocktails,
    rank_a_cocktail,
    show_cocktail_ranking,
    search_cocktail,
)

from modules.events import (
    new_event,
    show_event,
    show_all_events,
)

from modules.guests import show_all_guests

from modules.inventory import (
    show_inventory,
    add_low_stock_items_to_shopping_list,
)

from modules.orders import (
    new_order,
    get_next_order,
    all_open_orders,
    process_order,
)

from modules.unit_converter import unit_converter

from utils.demo_data import (
    load_demo_data,
    reset_application_data,
)

from utils import app_state

from utils.utils import (
    get_menu_choice,
    display_table,
    display_page,
    print_message,
)


# ==============================
# MAIN MENU
# ==============================


def main_menu():
    """
    Displays the main menu and handles navigation to the different
    sections of the Cocktail Party Manager.
    """

    while True:
        content = "Discover cocktails, take orders, manage events, keep track of your inventory, or explore the available features.\n\nSelect an option below to get started."

        if app_state.DEMO_MODE:
            content += "\n\n**[i]The app is currently running in [blue b]Demo mode[/].**"

        display_page(location="Cocktail Party Manager",
                     title="Main Menu",
                     content=content,
                     )

        columns = {
            "Menu": ["Cocktails", "Orders", "Events", "Inventory", "Guests", "Unit Converter"]
        }

        if app_state.DEMO_MODE and app_state.SHOW_DEMO_MENU:
            columns["Menu"].extend(["Disable Demo Mode"])

        elif not app_state.DEMO_MODE and app_state.SHOW_DEMO_MENU:
            columns["Menu"].append("Enable Demo Mode")

        columns["Menu"].extend(["", "Exit"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Menu"]) - 1))

        if menu_choice == 1:
            cocktail_menu()

        elif menu_choice == 2:
            orders_menu()

        elif menu_choice == 3:
            events_menu()

        elif menu_choice == 4:
            inventory_menu()

        elif menu_choice == 5:
            show_all_guests()

        elif menu_choice == 6:
            unit_converter()

        elif menu_choice == 7:
            if not app_state.DEMO_MODE:
                load_demo_data()

            if app_state.DEMO_MODE:
                print_message("[i][red]Warning:[/] Demo data will be reset when you disable demo mode.[/]\n")

                print_message("Are you sure you want to disable demo mode?\n", "bright_white")

                columns = {
                    "Action": ["Yes", "No"]
                }

                display_table(columns, auto_number=True)

                menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

                if menu_choice == 1:
                    reset_application_data(trigger="demo_exit")

            app_state.DEMO_MODE = not app_state.DEMO_MODE

        else:
            break

    return


# ==============================
# COCKTAIL MENUS
# ==============================

def cocktail_menu():
    """
    Displays the cocktail menu and provides access to the local cocktail
    collection, API searches, ratings, and all-time favorites.
    """
    while True:
        content = "Discover your favorite cocktails, explore recipes, and rate the drinks you've tried."

        display_page(location="Cocktail Party Manager",
                     title="Cocktails",
                     content=content
                     )

        columns = {
            "Action": ["All Available Cocktails", "Find New Cocktails", "Rate a Cocktail", "All-Time Favorites", "", "Back"]
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


def find_new_cocktails_menu():
    """
    Displays the cocktail search menu and directs the user to the selected
    search method using TheCocktailDB API.
    """
    while True:
        content = "Search for new cocktails by name or ingredient, or discover a random cocktail."

        display_page(location="Cocktails",
                     title="Find Cocktails",
                     content=content
                     )

        columns = {
            "Action": ["Search by Name", "Search by Ingredient", "Lucky 'Shot'", "", "Back"]
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


# ==============================
# ORDER MENU
# ==============================

def orders_menu():
    """
    Displays the orders menu and allows users to create new orders,
    process the next open order, or select an existing open order.
    """
    while True:
        content = "Create new cocktail orders or manage existing orders that are waiting to be served."

        display_page(location="Cocktail Party Manager",
                     title="Orders",
                     content=content
                     )

        columns = {
            "Action": ["New Order", "Next Open Order", "All Open Orders", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            new_order()

        elif menu_choice == 2:
            order_id, _ = get_next_order()
            if order_id is None:
                continue

            process_order(order_id)

        elif menu_choice == 3:
            order_id, order = all_open_orders()
            if order_id is None:
                continue

            process_order(order_id)

        else:
            break

    return


# ==============================
# EVENT MENU
# ==============================

def events_menu():
    """
    Displays the events menu and provides options to create an event,
    view the current event, or browse upcoming and past events.
    """
    while True:
        content = "Create new events, manage the current event, or explore upcoming and past events."

        display_page(location="Cocktail Party Manager",
                     title="Events",
                     content=content
                     )

        columns = {
            "Action": ["New Event", "Current Event", "Upcoming Events", "Past Events", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            new_event()

        elif menu_choice == 2:
            show_event(trigger="current_event")

        elif menu_choice == 3:
            show_all_events("upcoming")

        elif menu_choice == 4:
            show_all_events("past")

        else:
            break

    return


# ==============================
# INVENTORY MENU
# ==============================

def inventory_menu():
    """
    Displays the inventory menu and provides access to inventory
    overviews, low-stock items, and the shopping list.
    """
    while True:
        content = "View and manage your ingredient inventory, monitor low-stock items, and update your shopping list."

        display_page(location="Cocktail Party Manager",
                     title="Inventory",
                     content=content
                     )

        columns = {
            "Action": ["Full Inventory", "Items Below Minimum Quantity", "Add Low-Stock Items to Shopping List", "Shopping List", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            show_inventory(trigger="full_inventory")

        elif menu_choice == 2:
            show_inventory(trigger="below_min_quantity")

        elif menu_choice == 3:
            add_low_stock_items_to_shopping_list()

        elif menu_choice == 4:
            show_inventory(trigger="shopping_list")

        else:
            break

    return
