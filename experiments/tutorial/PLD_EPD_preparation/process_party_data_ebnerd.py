import json
from collections import defaultdict
import os
## This script is necessary for PLD and EPD model.
## It accounts for multiple political parties located in Denmark (Eb-Nerd).


# Define party groups
gov_parties = {
    "Social Democrats", "Venstre", "Moderate Party", "Union Party", "Social Democratic Party",
    "Inuit Ataqatigiit", "Naleraq"
}

opp_parties = {
    "Denmark Democrats - Inger Støjberg", "Green Left", "Liberal Alliance",
    "Conservative People's Party", "Conservative Party",
    "Red–Green Alliance", "Danish People's Party",
    "Danish Social Liberal Party",
    "The Alternative"
}

dataset_result_path = './ebnerd_results'

input_file_path = os.path.join(dataset_result_path, "party.json")

# Load the enriched raw {article id: Party mention} json file.
with open(input_file_path, 'r') as f:
    original_party_data = json.load(f)

gov_parties = {party.lower() for party in gov_parties}
opp_parties = {party.lower() for party in opp_parties}

# Processed dictionary
new_party_counts = {}

for article_id, parties in original_party_data.items():
    if not parties:
        new_party_counts[article_id] = {}
        continue

    # Temp counts dict, only add keys when needed
    counts = defaultdict(int)

    for party, mentions in parties.items():
        party_lower = party.lower()

        if party_lower in gov_parties:
            counts["GOV_PARTIES"] += mentions
        elif party_lower in opp_parties:
            counts["OPP_PARTIES"] += mentions
        else:
            counts["INDEP_FOREIGN_PARTIES"] += mentions

    # Convert defaultdict to normal dict, and remove zero entries
    if counts:
        new_party_counts[article_id] = dict(counts)
    else:
        new_party_counts[article_id] = {}

output_file_path = os.path.join(dataset_result_path, "converted_party.json")

with open(output_file_path, 'w') as json_file:
    json.dump(new_party_counts, json_file)

