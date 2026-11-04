import datetime

from modules.cocktail_api import (
    add_cocktail_to_local_db,
    search_cocktails_in_db,
)

from modules.inventory import (
    check_cocktail_availability,
)

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
            from modules.persons import select_guest
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
            score = float(get_input("How would you rate this cocktail (1–10)? ", float))

            if 1 <= score <= 10:
                break

            else:
                print_message(INVALID_INPUT)
                continue

        update_id = str(len(rankings) + 1)
        for ranking_id, ranking in rankings.items():
            if ranking["person"] == guest_id and ranking["cocktail"] == cocktail_id:
                update_id = ranking_id
                break


        update_ranking = {
            "id": update_id,
            "cocktail": cocktail_id,
            "person": guest_id,
            "date": today,
            "score": score
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

        total_scores = {}
        number_of_ratings = {}
        average_scores = {}

        for ranking in rankings.values():
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
            "Votes": []
        }

        for place, (cocktail, score) in enumerate(sorted(average_scores.items(), key=lambda item: item[1], reverse=True), start=1):
            columns["Place"].append(place)
            columns["Cocktail"].append(cocktail)
            columns["Score"].append(score)
            columns["Votes"].append(number_of_ratings[cocktail])

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



def select_cocktail(trigger=""):
    while True:
        cocktails = load_data("cocktails")

        if trigger == "new_order":


            content = f"Select the cocktail you want to order."

            display_page(location="Cocktails",
                         title="Available Cocktails",
                         content=content
                         )
        else:
            print_message("Select a cocktail:")

        cocktail_ids = []

        columns = {
            "Cocktail": []
        }

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):

            if cocktail["active"]:
                if trigger == "new_order":
                    low_on_stock = check_cocktail_availability(cocktail_id)
                    if not low_on_stock:
                        cocktail_ids.append(cocktail_id)
                        columns["Cocktail"].append(cocktail["name"])

                else:
                    cocktail_ids.append(cocktail_id)
                    columns["Cocktail"].append(cocktail["name"])

        if trigger == "new_order":
            columns["Cocktail"].extend(["", "Cocktail not on list"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))
        cocktail_id = cocktail_ids[menu_choice - 1]

        if menu_choice == 0:
            search_cocktail("name")

        break

    return cocktail_id


def show_cocktail(cocktail_id):
    cocktails = load_data("cocktails")
    inventory = load_data("inventory")

    cocktail =  cocktails[cocktail_id]
    cocktail_name = cocktail["name"]
    ingredients = cocktail["ingredients"]
    instructions = cocktail["instructions"]

    page_content = f"Ingredients and instructions for a [blue]{cocktail_name}[/].\n\n"
    page_content += "Ingredients marked [red]red[/] are not available in the inventory."

    display_page(location="Cocktails",
                 title=cocktail_name,
                 content=page_content
                 )

    low_on_stock = []

    columns = {
        "Ingredient": [],
        "Measure": []
    }

    for ingredient, measure in ingredients.items():
        if inventory[ingredient]["quantity"] == 0:
            low_on_stock.append(ingredient)
            columns["Ingredient"].append(f"[red]{inventory[ingredient]["name"]}[/]")
        else:
            columns["Ingredient"].append(inventory[ingredient]["name"])
        columns["Measure"].append(measure if measure is not None else "-")

    display_table(columns)

    panel_content = "- " + instructions.replace(". ", ".\n- ")

    display_panel(panel_content, title="instructions")

    while True:
        columns = {
            "Action": ["Order cocktail", "Statistics", "Deactivate cocktail"]
        }

        if low_on_stock:
            columns["Action"].append("Add unavailable ingredients to shopping list")

        columns["Action"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            if low_on_stock:
                get_input("Cocktail cannot be ordered because not all ingredients are available.", color="red")
                break
            from modules.orders import new_order
            new_order(cocktail_id)

        elif menu_choice == 2:
            show_cocktail_statistics(cocktail_id)
            continue

        elif menu_choice == 3:
            deactivate_cocktail(cocktail_id)

        elif menu_choice == 4:
            for item_id in low_on_stock:
                update_record("inventory", item_id, "shopping_list", True)
            print_message("Ingredients successfully added to shopping list.\n", "green")
            get_input()

        break

    return


def search_cocktail(search_method=""):
    if search_method == "lucky_shot":
        params = PARAM_LUCKY_SHOT
        cocktail_id = search_cocktails_in_db(params, "lucky_shot")

        if cocktail_id is None:
            return

    else:
        content = f"Here you can search cocktails by {search_method}."

        display_page(location="Cocktails",
                     title=f"Search by {search_method}",
                     content=content
                     )

        cocktails = None

        if search_method == "name":
            name = get_input("What is the name of the cocktail you would you like to search for? ").lower()
            params = PARAM_SEARCH_BY_NAME + name
            cocktails = search_cocktails_in_db(params, "name")

        elif search_method == "ingredient":
            print_message("The following ingredients are available in the inventory.")

            inventory = load_data("inventory")

            columns = {
                "Ingredient": [],
            }

            for item_id, item in inventory.items():
                if item["quantity"] > 0:
                    columns["Ingredient"].append(item["name"])

            columns["Ingredient"].extend(["", "Back"])

            display_table(columns, auto_number=True)

            menu_choice = get_menu_choice(range(0, len(columns["Ingredient"]) - 1))

            if menu_choice == 0:
                return

            ingredient = columns["Ingredient"][menu_choice - 1]
            params = PARAM_SEARCH_BY_INGREDIENT + ingredient
            cocktails = search_cocktails_in_db(params, "ingredient")

        if not isinstance(cocktails, dict):
            return

        content = "The following cocktails were found:"

        display_page(location="Cocktails",
                     title=f"Search by {search_method}",
                     content=content
                     )

        columns = {
            "Cocktail": []
        }

        for cocktail, cocktail_id in sorted(cocktails.items(), key=lambda entry: entry[0].casefold()):
            columns["Cocktail"].append(cocktail)

        columns["Cocktail"].extend(["", "Back"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))

        if menu_choice == 0:
            return

        cocktail_name = columns["Cocktail"][menu_choice -1]
        cocktail_id = cocktails[cocktail_name]

    add_cocktail_to_local_db(cocktail_id)
    cocktails = load_data("cocktails")

    if cocktail_id in cocktails:
        show_cocktail(cocktail_id)

    return


def deactivate_cocktail(cocktail_id):
    from modules.orders import cancel_order
    cancel_order(cocktail_id=cocktail_id)

    update_record("cocktails", cocktail_id, "active", False)

    print_message("Cocktail successfully deactivated.", "green")
    print()
    get_input()


def show_cocktail_statistics(cocktail_id):
    cocktails = load_data("cocktails")
    cocktail = cocktails[cocktail_id]

    orders = load_data("orders")
    rankings = load_data("rankings")
    persons = load_data("persons")
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

    total_score = 0.0
    number_of_ratings = 0

    for ranking in rankings.values():
        if ranking["cocktail"] == cocktail_id:
            number_of_ratings += 1
            total_score += ranking["score"]

    average_score = round(total_score / number_of_ratings, 1)

    panel_content += f"Average score:    {average_score}\n"
    panel_content += f"Number of votes:  {number_of_ratings}"

    display_panel(panel_content, title="Overview")

    columns = {
        "Guest": [],
        "Times served": [],
    }

    order_counts = {}

    for order in orders.values():
        if order["cocktail"] == cocktail_id and order["status"] == "served":
            person_id = order["person"]
            order_counts[person_id] = order_counts.get(person_id, 0) + 1

    for person_id, count in sorted(order_counts.items(), key=lambda entry: entry[1], reverse=True):
        person = persons[person_id]
        name = f"{person['first_name']} {person['surname']}"

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
        "Score": [],
    }

    for ranking in sorted(rankings.values(), key=lambda entry: entry["score"], reverse=True):
        if ranking["cocktail"] == cocktail_id:
            person = persons[ranking["person"]]
            name = f"{person['first_name']} {person['surname']}"

            columns["Guest"].append(name)
            columns["Date"].append(ranking["date"])
            columns["Score"].append(ranking["score"])

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


