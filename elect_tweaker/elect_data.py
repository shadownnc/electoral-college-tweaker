from lxml import html
import requests

# set this to True to print debugging lines
debug = False


def get_html_from_webpage(url):
    page = requests.get(url)
    return html.fromstring(page.content)


def get_html_from_file(path):
    with open(path, 'r', encoding="utf8") as f:
        return html.fromstring(f.read())


def get_state_table_from_html(html):
    tables = html.xpath('//table[@class="wikitable sortable"]')

    if len(tables) == 0:
        tables = html.xpath('//table[@class="wikitable"]')

    state_table = None
    for table in tables:
        state_header = first_or_none(table.xpath('.//th[text()="State"]'))
        if state_header is not None:
            state_table = table
            break

        state_header = first_or_none(table.xpath('.//th[starts-with(text(),"State or")]'))
        if state_header is not None:
            state_table = table
            break

    if state_table is None:
        raise ImportError

    return state_table


def build_candidate_index_from_state_table(state_table):
    candidate_cells = state_table.xpath('.//th[@colspan=3]')

    if len(candidate_cells) == 0:
        candidate_cells = state_table.xpath('.//td[@colspan=3]')

    candidate_index = []

    for cell in candidate_cells:
        text = cell.text_content()

        # had some trouble getting newlines in Google Sheets, using a special delimiter as a fallback
        split_character = "--" if "--" in text else "\n"

        values = text.split(split_character)
        values = list(filter(bool, values))

        candidate_index.append({
            "name": values[0].strip(),
            "party": values[len(values) - 1].strip(),
            "votes": {
                    "popular": {
                        "count": 0,
                        "percentage": 0
                    }
                }
            })

    return candidate_index


def first_or_none(result):
    return result[0] if result and len(result) > 0 else None


def parse_int(text):
    if text is None:
        return 0

    if len(text.strip()) == 0:
        return 0

    return int(text.replace("–", "0").replace("-", "0").replace(",", ""))


def parse_percentage(text):
    if text is None:
        return 0

    if len(text.strip()) == 0:
        return 0

    return float(text.replace("–", "0").replace("-", "0").strip('%')) / 100


def get_colspan(element):
    colspan = first_or_none(element.xpath('.//@colspan'))
    return 1 if not colspan else int(colspan)


def build_state_data_from_state_row(state_row, candidate_index, prev_state_name):
    state_cells = state_row.getchildren()

    if len(state_cells) == 1 or get_colspan(state_cells[0]) > 1:
        # this is a preliminary header that can be skipped
        return None

    # the state name might be in a link
    state_name = first_or_none(state_cells[0].xpath('.//a/text()'))

    # otherwise check the text
    if not state_name:
        state_name = state_cells[0].text

    # if we didn't find anything, or it's the header, skip this row
    if not state_name or state_name.lower() == "state":
        return None

    # normalize "Total" if we find it
    if state_name.lower().startswith("total"):
        state_name = "Total"

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
    current_candidate_index = 0
    i = 2

    while i < len(state_cells) and current_candidate_index < len(candidate_index):
        candidate_name = candidate_index[current_candidate_index]["name"]

        colspan = get_colspan(state_cells[i])

        # each candidate spans 3 columns
        vote_total_text = "0" if colspan > 1 else state_cells[i].text
        vote_percentage_text = "0" if colspan > 1 else state_cells[i + 1].text
        electoral_vote_total_text = "0" if colspan > 2 else state_cells[i + 3 - colspan].text

        i += 4 - colspan
        current_candidate_index += 1

        if must_calculate_total:
            total_electoral_votes += parse_int(electoral_vote_total_text)

        if debug:
            print("{}\t{}\t{}\t{}".format(state_name, candidate_name, vote_total_text, vote_percentage_text))

        vote_total = parse_int(vote_total_text)
        percentage = parse_percentage(vote_percentage_text)

        # handle cases where there was no popular vote by just tallying one vote for the winner picked by the state
        if vote_total == 0 and parse_int(electoral_vote_total_text) > 0 and colspan > 1:
            vote_total = 1
            percentage = 1

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
            break
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

    # strip out the first row, which is column letter headers
    rows[0].getparent().remove(rows[0])

    candidate_index = build_candidate_index_from_state_table(state_table)
    voting_data = build_voting_data_from_state_table(state_table, candidate_index)

    return voting_data
