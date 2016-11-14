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

    if state_table is None:
        raise ImportError

    return state_table


def firstOrNone(result):
    return result[0] if result and len(result) > 0 else None


def build_candidate_index_from_state_table(state_table):
    candidate_cells = state_table.xpath('.//th[@colspan=3]/text()')
    candidate_index = []

    for value in candidate_cells:
        candidate_record = None
        if len(candidate_index) > 0:
            candidate_record = candidate_index[len(candidate_index) - 1]

        if candidate_record is None or candidate_record["party"]:
            candidate_index.append({
                "name": value.strip(),
                "party": None,
                "electoralVotes": {}
            })
        elif candidate_record["party"] is None:
            candidate_record["party"] = value.strip()

    return candidate_index


def build_state_data_from_state_row(state_row, candidate_index):
    state_cells = state_row.getchildren()

    # the state name will be in a link
    state_name = firstOrNone(state_cells[0].xpath('.//a/text()'))

    if not state_name:
        return None

    electoral_votes = state_cells[1].text

    state_data = {
        "name": state_name,
        "electoralVotes": electoral_votes,
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

        vote_total = vote_total_text.replace("–", "0").replace(",", "")
        percentage = float(vote_percentage_text.replace("–", "0").strip('%')) / 100
        if percentage > top_percentage:
            top_candidate = candidate_name
            top_percentage = percentage

        candidate_data = {
            "popularVoteTotal": vote_total,
            "popularVotePercentage": "{0:.4f}".format(percentage)
        }
        state_data["candidateData"][candidate_name] = candidate_data

    state_data["topCandidate"] = top_candidate

    return state_data


def build_voting_data_from_state_table(state_table, candidate_index):
    voting_data = {
        "candidates": candidate_index,
        "stateResults": []
    }
    state_rows = state_table.getchildren()

    for row in state_rows:
        state_data = build_state_data_from_state_row(row, candidate_index)

        if state_data:
            voting_data["stateResults"].append(state_data)

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
