# ==============================
# LIBRARY IMPORTS
# ==============================

from collections.abc import Iterable
from typing import Any

# ==============================
# RATING CALCULATIONS
# ==============================

def calculate_average_ratings(rankings: Iterable[dict[str, Any]]) -> dict[str, dict[str, float | int]]:
    """
    Calculates the average rating and number of votes for each cocktail.

    Processes individual ratings and groups them by cocktail ID.
    The average rating is rounded to one decimal place.

    Args:
        rankings (list): A list of rating dictionaries containing
            the cocktail ID and its numerical rating.

    Returns:
        dict: A dictionary containing the average rating and total
            number of votes for each cocktail, indexed by cocktail ID.
    """
    total_ratings = {}
    number_of_ratings = {}

    # Calculate the total rating and number of votes per cocktail.
    for ranking in rankings:
        cocktail_id = ranking["cocktail"]

        total_ratings[cocktail_id] = total_ratings.get(cocktail_id, 0) + ranking["rating"]
        number_of_ratings[cocktail_id] = number_of_ratings.get(cocktail_id, 0) + 1

    average_ratings = {}

    # Calculate the average rating for each cocktail.
    for cocktail_id, total_rating in total_ratings.items():
        number = number_of_ratings[cocktail_id]
        average_ratings[cocktail_id] = {
            "average": round(total_rating / number, 1),
            "votes": number
        }

    return average_ratings