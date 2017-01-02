from elect_tweaker import elect_data
from elect_tweaker import elect_tweaker
from elect_tweaker import repository
import json

year = "1988"

voting_data = repository.load_saved_voting_data(year)

if voting_data is None:
    print("Retrieving from wikipedia...")
    voting_data = elect_data.convert_wiki_to_json_data('https://en.wikipedia.org/wiki/United_States_presidential_election,_' + year)
    repository.persist_voting_data(voting_data, year)

elect_tweaker.process_winner_take_all(voting_data)
elect_tweaker.process_proportional(voting_data)

repository.persist_tweaker_results(voting_data, year)

print(json.dumps(voting_data["candidates"], indent=2, sort_keys=True))