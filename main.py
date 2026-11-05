# ==============================
# FUNCTION IMPORTS
# ==============================

import datetime

from utils.utils import (
    load_data,
    save_data,
    display_page,
    get_menu_choice,
    display_table,
    get_input,
    update_record,
)

from menus import main_menu

from utils.constants import (
    CONTINUE_PROMPT,
)

from modules.orders import cancel_order


def update_events():
    events = load_data("events")
    today = datetime.date.today()

    for event_id, event in events.items():
        if not event["active"]:
            cancel_order(event_id=event_id)
            continue

        event_date = datetime.datetime.strptime(event["date"], "%d-%m-%Y").date()

        current = event_date == today
        active = event_date >= today

        event_update = {
            "id": event_id,
            "name": event["name"],
            "date": event["date"],
            "current": current,
            "active": active,
            "guests": event["guests"]
        }

        if event["current"] != current or event["active"] != active:
            save_data("events", event_update)

            if not active:
                cancel_order(event_id=event_id)

    return


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