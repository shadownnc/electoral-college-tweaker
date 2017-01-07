import json
import os


def file_exists(path):
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return False

    return True


def get_voting_data_path_for_year(year):
    return "elect_tweaker/data/voting_data_" + str(year) + ".json"


def load_saved_voting_data(year):
    path = get_voting_data_path_for_year(year)

    if not file_exists(path):
        return None

    with open(path) as f:
        return json.load(f)


def persist_voting_data(voting_data, year):
    path = get_voting_data_path_for_year(year)
    with open(path, 'w', encoding="utf8") as f:
        json.dump(voting_data, f)


def load_saved_tweaker_results(year = None):
    if not year:
        path = "elect_tweaker/data/tweaker_results.json"

        if not file_exists(path):
            historical_data = {}
        else:
            # read the existing historical results
            with open(path) as f:
                historical_data = json.load(f)

        return historical_data
    else:
        year = str(year)
        historical_data = load_saved_tweaker_results()

        if year not in historical_data:
            return None

        return historical_data[year]


def persist_tweaker_results(voting_data, year):
    path = "elect_tweaker/data/tweaker_results.json"
    year = str(year)
    historical_data = load_saved_tweaker_results()

    historical_data[year] = voting_data["candidates"]

    # write the new results
    with open(path, 'w', encoding="utf8") as f:
        json.dump(historical_data, f)