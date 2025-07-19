import json

with open("party.json", "r") as f:
    party_raw_data = json.load(f)
    print(party_raw_data)

new_dict = {}

for article_id, parties in party_raw_data.items():
    if not parties:
        new_dict[article_id] = {"No party": 1}
    else:
        new_dict[article_id] = {party: 1 for party in parties}

print(json.dumps(new_dict, indent=4))
with open("entities_binary_count.json", "w") as f:
    json.dump(new_dict, f)
