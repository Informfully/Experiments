import json

## Example for EB-NERD,and Mind dataset

# Load the sentiment.json file
with open("sentiment.json", "r", encoding="utf-8") as f:
    sentiment_data = json.load(f) # Extract the dictionary from the list

print(f"len sentiment:{len(sentiment_data)}")

# Function to convert sentiment score to one-hot encoding
def sentiment_to_one_hot(score):
    if -1 <= score < -0.5:
        return [1, 0, 0, 0]
    elif -0.5 <= score < 0:
        return [0, 1, 0, 0]
    elif 0 <= score < 0.5:
        return [0, 0, 1, 0]
    elif 0.5 <= score <= 1:
        return [0, 0, 0, 1]

# Apply the function to each sentiment value
one_hot_encoded = {key: sentiment_to_one_hot(value) for key, value in sentiment_data.items()}

# Save the result to a new JSON file
with open("sentiment_vectors.json", "w", encoding="utf-8") as f:
    json.dump(one_hot_encoded, f, indent=4)

print("One-hot encoding complete! Saved as sentiment_vectors.json")
