from rich import box
from rich.table import Table
from rich.text import Text
from rich.console import Console
from rich.padding import Padding

from cocktail_api import (
    new_cocktail,
    get_cocktails_by_name,
)

from inventory import check_cocktail_availability

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
    SELECT_OPTION,
    CONTINUE_PROMPT,
)

# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)


def select_cocktail():
    while True:
        clear_terminal()

        cocktails = load_data("cocktails")

        options_column_1 = []
        options_column_2 = []
        cocktail_ids = []

        for cocktail_id, cocktail in sorted(cocktails.items(), key=lambda item: item[1]["name"].casefold()):
            low_on_stock = check_cocktail_availability(cocktail_id)
            print(low_on_stock)

            if cocktail["active"] and not low_on_stock:
                cocktail_ids.append(cocktail_id)
                options_column_2.append(cocktail["name"])

        options_column_2.append("")
        options_column_2.append("Cocktail not on list.")

        console.print(
            Padding(display_table(name_column_1="Options", options_column_1=options_column_1,
                                  name_column_2="Cocktails", options_column_2=options_column_2, width=70),
                    (1, 0, 1, 5))
        )

        menu_choice = get_menu_choice(range(0, len(options_column_2) + 1))
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


