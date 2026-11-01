import os
from dotenv import load_dotenv

# ==============================
# USER INTERFACE
# ==============================

INVALID_INPUT = f"\n{" " * 5}[red]Invalid input. Please try again.[/]\n"
CONTINUE_PROMPT = "Press [blue]Enter[/] to continue."
SELECT_OPTION = "Select an option: "

URL = "https://www.thecocktaildb.com/api/json/v1/"

load_dotenv()
API_KEY = os.getenv("API_KEY")

PARAM_LUCKY_SHOT = "/random.php"
PARAM_SEARCH_BY_NAME = "/search.php?s="
PARAM_SEARCH_BY_INGREDIENT = "/filter.php?i="
PARAM_ITEM_DESCRIPTION = "/lookup.php?iid=552"
