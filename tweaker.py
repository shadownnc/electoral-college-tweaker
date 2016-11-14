from elect_tweaker import elect_data
from elect_tweaker import elect_tweaker
import json

voting_data = elect_data.convert_wiki_to_json_data('https://en.wikipedia.org/wiki/United_States_presidential_election,_1996')

elect_tweaker.process_winner_take_all(voting_data)
elect_tweaker.process_proportional(voting_data)

print(json.dumps(voting_data["candidates"], indent=2))