# ==============================
# FUNCTION IMPORTS
# ==============================

from menus import main_menu

from modules.events import update_events

from utils.constants import (
    CONTINUE_PROMPT,
)

from utils.utils import (
    display_page,
    get_menu_choice,
    display_table,
    get_input,
)


def main():
    """
    Initializes the application, displays the welcome screen,
    and manages the main menu and exit confirmation.
    """
    update_events()

    content = """Welcome to [bright_yellow]the Cocktail Party Manager[/]!

For the best experience, it is recommended to run the program 
in a [green]terminal[/] or to enable [green]Emulate terminal in output console[/] 
in PyCharm."""

    display_page(location="Cocktail Party Manager",
                 title="Welcome",
                 content=content
                 )

    get_input(CONTINUE_PROMPT)

    while True:
        main_menu()

        content = "Are you sure you want to exit [bright_yellow]the Cocktail Party Manager[/]?"

        display_page(location="Cocktail Party Manager",
                     title="Exit Confirmation",
                     content=content
                     )

        columns = {
            "Action": ["Yes", "No"]
        }

        display_table(columns, auto_number=True)

        menu_choice = get_menu_choice(range(1, len(columns["Action"]) + 1))

        if menu_choice == 2:
            continue

        else:
            content = "Thank you for using [bright_yellow]the Cocktail Party Manager[/].\n\n"
            content += "[blue]Until we drink again![/]"

            display_page(location="Cocktail Party Manager",
                         title="Exit",
                         content=content
                         )
            break


if __name__ == "__main__":
    main()
