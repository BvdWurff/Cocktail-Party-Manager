# ==============================
# FUNCTION IMPORTS
# ==============================

import os
import requests
from dotenv import load_dotenv

from rich import box
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich.console import Console


from utils.utils import (
    get_menu_choice,
    print_message,
    get_input,
    display_panel,
    display_table,
    clear_terminal,
    display_page,
)

from menus import main_menu

# ==============================
# CONSTANTS
# ==============================

from utils.constants import (
    CONTINUE_PROMPT,
)


# ==============================
# CONFIGURATION
# ==============================

console = Console(width=80)



def main():
    """
        Controls the main program flow.
    """


    main_menu()




if __name__ == "__main__":
    main()