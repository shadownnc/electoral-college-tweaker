from lxml import html
import requests
#import io

page = requests.get('https://en.wikipedia.org/wiki/United_States_presidential_election,_2000')
tree = html.fromstring(page.content)

#tree = None
#with open('wikipedia_election_1996.html', 'r', encoding="utf8") as f:
#    tree = html.fromstring(f.read())

tables = tree.xpath('//table[@class="wikitable sortable"]')

stateTable = None
for table in tables:
    stateHeader = table.xpath('.//th[text()="State"]')
    if stateHeader:
        stateTable = table
        break

if stateTable is None:
    raise ImportError

candidateArray = stateTable.xpath('.//th[@colspan=3]/text()')

candidateIndex = []

for value in candidateArray:
    candidateRecord = None
    if len(candidateIndex) > 0:
        candidateRecord = candidateIndex[len(candidateIndex) - 1]

    if candidateRecord is None or candidateRecord["party"]:
        candidateIndex.append({
            "name": value.strip(),
            "party": None
        })
    elif candidateRecord["party"] is None:
        candidateRecord["party"] = value.strip()

print(candidateIndex)

stateRows = stateTable.getchildren()

votingData = []

#print(stateRows)

def firstOrNone(result):
    return result[0] if result and len(result) > 0 else None

foundState = False
for row in stateRows:
    stateCells = row.getchildren()

    #print(stateCells)

    stateName = firstOrNone(stateCells[0].xpath('.//a/text()'))

    if not foundState and stateName == 'Alabama':
        foundState = True
    elif not foundState:
        continue

    electoralVotes = stateCells[1].text

    stateData = {
        "name": stateName,
        "electoralVotes": electoralVotes,
        "candidateData": {}
    }

    for i in range(0, len(candidateIndex)):
        candidateData = {
            "popularVoteTotal": stateCells[3*i + 2].text,
            "popularVotePercentage": stateCells[3*i + 3].text
        }
        stateData["candidateData"][candidateIndex[i]["name"]] = candidateData

    votingData.append(stateData)


print(votingData)