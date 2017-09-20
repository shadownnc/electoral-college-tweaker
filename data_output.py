from elect_tweaker import repository

tweaker_results = repository.load_saved_tweaker_results()

print("{}\t{}\t{}\t{}\t{}\t{}".format("Year", "Popular Vote %", "Winner Take All %", "Proportional Winner %", "Winner Take All Third Party %", "Proportional Third Party %"))

for year in sorted(tweaker_results):
    first_place_candidate = None
    second_place_candidate = None
    third_party_candidates = []

    first_place_winner_take_all_percentage = 0
    second_place_winner_take_all_percentage = 0
    total_third_party_winner_take_all_percentage = 0

    # construct dictionary for easy lookup later
    index = {}

    for candidate in tweaker_results[year]:
        index[candidate["name"]] = candidate

        candidate_winner_take_all_percentage = 0

        if "electoralWinnerTakeAll" in candidate["votes"]:
            candidate_winner_take_all_percentage = candidate["votes"]["electoralWinnerTakeAll"]["percentage"]

        if candidate_winner_take_all_percentage > first_place_winner_take_all_percentage:
            # bump down second place
            if second_place_candidate:
                third_party_candidates.append(second_place_candidate)
                total_third_party_winner_take_all_percentage += second_place_winner_take_all_percentage

            # bump down first place
            if first_place_candidate:
                second_place_candidate = first_place_candidate
                second_place_winner_take_all_percentage = first_place_winner_take_all_percentage

            first_place_candidate = candidate["name"]
            first_place_winner_take_all_percentage = candidate_winner_take_all_percentage
        elif candidate_winner_take_all_percentage > second_place_winner_take_all_percentage:
            # bump down second place
            if second_place_candidate:
                third_party_candidates.append(second_place_candidate)
                total_third_party_winner_take_all_percentage += second_place_winner_take_all_percentage

            second_place_candidate = candidate["name"]
            second_place_winner_take_all_percentage = candidate_winner_take_all_percentage
        else:
            third_party_candidates.append(candidate["name"])
            total_third_party_winner_take_all_percentage += candidate_winner_take_all_percentage

    total_third_party_proportional_percentage = 0

    for third_party_candidate in third_party_candidates:
        if "electoralProportional" in index[third_party_candidate]["votes"]:
            total_third_party_proportional_percentage += index[third_party_candidate]["votes"]["electoralProportional"]["percentage"]

    footnote = ""
    if index[first_place_candidate]["votes"]["electoralProportional"]["percentage"] < .5:
        if index[second_place_candidate]["votes"]["electoralProportional"]["percentage"] > .5:
            # second place ended up getting majority
            footnote = "L"
        else:
            # nobody got the majority, goes to the house
            footnote = "H"

    print("{}\t{}\t{}\t{}\t{}\t{}\t{}".format(
        year,
        index[first_place_candidate]["votes"]["popular"]["percentage"],
        index[first_place_candidate]["votes"]["electoralWinnerTakeAll"]["percentage"],
        index[first_place_candidate]["votes"]["electoralProportional"]["percentage"],
        total_third_party_winner_take_all_percentage,
        total_third_party_proportional_percentage,
        footnote
    ))





