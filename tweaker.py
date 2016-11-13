from lxml import html
import requests
import io

page = requests.get('https://en.wikipedia.org/wiki/United_States_presidential_election,_2008')
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
            "party": None,
            "winnerTakeAllVotes": 0,
            "proportionedVotes": 0
        })
    elif candidateRecord["party"] is None:
        candidateRecord["party"] = value.strip()

#print(candidateIndex)

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
    elif not foundState or not stateName:
        continue

    electoralVotes = stateCells[1].text

    stateData = {
        "name": stateName,
        "electoralVotes": electoralVotes,
        "topCandidate": None,
        "candidateData": {}
    }

    topCandidate = None
    topPercentage = 0

    for i in range(0, len(candidateIndex)):
        candidateName = candidateIndex[i]["name"]

        textVoteTotal = stateCells[3*i + 2].text
        textPercentage = stateCells[3*i + 3].text

        percentage = float(textPercentage.replace("–", "0").strip('%'))/100
        if percentage > topPercentage:
            topCandidate = candidateName
            topPercentage = percentage

        candidateData = {
            "popularVoteTotal": textVoteTotal.replace("–", "0").replace(",", ""),
            "popularVotePercentage": "{0:.4f}".format(percentage)
        }
        stateData["candidateData"][candidateName] = candidateData

    stateData["topCandidate"] = topCandidate
    votingData.append(stateData)


#print(votingData)

def addElectoralVotes(candidateName, key, amount):
    for candidate in candidateIndex:
        if candidate["name"] == candidateName:
            candidate[key] = int(candidate[key]) + int(amount)

def processWinnerTakeAll(votingData):
    for stateData in votingData:
        print("{}: Awarding all {} electoral votes to {}".format(stateData["name"], stateData["electoralVotes"], stateData["topCandidate"]))
        addElectoralVotes(stateData["topCandidate"], "winnerTakeAllVotes", stateData["electoralVotes"])

def processProportional(votingData):
    for stateData in votingData:
        totalElectoralVotes = float(stateData["electoralVotes"])
        allocated = 0
        voteMap = {}
        for candidateKey in stateData["candidateData"]:
            candidateData = stateData["candidateData"][candidateKey]
            proportionedVotes = int(totalElectoralVotes * float(candidateData["popularVotePercentage"]))
            voteMap[candidateKey] = proportionedVotes
            print("{}: Awarding {} electoral votes to {}".format(stateData["name"], voteMap[candidateKey], candidateKey))
            addElectoralVotes(candidateKey, "proportionedVotes", proportionedVotes)
            allocated = allocated + voteMap[candidateKey]

        # any unallocated votes go to the top vote getter
        addElectoralVotes(stateData["topCandidate"], "proportionedVotes", totalElectoralVotes - allocated)



processWinnerTakeAll(votingData)
processProportional(votingData)

print(candidateIndex)