import datetime

from modules.cocktail_api import (
    new_cocktail,
    get_cocktails,
)

from modules.persons import select_guest

from modules.inventory import check_cocktail_availability

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

)

from utils.constants import (
    INVALID_INPUT,
    API_KEY,
    URL,
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

        columns["Cocktail"].extend(["", "Back to cocktail menu"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))

        if menu_choice == 0:
            break

        cocktail_id = cocktail_ids[menu_choice - 1]

        show_cocktail(cocktail_id)

        get_input("Press [blue]Enter[/] to return to All available cocktails.")

        continue

    return



def rank_a_cocktail():
    current_event, current_event_id = get_current_event()
    if current_event is None:
        return

    guest_id = None
    cocktail_id = None
    today = datetime.date.today().strftime("%d-%m-%Y")

    while True:
        rankings = load_data("rankings")
        content = "Here you can rank the cocktails you drank."

        display_page(location="Cocktails",
                     title="Rank a cocktail",
                     content=content
                     )

        if guest_id is None and cocktail_id is None:
            get_input("press [blue]Enter[/] to select a guest.")

        if guest_id is None:
            guest_id = select_guest()
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
                print(1)
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
        print_message("Your rating has been saved successfully!", "green")


        columns = {
            "Action": ["Rank another cocktail", "View ranking", "", "Back to cocktail menu"]
        }

        print()
        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Action"]) - 1))

        if menu_choice == 1:
            guest_id = ""
            cocktail_id = ""
            continue

        elif menu_choice == 2:
            show_cocktail_ranking()
            break

        break

    return


def show_cocktail_ranking():
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
        if cocktail in total_scores.keys():
            score = total_scores[cocktail] + ranking["score"]
            number = number_of_ratings[cocktail] + 1
        else:
            score = ranking["score"]
            number = 1

        total_scores[cocktail] = score
        number_of_ratings[cocktail] = number

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

    get_input("Press [blue]Enter[/] to return to the cocktail menu.")

    return



def select_cocktail(trigger=""):
    while True:
        cocktails = load_data("cocktails")

        content = "Select the cocktail you want to order."

        display_page(location="Cocktails",
                     title="Available Cocktails",
                     content=content
                     )

        cocktail_ids = []

        columns = {
            "Cocktail": []
        }

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):

            if cocktail["active"] and (trigger or not check_cocktail_availability(cocktail_id)):
                cocktail_ids.append(cocktail_id)
                columns["Cocktail"].append(cocktail["name"])

        if not trigger:
            columns["Cocktail"].extend(["", "Cocktail not on list"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))
        cocktail_id = cocktail_ids[menu_choice - 1]

        if menu_choice == 0:
            #cocktails = get_cocktails_by_name()

            if cocktails:

                print()
                print_message("The following cocktails were found:", "bright_white")

                columns = {
                    "Cocktail": []
                }

                for cocktail, cocktail_id in sorted(cocktails.items(), key=lambda item: item[0].casefold()):
                    columns["Cocktail"].append(str(cocktail))

                display_table(columns, auto_number=True)

                menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) - 1))
                cocktail_name = columns["Cocktail"][menu_choice]
                cocktail_id = cocktails.get(cocktail_name)
                new_cocktail(cocktail_id, cocktail_name)
        break

    return cocktail_id



def show_cocktail(cocktail_id):
    cocktails = load_data("cocktails")

    cocktail =  cocktails[cocktail_id]
    cocktail_name = cocktail["name"]
    ingredients = cocktail["ingredients"]
    instructions = cocktail["instructions"]

    page_content = f"Ingredients and instructions for a [blue]{cocktail_name}[/]"

    display_page(location="Cocktails",
                 title=cocktail_name,
                 content=page_content
                 )

    columns = {
        "Number": [],
        "Ingredient": [],
        "Measure": []
    }

    for number, (ingredient, measure) in enumerate(ingredients.items(), start=1):
        columns["Number"].append(number)
        columns["Ingredient"].append(ingredient)
        columns["Measure"].append(measure if measure is not None else "")

    display_table(columns)

    panel_content = "- " + instructions.replace(". ", ".\n- ")

    display_panel(panel_content, title="instructions")


def search_cocktail(search_method=""):
    content = f"Here you can search cocktails by {search_method}."

    display_page(location="Cocktails",
                 title=f"Search by {search_method}",
                 content=content
                 )

    cocktails = None

    if search_method == "name":
        name = get_input("What is the name of the cocktail you would you like to search for? ").lower()
        params = f"/search.php?s={name}"
        cocktails = get_cocktails(params, "name")

    elif search_method == "ingredient":
        inventory = load_data("inventory")

        columns = {
            "Ingredient": [],
        }

        for item_id, item in inventory.items():
            if item["quantity"] > 0:
                columns["Ingredient"].append(item["name"])

        columns["Ingredient"].extend(["", "Back to cocktails menu"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Ingredient"]) - 1))

        if menu_choice == 0:
            return

        ingredient = columns["Ingredients"][menu_choice - 1]
        params = f"/filter.php?i={ingredient}"
        cocktails = get_cocktails(params, "ingredient")


    if cocktails:
        print()
        print_message("The following cocktails were found:", "bright_white")

        columns = {
            "Cocktail": []
        }

        for cocktail in sorted(cocktails.keys(), key = lambda item: item.casefold()):
            columns["Cocktail"].append(str(cocktail))

        columns["Cocktail"].extend(["", "Back to cocktail menu"])

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Cocktail"]) + 1)) - 1
        cocktail_name = columns["Cocktail"][menu_choice]
        cocktail_id = cocktails.get(cocktail_name)

        new_cocktail(cocktail_id, cocktail_name)

        show_cocktail(cocktail_id)

        get_input()


