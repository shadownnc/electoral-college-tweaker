from elect_tweaker import elect_data

voting_data = elect_data.convert_wiki_to_json_data('https://en.wikipedia.org/wiki/United_States_presidential_election,_1996')


def add_electoral_votes(candidate_name, candidate_index, algorithm, amount):
    for candidate in candidate_index:
        if candidate["name"] == candidate_name:
            candidate[algorithm] = int(candidate[algorithm]) + int(amount)


def process_winner_take_all(voting_data):
    for state_data in voting_data["stateResults"]:
        print("{}: Awarding all {} electoral votes to {}".format(state_data["name"], state_data["electoralVotes"], state_data["topCandidate"]))
        add_electoral_votes(state_data["topCandidate"], voting_data["candidates"], "winnerTakeAllVotes", state_data["electoralVotes"])


def process_proportional(votingData):
    for stateData in votingData["stateResults"]:
        total_electoral_votes = float(stateData["electoralVotes"])
        allocated = 0
        vote_map = {}
        for candidate_key in stateData["candidateData"]:
            candidate_data = stateData["candidateData"][candidate_key]
            proportioned_votes = int(total_electoral_votes * float(candidate_data["popularVotePercentage"]))
            vote_map[candidate_key] = proportioned_votes
            if proportioned_votes > 0:
                print("{}: Awarding {} electoral votes to {}".format(stateData["name"], proportioned_votes, candidate_key))
            add_electoral_votes(candidate_key, voting_data["candidates"], "proportionedVotes", proportioned_votes)
            allocated = allocated + vote_map[candidate_key]

        # any unallocated votes go to the top vote getter
        add_electoral_votes(stateData["topCandidate"], voting_data["candidates"], "proportionedVotes", total_electoral_votes - allocated)


process_winner_take_all(voting_data)
process_proportional(voting_data)

print(voting_data["candidates"])