import json
import glob
import sys

collectionName = sys.argv[1].lower()
platform = sys.argv[2].lower()

objects = {}
weight = {}
max = 0

directory = glob.glob(f"../collections/{platform}/{collectionName}/metadata/*.json")
for file in directory:
    number = file.replace(f"../collections/{platform}/{collectionName}/metadata/", '').replace('.json', '')
    f = open(file)
    data = json.load(f)
    max += 1
    if "attributes" not in data:
        data["attributes"] = []

    for row in data["attributes"]:
        if "display_type" in row:
            del row["display_type"]
        if "max_value" in row:
            del row["max_value"]
        if "trait_count" in row:
            del row["trait_count"]
        if "order" in row:
            del row["order"]

        if type(row["value"]) == str:
            row["value"] = row["value"].replace("", "")

        if not row["trait_type"] in objects:
            objects[row["trait_type"]] = {}
        if not row["value"] in objects[row["trait_type"]]:
            objects[row["trait_type"]][row["value"]] = 0
        objects[row["trait_type"]][row["value"]] += 1

    f.close()
    dfile = open(file, "w+")
    json.dump(data, dfile, indent=3)
    dfile.close()

for file in directory:
    number = file.replace(f"../collections/{platform}/{collectionName}/metadata/", '').replace('.json', '')
    f = open(file)
    data = json.load(f)
    if not data["attributes"]:
        weight[number] = 0
    for row in data["attributes"]:
        if not number in weight:
            weight[number] = 0
        weight[number] += 1/objects[row["trait_type"]][row["value"]]*100
    f.close()
weight = {k: v for k, v in sorted(weight.items(), key=lambda item: item[1], reverse=True)}

rank = 1
for x in weight:
    file = f"../collections/{platform}/{collectionName}/metadata/{x}.json"
    f = open(file)
    data = json.load(f)
    for row in data["attributes"]:
        if row["trait_type"] == "Rarity Rank":
            data["attributes"].remove(row)

    data["attributes"].append({
        "trait_type": "Rarity Rank",
        "value": rank,
        "display_type": "number",
        "max_value": max
    })
    f.close()
    dfile = open(file, "w+")
    json.dump(data, dfile, indent=3)
    dfile.close()
    rank += 1