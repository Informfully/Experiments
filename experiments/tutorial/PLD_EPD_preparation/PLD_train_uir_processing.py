import os
import pickle
import random
import sys
import pandas as pd


from cornac.datasets import mind as mind

## Update the path to the processed results of different dataset.
dataset_result_folder =  './nemig_results'

train_uir_imp_path = os.path.join(dataset_result_folder, "uir_impression_train.csv")
feedback_train = mind.load_feedback(fpath = train_uir_imp_path)
print(f"Total uir in feedback_train: {len(feedback_train)}")
print(f"feedback_train head 5: {feedback_train[:5]}")

test_uir_imp_path = os.path.join(dataset_result_folder,  "uir_impression_test.csv")
feedback_test = mind.load_feedback(fpath = test_uir_imp_path)

print(f"Total uir in feedback_test: {len(feedback_test)}")
print(f"feedback_test head 5: {feedback_test[:5]}")
import json
import random

history_file_path = os.path.join(dataset_result_folder,  "combined_user_history.json")

with open(history_file_path, 'r') as file:
    user_item_history = json.load(file)


# Print the total number of users in the dictionary
print(f"Total train users in history: {len(user_item_history)}")


# Now, create a new [(u, i,r)]
# Step1. Include all (u-i-r) tuples from feedback_train
new_feedback = list(feedback_train)

# Step 2: Expand history for train users
train_users = {user for user, _, _ in feedback_train}  # Extract users from training set

for user in train_users:
    if user in user_item_history:  # Ensure user has a history
        for item in user_item_history[user]:  # Iterate through the user's history
            new_feedback.append((user, item, 1))  # Assign rating 1

    else:
        print(f"missing train user {user} history" )
# Step 3: Expand history for test users
test_users = {user for user, _, _ in feedback_test}  # Extract users from test set
for user in test_users:
    if user in user_item_history:  # Ensure user has a history
        for item in user_item_history[user]:  # Iterate through the user's history
            new_feedback.append((user, item, 1))  # Assign rating 1
    else:
        print(f"missing test user {user} history" )

## drop duplicates
new_feedback = list(set(new_feedback))



import pandas as pd

# Convert list of tuples into a DataFrame
df_uir = pd.DataFrame(new_feedback, columns=["UserID", "ItemID", "Rating"])



# Define the output file path
output_pld_train_uir_path = os.path.join(dataset_result_folder,  "PLD_uir_trainImp_trainHis_testHis.csv")

# Save to CSV file
df_uir.to_csv(output_pld_train_uir_path, index=False)

print(f"Saved feedback to {output_pld_train_uir_path}")
