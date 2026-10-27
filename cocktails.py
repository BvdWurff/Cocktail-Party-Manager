import datetime

from rich import box
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.padding import Padding

from cocktail_api import (
    new_cocktail,
    get_cocktails_by_name,
)

from persons import select_guest

from inventory import check_cocktail_availability

from events import get_current_event

from utils.utils import (
    load_data,
    save_data,
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    clear_terminal,
    display_page,

)

from utils.constants import (
    INVALID_INPUT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


def all_available_cocktails():
    while True:
        cocktails = load_data("cocktails")

        content = "Browse all available cocktails and explore their recipes and ingredients."

        display_page(location="Cocktails",
                     title="All available cocktails",
                     content=content
                     )

        options_column_2 = []
        cocktail_ids = []

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):
            if cocktail["active"]:
                cocktail_ids.append(cocktail_id)
                options_column_2.append(cocktail["name"])

        options_column_2.append("")
        options_column_2.append("Back to cocktail menu")

        console.print(
            Padding(display_table(name_column_2="Cocktail", options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) - 1))
        cocktail_id = cocktail_ids[menu_choice - 1]

        if menu_choice == 0:
            break

        else:
            cocktail_name = cocktails[cocktail_id]["name"]
            ingredients = cocktails[cocktail_id]["ingredients"]
            instructions = cocktails[cocktail_id]["instructions"]
            show_cocktail(cocktail_name, ingredients, instructions)

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

        options_column_2 = ["Rank another cocktail", "View ranking", "", "Back to cocktail menu"]

        console.print(
            Padding(display_table(options_column_2=options_column_2, width=70), (1, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, 3))

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

    options_column_1 = []
    options_column_2 = []
    options_column_3 = []
    options_column_4 = []

    counter = 0

    for cocktail, score in sorted(average_scores.items(), reverse=True, key=lambda item: item[1]):
        counter += 1
        options_column_1.append(counter)
        options_column_2.append(cocktail)
        options_column_3.append(score)
        options_column_4.append(number_of_ratings[cocktail])

    table = Table(
        box=box.SQUARE,
        expand=True,
        header_style="bold bright_white",
        border_style="bright_yellow",
        padding=(0, 1),
        width=70
    )

    table.add_column("Place")
    table.add_column("Cocktail")
    table.add_column("Score")
    table.add_column("Votes")

    for option_c1, option_c2, option_c3, option_c4 in zip(options_column_1, options_column_2, options_column_3, options_column_4):
        table.add_row(str(option_c1), option_c2, str(option_c3), str(option_c4))

    console.print(
        Padding(table, (0, 0, 1, 5))
    )

    get_input("Press [blue]Enter[/] to return to the cocktail menu.")

    return



def select_cocktail(trigger=""):
    while True:
        clear_terminal()
        cocktails = load_data("cocktails")

        content = "Select the cocktail you want to order."

        display_page(location="Cocktails",
                     title="Available Cocktails",
                     content=content
                     )

        options_column_2 = []
        cocktail_ids = []

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):

            if cocktail["active"] and (trigger or not check_cocktail_availability(cocktail_id)):
                cocktail_ids.append(cocktail_id)
                options_column_2.append(cocktail["name"])

        if not trigger:
            options_column_2.append("")
            options_column_2.append("Cocktail not on list")

        console.print(
            Padding(display_table(name_column_2="Cocktail", options_column_2=options_column_2, width=70), (0, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) -1))
        cocktail_id = cocktail_ids[menu_choice - 1]

        if menu_choice == 0:
            cocktails = get_cocktails_by_name()

            if cocktails:

                print()
                print_message("The following cocktails were found:", "bright_white")

                options_column_2 = []

                for cocktail, cocktail_id in sorted(cocktails.items(), key=lambda item: item[0].casefold()):
                    options_column_2.append(str(cocktail))

                console.print(
                    Padding(display_table(name_column_1="Option", name_column_2="Cocktail", options_column_2=options_column_2, width=70),
                            (0, 0, 1, 5))
                )

                menu_choice = get_menu_choice(range(0, len(options_column_2) + 1)) - 1
                cocktail_name = options_column_2[menu_choice]
                cocktail_id = cocktails.get(cocktail_name)
                new_cocktail(cocktail_id, cocktail_name)
        break

    return cocktail_id



def show_cocktail(cocktail, ingredients, instructions):
    clear_terminal()

    location = "Cocktails"
    title = cocktail
    content = f"Ingredients and instructions for a [blue]{cocktail}[/]"

    display_page(location, title, content)

    table = Table(
        box=box.SQUARE,
        expand=True,
        header_style="bold bright_white",
        border_style="bright_yellow",
        padding=(0, 1),
        width=70
    )

    table.add_column("Number")
    table.add_column("Ingredient")
    table.add_column("Measure")

    counter = 1
    for ingredient, measure in ingredients.items():
        if measure is None:
            measure = ""

        table.add_row(
            Text(str(counter)),
            Text(ingredient),
            Text(measure),
        )
        counter += 1

    console.print(
        Padding(
            table,
            (0, 0, 1, 5),
        )
    )

    content = "- " + instructions.replace(". ", ".\n- ")

    display_panel(content, title="instructions")


