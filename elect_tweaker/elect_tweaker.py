# set this to True to print debugging lines
debug = False


def add_electoral_votes(amount, candidate_name, candidate_index, algorithm):
    for candidate in candidate_index:
        if candidate["name"] == candidate_name:
            if algorithm not in candidate["votes"]:
                candidate["votes"][algorithm] = {
                    "count": 0,
                    "percentage": 0
                }

            candidate["votes"][algorithm]["count"] = int(candidate["votes"][algorithm]["count"]) + int(amount)


def fill_in_percentages(candidate_index, algorithm):
    # get total votes
    total_votes = 0
    for candidate in candidate_index:
        if algorithm not in candidate["votes"]:
            continue

        total_votes += int(candidate["votes"][algorithm]["count"])

    # fill in percentages
    for candidate in candidate_index:
        if algorithm not in candidate["votes"]:
            continue

        candidate["votes"][algorithm]["percentage"] = float("{0:.4f}".format(int(candidate["votes"][algorithm]["count"]) / total_votes))


def process_winner_take_all(voting_data):
    ALGORITHM = "electoralWinnerTakeAll"

    for state_data in voting_data["stateResults"]:
        if debug:
            print("{}: Awarding all {} electoral votes to {}".format(state_data["name"], state_data["electoralVotes"], state_data["topCandidate"]))

        add_electoral_votes(state_data["electoralVotes"], state_data["topCandidate"], voting_data["candidates"],
                            ALGORITHM)

    fill_in_percentages(voting_data["candidates"], ALGORITHM)


def process_proportional(voting_data):
    ALGORITHM = "electoralProportional"

    for stateData in voting_data["stateResults"]:
        total_state_electoral_votes = float(stateData["electoralVotes"])
        allocated = 0

        for candidate_key in stateData["candidateData"]:
            candidate_data = stateData["candidateData"][candidate_key]
            proportioned_votes = int(total_state_electoral_votes * float(candidate_data["popularVotePercentage"]))

            if proportioned_votes > 0:
                add_electoral_votes(proportioned_votes, candidate_key, voting_data["candidates"], ALGORITHM)
                allocated += proportioned_votes

            if proportioned_votes > 0 and debug:
                print("{}: Awarding {} electoral votes to {}".format(stateData["name"], proportioned_votes, candidate_key))

        # any unallocated votes go to the top vote getter
        add_electoral_votes(total_state_electoral_votes - allocated, stateData["topCandidate"], voting_data["candidates"],
                            ALGORITHM)

    fill_in_percentages(voting_data["candidates"], ALGORITHM)