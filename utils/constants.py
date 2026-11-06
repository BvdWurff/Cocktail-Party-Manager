# ==============================
# LIBRARY IMPORTS
# ==============================

import os

from dotenv import load_dotenv


# ==============================
# USER INTERFACE
# ==============================

# Standard messages and prompts used throughout the application.
INVALID_INPUT = f"\n{" " * 5}[red]Invalid input. Please try again.[/]\n"
CONTINUE_PROMPT = "Press [blue]Enter[/] to continue."
SELECT_OPTION = "Select an option: "


# ==============================
# API CONFIGURATION
# ==============================

# Base URL for TheCocktailDB API.
URL = "https://www.thecocktaildb.com/api/json/v1/"

# Load the API key from environment variables.
load_dotenv()
API_KEY = os.getenv("API_KEY")


# ==============================
# API ENDPOINTS
# ==============================

# Cocktail endpoints.
PARAM_LUCKY_SHOT = "/random.php"
PARAM_SEARCH_BY_NAME = "/search.php?s="
PARAM_SEARCH_BY_INGREDIENT = "/filter.php?i="
PARAM_COCKTAIL_BY_ID = "/lookup.php?i="

# Ingredient endpoints.
PARAM_ITEM_BY_ID = "/lookup.php?iid="
PARAM_ITEM_BY_NAME = "/search.php?i="
