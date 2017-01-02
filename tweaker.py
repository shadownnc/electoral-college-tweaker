from elect_tweaker import elect_data
from elect_tweaker import elect_tweaker
from elect_tweaker import repository
import json

year = "2012"
persist = True
use_adjusted_google_sheet = False

voting_data = repository.load_saved_voting_data(year)
#voting_data = None

if voting_data is None:
    if use_adjusted_google_sheet:
        print("Processing google sheet html...")
        voting_data = elect_data.convert_adjusted_table_to_json_data("google_sheets_election_{}.html".format(year))
    else:
        print("Retrieving from wikipedia...")
        voting_data = elect_data.convert_wiki_to_json_data(
            "https://en.wikipedia.org/wiki/United_States_presidential_election,_{}".format(year))

    if persist:
        repository.persist_voting_data(voting_data, year)
    else:
        print(json.dumps(voting_data, indent=2, sort_keys=True))

elect_tweaker.process_winner_take_all(voting_data)
elect_tweaker.process_proportional(voting_data)

if persist:
    repository.persist_tweaker_results(voting_data, year)

print(json.dumps(voting_data["candidates"], indent=2, sort_keys=True))