import datetime
from urllib.parse import quote

from modules.cocktail_api import (
    add_cocktail_to_local_db,
    search_cocktails_in_db,
)

from modules.inventory import (
    check_cocktail_availability,
)

from modules.ratings import calculate_average_ratings

from modules.events import get_current_event

from utils.utils import (
    load_data,
    save_data,
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    display_page,
    update_record,
    confirm_action,
)

from utils.constants import (
    INVALID_INPUT,
    PARAM_LUCKY_SHOT,
    PARAM_SEARCH_BY_NAME,
    PARAM_SEARCH_BY_INGREDIENT,
)


def all_available_cocktails():
    while True:
        cocktails = load_data("cocktails")

        content = "Browse all available cocktails and explore their recipes and ingredients."

        display_page(location="Cocktails",
                     title="All available cocktails",
                     content=content
                     )

        columns = {
            "Cocktail": []
        }

        cocktail_ids = []

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):
            if cocktail["active"]:
                cocktail_ids.append(cocktail_id)
                columns["Cocktail"].append(cocktail["name"])

        columns["Cocktail"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))

        if menu_choice == 0:
            break

        cocktail_id = cocktail_ids[menu_choice - 1]

        show_cocktail(cocktail_id)

        continue

    return


def rank_a_cocktail(guest_id=None, trigger=None):
    current_event, current_event_id = get_current_event()
    if current_event is None:
        return

    cocktail_id = None
    today = datetime.date.today().strftime("%d-%m-%Y")

    while True:
        rankings = load_data("rankings")
        content = "Here you can rank the cocktails you drank."

        display_page(location="Cocktails",
                     title="Rank a cocktail",
                     content=content
                     )

        if guest_id is None:
            from modules.guests import select_guest
            guest_id = select_guest("rank_a_cocktail")
            if guest_id is None:
                break
            continue

        if cocktail_id is None:
            cocktail_id = select_cocktail(trigger="rank_a_cocktail")
            if cocktail_id is None:
                break
            continue

        while True:
            rating = float(get_input("How would you rate this cocktail (1–10)? ", float))

            if 1 <= rating <= 10:
                break

            else:
                print_message(INVALID_INPUT)
                continue

        update_id = str(len(rankings) + 1)
        for ranking_id, ranking in rankings.items():
            if ranking["guest"] == guest_id and ranking["cocktail"] == cocktail_id:
                update_id = ranking_id
                break


        update_ranking = {
            "id": update_id,
            "cocktail": cocktail_id,
            "guest": guest_id,
            "date": today,
            "rating": rating
        }

        save_data("rankings", update_ranking)

        print()
        print_message("The cocktail was rated successfully.", "green")


        columns = {
            "Action": ["Rank another cocktail", "View ranking", "", "Back"]
        }

        print()
        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            if trigger is None:
                guest_id = None
            cocktail_id = None
            continue

        elif menu_choice == 2:
            show_cocktail_ranking()
            break

        break

    return


def show_cocktail_ranking():
    while True:
        rankings = load_data("rankings")
        cocktails = load_data("cocktails")

        content = "Discover the all-time favorite cocktails, ranked by their average rating."

        display_page(location="Cocktails",
                     title="All-time favorites",
                     content=content
                     )

        average_ratings = calculate_average_ratings(rankings.values())

        columns = {
            "Place": [],
            "Cocktail": [],
            "Rating": [],
            "Votes": []
        }

        for place, (cocktail_id, rating) in enumerate(sorted(average_ratings.items(), key=lambda item: item[1]["average"], reverse=True),start=1):
            columns["Place"].append(place)
            columns["Cocktail"].append(cocktails[cocktail_id]["name"])
            columns["Rating"].append(rating["average"])
            columns["Votes"].append(rating["votes"])

        display_table(columns)

        columns = {
            "Action": ["Rank a cocktail", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            rank_a_cocktail()
            continue

        break

    return




def select_cocktail(trigger=None):
    while True:
        cocktails = load_data("cocktails")

        if trigger == "new_order":
            content = "Select the cocktail you want to order."

            display_page(
                location="Cocktails",
                title="Available Cocktails",
                content=content
            )
        else:
            print_message("Select a cocktail:")

        cocktail_ids = []

        columns = {
            "Cocktail": []
        }

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda entry: entry[1]["name"].casefold()):
            if not cocktail["active"]:
                continue

            if trigger == "new_order":
                if check_cocktail_availability(cocktail_id):
                    continue

            cocktail_ids.append(cocktail_id)
            columns["Cocktail"].append(cocktail["name"])

        search_option = 0

        if trigger == "new_order":
            search_option = len(cocktail_ids) + 1
            columns["Cocktail"].extend(["Cocktail not on list", "", "Back"])
            valid_choices = range(0, search_option + 1)

        else:
            columns["Cocktail"].extend(["", "Back"])
            valid_choices = range(0, len(cocktail_ids) + 1)

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(valid_choices)

        if menu_choice == 0:
            return None

        if trigger == "new_order" and menu_choice == search_option:
            cocktail_id = search_cocktail("name", for_order=True)

            if cocktail_id is None:
                continue

            if check_cocktail_availability(cocktail_id):
                get_input("Cocktail cannot be ordered because not all ingredients are available.", color="red")
                continue

            return cocktail_id

        return cocktail_ids[menu_choice - 1]



def show_cocktail(cocktail_id, trigger=None):
    cocktails = load_data("cocktails")

    cocktail = cocktails[cocktail_id]
    cocktail_name = cocktail["name"]
    ingredients = cocktail["ingredients"]
    instructions = cocktail["instructions"]

    page_content = f"Ingredients and instructions for a [blue]{cocktail_name}[/].\n\n"
    page_content += "Ingredients marked [red]red[/] are not available."

    display_page(
        location="Cocktails",
        title=cocktail_name,
        content=page_content
    )

    low_on_stock = check_cocktail_availability(cocktail_id, for_existing_order=trigger == "process_order")
    inventory = load_data("inventory")

    columns = {
        "Ingredient": [],
        "Measure": []
    }

    for ingredient_id, measure in ingredients.items():
        ingredient_name = (inventory[ingredient_id]["name"] if ingredient_id in inventory else f"Unknown ingredient ({ingredient_id})")

        if ingredient_id in low_on_stock:
            ingredient_name = f"[red]{ingredient_name}[/]"

        columns["Ingredient"].append(ingredient_name)
        columns["Measure"].append(measure if measure is not None else "-")

    display_table(columns)

    panel_content = "- " + instructions.replace(". ", ".\n- ")
    display_panel(panel_content, title="instructions")

    # Only existing inventory items can be added to the shopping list.
    shopping_list_ids = [
        ingredient_id
        for ingredient_id in low_on_stock
        if ingredient_id in inventory
    ]

    if trigger != "process_order":
        while True:
            columns = {
                "Action": ["Order cocktail", "Statistics", "Deactivate cocktail"]
            }

            if shopping_list_ids:
                columns["Action"].append("Add unavailable ingredients to shopping list")

            columns["Action"].extend(["", "Back"])

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

            if menu_choice == 1:
                if low_on_stock:
                    get_input(
                        "Cocktail cannot be ordered because not all ingredients are available.",
                        color="red"
                    )
                    break

                from modules.orders import new_order
                new_order(cocktail_id)

            elif menu_choice == 2:
                show_cocktail_statistics(cocktail_id)
                continue

            elif menu_choice == 3:
                deactivate_cocktail(cocktail_id)

            elif menu_choice == 4 and shopping_list_ids:
                for item_id in shopping_list_ids:
                    update_record("inventory", item_id, "shopping_list", True)

                print_message(
                    "Ingredients successfully added to shopping list.\n",
                    "green"
                )
                get_input()

            break

    return



def search_cocktail(search_method="", for_order=False):
    if search_method == "lucky_shot":
        params = PARAM_LUCKY_SHOT
        cocktail_id = search_cocktails_in_db(params, "lucky_shot")

        if cocktail_id is None:
            return None

    else:
        content = f"Here you can search cocktails by {search_method}."

        display_page(
            location="Cocktails",
            title=f"Search by {search_method}",
            content=content
        )

        cocktails = None

        if search_method == "name":
            while True:
                name = get_input("What is the name of the cocktail you would like to search for? ").strip()

                if name:
                    break

                print_message(INVALID_INPUT)

            params = PARAM_SEARCH_BY_NAME + quote(name, safe="")
            cocktails = search_cocktails_in_db(params, "name")

        elif search_method == "ingredient":
            print_message("The following ingredients are available in the inventory.")

            inventory = load_data("inventory")

            columns = {
                "Ingredient": []
            }

            for item in inventory.values():
                if item["quantity"] > 0:
                    columns["Ingredient"].append(item["name"])

            columns["Ingredient"].extend(["", "Back"])

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Ingredient"]) - 1))

            if menu_choice == 0:
                return None

            ingredient = columns["Ingredient"][menu_choice - 1]
            params = PARAM_SEARCH_BY_INGREDIENT + quote(ingredient, safe="")
            cocktails = search_cocktails_in_db(params, "ingredient")

        if not isinstance(cocktails, dict) or not cocktails:
            return None

        content = "The following cocktails were found:"

        display_page(
            location="Cocktails",
            title=f"Search by {search_method}",
            content=content
        )

        sorted_cocktails = sorted(cocktails.items(), key=lambda entry: entry[0].casefold())

        columns = {
            "Cocktail": [name for name, _ in sorted_cocktails]
        }

        columns["Cocktail"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(sorted_cocktails) + 1))

        if menu_choice == 0:
            return None

        cocktail_id = sorted_cocktails[menu_choice - 1][1]

    if not add_cocktail_to_local_db(cocktail_id):
        return None

    if for_order:
        return cocktail_id

    show_cocktail(cocktail_id)

    return None



def deactivate_cocktail(cocktail_id):
    if not confirm_action("deactivate", "cocktail"):
        return

    from modules.orders import cancel_order
    cancel_order(cocktail_id=cocktail_id)

    update_record("cocktails", cocktail_id, "active", False)

    print_message("Cocktail successfully deactivated.", "green")
    print()
    get_input()


def show_cocktail_statistics(cocktail_id):
    from modules.guests import get_guest_full_name

    cocktails = load_data("cocktails")
    cocktail = cocktails[cocktail_id]

    orders = load_data("orders")
    rankings = load_data("rankings")
    guests = load_data("guests")
    events = load_data("events")

    content = f"Statistics for cocktail [blue]{cocktail["name"]}[/]."

    display_page(location="Cocktails",
                 title=f"Statistics",
                 content=content
                 )

    times_served = 0
    for order in orders.values():
        if order["cocktail"] == cocktail_id and order["status"] == "served":
            times_served += 1

    panel_content = f"Times served:     {times_served}\n"

    rating = calculate_average_ratings(rankings.values()).get(cocktail_id)

    if rating is not None:
        panel_content += f"Average rating:    {rating['average']}\n"
        panel_content += f"Number of votes:  {rating['votes']}"

    display_panel(panel_content, title="Overview")

    columns = {
        "Guest": [],
        "Times served": [],
    }

    order_counts = {}

    for order in orders.values():
        if order["cocktail"] == cocktail_id and order["status"] == "served":
            guest_id = order["guest"]
            order_counts[guest_id] = order_counts.get(guest_id, 0) + 1

    for guest_id, count in sorted(order_counts.items(), key=lambda entry: entry[1], reverse=True):
        name = get_guest_full_name(guests[guest_id])

        columns["Guest"].append(name)
        columns["Times served"].append(count)

    if columns["Guest"]:
        display_table(columns)

    else:
        panel_content = f"[red]Cocktail is never served to a guest.[/]"
        display_panel(panel_content, title="Served")


    columns = {
        "Guest": [],
        "Date": [],
        "Rating": [],
    }

    for ranking in sorted(rankings.values(), key=lambda entry: entry["rating"], reverse=True):
        if ranking["cocktail"] == cocktail_id:
            guest_id = ranking["guest"]
            name = get_guest_full_name(guests[guest_id])

            columns["Guest"].append(name)
            columns["Date"].append(ranking["date"])
            columns["Rating"].append(ranking["rating"])

    if columns["Guest"]:
        display_table(columns)

    else:
        panel_content = f"[red]Cocktail is never rated by a guest.[/]"
        display_panel(panel_content, title="Rated")

    columns = {
        "Event": [],
        "Date": [],
        "Times ordered": [],
    }

    order_counts = {}

    for order in orders.values():
        if order["cocktail"] == cocktail_id and order["status"] == "served":
            event_id = order["event"]
            order_counts[event_id] = order_counts.get(event_id, 0) + 1

    for event_id, count in sorted(order_counts.items(), key=lambda entry: entry[1], reverse=True):
        columns["Event"].append(events[event_id]["name"])
        columns["Date"].append(events[event_id]["date"])
        columns["Times ordered"].append(count)

    if columns["Event"]:
        display_table(columns)

    else:
        panel_content = f"[red]Cocktail is never served on an event.[/]"
        display_panel(panel_content, title="Event")


    get_input()
    return


