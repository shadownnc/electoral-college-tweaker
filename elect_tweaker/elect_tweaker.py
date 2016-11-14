def add_electoral_votes(amount, candidate_name, candidate_index, algorithm):
    for candidate in candidate_index:
        if candidate["name"] == candidate_name:
            if algorithm not in candidate["electoralVotes"]:
                candidate["electoralVotes"][algorithm] = 0

            candidate["electoralVotes"][algorithm] = int(candidate["electoralVotes"][algorithm]) + int(amount)


def process_winner_take_all(voting_data):
    for state_data in voting_data["stateResults"]:
        #print("{}: Awarding all {} electoral votes to {}".format(state_data["name"], state_data["electoralVotes"], state_data["topCandidate"]))
        add_electoral_votes(state_data["electoralVotes"], state_data["topCandidate"], voting_data["candidates"],
                            "winnerTakeAll")


def process_proportional(voting_data):
    for stateData in voting_data["stateResults"]:
        total_electoral_votes = float(stateData["electoralVotes"])
        allocated = 0

        for candidate_key in stateData["candidateData"]:
            candidate_data = stateData["candidateData"][candidate_key]
            proportioned_votes = int(total_electoral_votes * float(candidate_data["popularVotePercentage"]))

            add_electoral_votes(proportioned_votes, candidate_key, voting_data["candidates"], "proportional")
            allocated += proportioned_votes

            #if proportioned_votes > 0:
            #    print("{}: Awarding {} electoral votes to {}".format(stateData["name"], proportioned_votes, candidate_key))

        # any unallocated votes go to the top vote getter
        add_electoral_votes(total_electoral_votes - allocated, stateData["topCandidate"], voting_data["candidates"],
                            "proportional")