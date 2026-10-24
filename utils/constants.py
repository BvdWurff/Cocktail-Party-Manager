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
