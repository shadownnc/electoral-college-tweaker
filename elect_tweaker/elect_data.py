from lxml import html
import requests


def get_html_from_webpage(url):
    page = requests.get(url)
    return html.fromstring(page.content)


def get_html_from_file(path):
    with open(path, 'r', encoding="utf8") as f:
        return html.fromstring(f.read())


def get_state_table_from_html(html):
    tables = html.xpath('//table[@class="wikitable sortable"]')

    state_table = None
    for table in tables:
        state_header = table.xpath('.//th[text()="State"]')
        if state_header:
            state_table = table
            break

        state_header = table.xpath('.//th[starts-with(text(),"State or")]')
        if state_header:
            state_table = table
            break

    if state_table is None:
        raise ImportError

    return state_table


def build_candidate_index_from_state_table(state_table):
    candidate_cells = state_table.xpath('.//th[@colspan=3]/text()')

    if len(candidate_cells) == 0:
        candidate_cells = state_table.xpath('.//td[@colspan=3]/text()')

    candidate_index = []

    for value in candidate_cells:
        candidate_record = None
        if len(candidate_index) > 0:
            candidate_record = candidate_index[len(candidate_index) - 1]

        if candidate_record is None or candidate_record["party"]:
            candidate_index.append({
                "name": value.strip(),
                "party": None,
                "votes": {
                    "popular": {
                        "count": 0,
                        "percentage": 0
                    }
                }
            })
        elif candidate_record["party"] is None:
            candidate_record["party"] = value.strip()

    return candidate_index


def first_or_none(result):
    return result[0] if result and len(result) > 0 else None


def parse_int(text):
    if text is None:
        return 0

    return int(text.replace("–", "0").replace("-", "0").replace(",", ""))


def parse_percentage(text):
    if text is None:
        return 0

    return float(text.replace("–", "0").strip('%')) / 100


def build_state_data_from_state_row(state_row, candidate_index, prev_state_name):
    state_cells = state_row.getchildren()

    # the state name will be in a link
    state_name = first_or_none(state_cells[0].xpath('.//a/text()'))

    #print(state_name)

    if not state_name:
        if state_cells[len(state_cells) - 1].text == "US" or state_cells[len(state_cells) - 2].text == "US":
            state_name = "Total"
        else:
            return None

    total_electoral_votes = state_cells[1].text
    must_calculate_total = False

    if total_electoral_votes == "CD" and prev_state_name in state_name:
        return "CD"

    if total_electoral_votes == "WTA" or total_electoral_votes == "CD":
        total_electoral_votes = 0
        must_calculate_total = True

    state_data = {
        "name": state_name,
        "electoralVotes": 0,
        "topCandidate": None,
        "candidateData": {}
    }

    top_candidate = None
    top_percentage = 0

    for i in range(0, len(candidate_index)):
        candidate_name = candidate_index[i]["name"]

        # each candidate spans 3 columns
        vote_total_text = state_cells[3 * i + 2].text
        vote_percentage_text = state_cells[3 * i + 3].text
        electoral_vote_total_text = state_cells[3 * i + 4].text

        if must_calculate_total:
            total_electoral_votes += parse_int(electoral_vote_total_text)

        #print("{}\t{}\t{}\t{}".format(state_name, candidate_name, vote_total_text, vote_percentage_text))

        vote_total = parse_int(vote_total_text)
        percentage = parse_percentage(vote_percentage_text)
        if percentage > top_percentage:
            top_candidate = candidate_name
            top_percentage = percentage

        candidate_data = {
            "popularVoteTotal": vote_total,
            "popularVotePercentage": "{0:.4f}".format(percentage)
        }
        state_data["candidateData"][candidate_name] = candidate_data

    state_data["topCandidate"] = top_candidate
    state_data["electoralVotes"] = total_electoral_votes

    return state_data


def set_national_popular_vote(candidate_index, total_data):
    for candidate in candidate_index:
        candidate_name = candidate["name"]
        if candidate_name in total_data["candidateData"]:
            candidate["votes"]["popular"]["count"] = int(
                total_data["candidateData"][candidate_name]["popularVoteTotal"])
            candidate["votes"]["popular"]["percentage"] = float(
                total_data["candidateData"][candidate_name]["popularVotePercentage"])


def build_voting_data_from_state_table(state_table, candidate_index):
    voting_data = {
        "candidates": candidate_index
    }
    state_results = []
    state_rows = state_table.xpath('.//tr')
    prev_state_data = None

    for row in state_rows:
        state_data = build_state_data_from_state_row(row, candidate_index,
                                                     prev_state_data["name"] if prev_state_data else None)

        if not state_data:
            prev_state_data = None
            continue

        if state_data == "CD":
            # if it is the results for a congressional district, it counts as one more elector for the state
            prev_state_data["electoralVotes"] += 1
        elif state_data["name"] == "Total":
            set_national_popular_vote(candidate_index, state_data)
        else:
            state_results.append(state_data)
            prev_state_data = state_data

    voting_data["stateResults"] = state_results
    return voting_data


def convert_wiki_to_json_data(path):
    if path.startswith("http"):
        html_tree = get_html_from_webpage(path)
    else:
        html_tree = get_html_from_file(path)

    state_table = get_state_table_from_html(html_tree)
    candidate_index = build_candidate_index_from_state_table(state_table)
    voting_data = build_voting_data_from_state_table(state_table, candidate_index)

    return voting_data


def convert_adjusted_table_to_json_data(path):
    """
    Some Wikipedia election result tables have inconsistencies with
    the rest. In these situations, I copy the table to Google Sheets,
    make it conform to the standard, and download it as an adjusted
    HTML file.

    This unfortunately adds row numbers to every row, so those need to
    be stripped out before it can be properly processed.
    """
    html_tree = get_html_from_file(path)

    state_table = first_or_none(html_tree.xpath('//table'))

    if state_table is None:
        return None

    # strip out the first column of every row, which is a superfluous row number
    rows = state_table.xpath('.//tr')
    for row in rows:
        cells = row.getchildren()
        row.remove(cells[0])

    candidate_index = build_candidate_index_from_state_table(state_table)
    voting_data = build_voting_data_from_state_table(state_table, candidate_index)

    return voting_data
