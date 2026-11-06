from utils.utils import (
    display_table,
    get_input,
    print_message,
    get_menu_choice,
    display_page,
)


def unit_converter():
    while True:
        content = "Convert different units of measurement to milliliters (ml)."

        display_page(location="Cocktail Party Manager",
                     title="Unit converter",
                     content=content
                     )

        print_message("Select the unit you would like to convert:\n")

        columns = {
            "Unit": ["oz (fl oz)", "cup", "liter (L)", "centiliter (cl)", "teaspoon (tsp)", "tablespoon (tbsp)", "", "Back"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(0, len(columns["Unit"]) - 1))
        if menu_choice == 0:
            break

        factor = float(0)

        match menu_choice:
            case 1:
                factor = 29.5735
            case 2:
                factor = 236.5882
            case 3:
                factor = 1000
            case 4:
                factor = 10
            case 5:
                factor = 4.9289
            case 6:
                factor = 14.7868

        while True:
            volume = float(get_input("What is the volume of the unit you want to convert? ", float))

            if volume >= 0:
                print()
                volume_ml = round(volume * factor)
                print_message(f"[purple]{volume} {columns["Unit"][menu_choice - 1]}[/] is [blue]{volume_ml} ml[/]")
                print()
                get_input()
                break

            print_message("Volume cannot be negative.", "red")
            continue

    return