import json

# Load sentiment vectors, see `evaluation_scripts/README.md` for sentiment vectors computation.
with open('sentiment_vectors.json', 'r') as f:
     senti_dict= json.load(f)

print(senti_dict)

# Load party vectors, see `evaluation_scripts/README.md` for party vectors computation
with open('party_vectors.json', 'r') as f:
     party_dict= json.load(f)

print(party_dict)

combined_dict = {}

for item_id in senti_dict.keys():  # keep senti_dict order
    senti_vec = senti_dict.get(item_id)
    party_vec = party_dict.get(item_id)

    if item_id not in party_dict:
        print(f"Item {item_id} missing in party_dict!")
        continue

    if senti_vec is None or party_vec is None:
        print(f"Item {item_id} has None value!")
        continue

    if len(senti_vec) != 4:
        print(f"Item {item_id} has invalid senti vector length: {len(senti_vec)}")
        continue

    if len(party_vec) != 5:
        print(f"Item {item_id} has invalid party vector length: {len(party_vec)}")
        continue

    # Concatenate and keep order
    combined_dict[item_id] = senti_vec + party_vec

print(f"Total combined items: {len(combined_dict)}")

# Save combined_dict to JSON
with open('combined_senti_party_vectors.json', 'w') as f:
    json.dump(combined_dict, f)

print("combined_dict saved to combined_senti_party_vectors.json ")
