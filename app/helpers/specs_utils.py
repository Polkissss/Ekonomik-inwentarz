import json

def ParseToList(dict):
    optionsParsed = json.loads(dict)
    optionsList = [item["value"] for item in optionsParsed]
    return optionsList