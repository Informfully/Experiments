import json
import pandas as pd

## Example for EB-NERD dataset
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

# Load from a JSON file
with open('party.json', 'r') as f:
    article_parties = json.load(f)

def normalize(party_name):
    # Lowercase and strip surrounding whitespace
    return party_name.lower().strip()

# Normalize party sets
gov_parties_normalized = set(map(normalize, gov_parties))
opp_parties_normalized = set(map(normalize, opp_parties))

# Classify articles
article_categories = {}

for article_id, parties in article_parties.items():
    # Normalize mentioned party names
    mentioned_parties = set(map(normalize, parties.keys()))

    # Check mentions
    gov_mentioned = bool(mentioned_parties & gov_parties_normalized)
    opp_mentioned = bool(mentioned_parties & opp_parties_normalized)

    # Identify "other" parties
    known_parties = gov_parties_normalized.union(opp_parties_normalized)
    other_parties = mentioned_parties - known_parties

    # Assign category
    if not mentioned_parties:
        category = "No Party"
    elif other_parties:
        category = "Other Parties"
    elif gov_mentioned and opp_mentioned:
        category = "Both GOV + OPP Parties"
    elif gov_mentioned and not opp_mentioned:
        category = "Only GOV Parties"
    elif opp_mentioned and not gov_mentioned:
        category = "Only OPP Parties"
    else:
        category = "Other Parties"  # Fallback

    article_categories[article_id] = category

# Print results
for article, cat in article_categories.items():
    print(f"Article {article}: {cat}")

# Convert dictionary to DataFrame
df = pd.DataFrame(list(article_categories.items()), columns=["article_id", "category"])
distribution = df['category'].value_counts()
print(distribution)

category_to_vector = {
    "Only GOV Parties": [1, 0, 0, 0, 0],
    "Only OPP Parties": [0, 1, 0, 0, 0],
    "Both GOV + OPP Parties": [0, 0, 1, 0, 0],
    "Other Parties": [0, 0, 0, 1, 0],
    "No Party": [0, 0, 0, 0, 1]
}

df['one_hot'] = df['category'].map(category_to_vector)

# Create dictionary {article_id: one_hot}
article_to_onehot = df.set_index('article_id')['one_hot'].to_dict()

# Done!
print(article_to_onehot)

with open("party_vectors.json", "w") as f:
    json.dump(article_to_onehot, f)

print("Saved to party_vectors.json")
