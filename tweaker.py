from elect_tweaker import elect_data
from elect_tweaker import elect_tweaker
from elect_tweaker import repository
import json
import datetime


def print_message(title, message):
    print("{}: {}".format(title, message))


start_year = 1840
persist = True
override_cache = False
use_adjusted_google_sheet = False

current_year = datetime.datetime.now().year

for year in range(start_year, current_year, 4):
    voting_data = repository.load_saved_voting_data(year)

    if voting_data is None or override_cache:
        if use_adjusted_google_sheet:
            print_message(year, "Processing google sheet html...")
            voting_data = elect_data.convert_adjusted_table_to_json_data("google_sheets_election_{}.html".format(year))
        else:
            print_message(year, "Retrieving from wikipedia...")
            try:
                voting_data = elect_data.convert_wiki_to_json_data(
                    "https://en.wikipedia.org/wiki/United_States_presidential_election,_{}".format(year))
            except:
                print_message(year, "***** Error processing wikipedia table *****")
                continue

        if persist:
            repository.persist_voting_data(voting_data, year)
            print_message(year, "Saved voting data")

        print(json.dumps(voting_data, indent=2, sort_keys=True))
    else:
        print_message(year, "Found cached voting data")

    tweaker_results = repository.load_saved_tweaker_results(year)

    if tweaker_results is None or override_cache:
        print_message(year, "Processing voting data...")
        elect_tweaker.process_winner_take_all(voting_data)
        elect_tweaker.process_proportional(voting_data)

        if persist:
            repository.persist_tweaker_results(voting_data, year)
            print_message(year, "Saved allocation results")

        print(json.dumps(voting_data["candidates"], indent=2, sort_keys=True))
    else:
        print_message(year, "Found cached allocation results")
