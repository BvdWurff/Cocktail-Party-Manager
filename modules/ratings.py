def calculate_average_ratings(rankings):
    total_ratings = {}
    number_of_ratings = {}

    for ranking in rankings:
        cocktail_id = ranking["cocktail"]

        total_ratings[cocktail_id] = total_ratings.get(cocktail_id, 0) + ranking["rating"]
        number_of_ratings[cocktail_id] = number_of_ratings.get(cocktail_id, 0) + 1

    average_ratings = {}

    for cocktail_id, total_rating in total_ratings.items():
        number = number_of_ratings[cocktail_id]
        average_ratings[cocktail_id] = {
            "average": round(total_rating / number, 1),
            "votes": number
        }

    return average_ratings