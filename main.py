# ==============================
# FUNCTION IMPORTS
# ==============================


from utils.utils import (
    display_page,
    get_menu_choice,
    display_table,
    get_input,
)

from menus import main_menu

from utils.constants import (
    CONTINUE_PROMPT,
)

from modules.events import update_events


def main():
    """
        Controls the main program flow.
    """
    update_events()

    content = f"""Welcome to [bright_yellow]the Cocktail Party Manager[/]!

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
                     title="Exit confirmation",
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
            content = ("Thank you for using [bright_yellow]the Cocktail Party Manager[/].\n\n"
                       "[blue]Until we drink again![/]")

            display_page(location="Cocktail Party Manager",
                         title="Exit",
                         content=content
                         )
            break

if __name__ == "__main__":
    main()