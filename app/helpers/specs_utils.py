import json

def ParseToList(dict):
    if dict:
        optionsParsed = json.loads(dict)
        optionsList = [item["value"] for item in optionsParsed]
        return optionsList
    else:
        return []