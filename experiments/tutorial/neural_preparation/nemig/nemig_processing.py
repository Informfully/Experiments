import sys
import pandas as pd
import numpy as np
import json
import os

input_folder = './nemig_input'

# Step 1: Load NeMig dataset behaviors
behaviors_path = os.path.join(input_folder, 'behaviors.tsv')
behaviors_column_names = ['Impression ID', 'User ID', 'History', 'Impressions']
df_behavior = pd.read_csv(behaviors_path, sep='\t', encoding='utf-8', header=None, names=behaviors_column_names)

unique_user_ids = df_behavior['User ID'].unique()

# Filter users with empty or missing history
no_history_df = df_behavior[df_behavior['History'].isna() | (df_behavior['History'].str.strip() == '')]

# Display users without history
print("Users with no history:")
print(no_history_df[['User ID', 'History']])
print(f"total users: {len(unique_user_ids)}")
missing_his_user_ids = no_history_df['User ID'].unique()
print(f"len missing his users: {len(missing_his_user_ids)}")

# Step 4: Remove no-history users from df_behavior
df_behavior_cleaned = df_behavior[~df_behavior['User ID'].isin(missing_his_user_ids)]

# Optional: Check remaining users
print(f"Users after cleanup: {df_behavior_cleaned['User ID'].nunique()}")


#---------------------------------------------
# Check every user's number of rows.
user_counts = df_behavior['User ID'].value_counts()


# we found every user has exactly 5 rows.
all_have_five = (user_counts == 5).all()

if all_have_five:
    print("Every user has exactly 5 rows.")
else:
    print("Not all users have 5 rows.")
    print("\nUsers with row counts other than 5:")
    print(user_counts[user_counts != 5])

#---------------------------------------------
#  Because NeMig doesn't provide splitted train and test set.
# Here we apply 80%/20% split. 
# Randomly sample 20% entry per user to form the test set.


# Sample 1 row per user for the test set
df_val_behaviors = df_behavior_cleaned.groupby('User ID', group_keys=False).sample(n=1, random_state=42).copy()

# The rest go to the train set
df_train_behaviors = df_behavior_cleaned.drop(index=df_val_behaviors.index).copy()

print(f"Test set size: {len(df_val_behaviors)}")
print(f"Train set size: {len(df_train_behaviors)}")



dataset_result_folder =  './nemig_results'
incompelete_article_path = os.path.join(dataset_result_folder, "incomplete_article_ids.txt")
with open(incompelete_article_path, "r") as file:
    incomplete_ids = [line.strip() for line in file if line.strip()]

incomplete_ids_set = set(incomplete_ids)
print(f" len incomplete_ids_set:{len(incomplete_ids_set)}")


### Helper functions
def aggregate_data_by_userid(df):
    """
    Aggregate data by user ID while considering both 'History' and 'Impressions' columns.

    Parameters:
    -----------
    df : pandas DataFrame
        DataFrame containing the 'User ID', 'History', and 'Impressions' columns.

    Returns:
    --------
    pandas DataFrame
        DataFrame with aggregated data where each row corresponds to a unique user ID.
    """
    # Initialize an empty list to store the aggregated data
    agg_data = []

    # Replace NaN values with an empty string
    df['History'] = df['History'].fillna('')
    df['Impressions'] = df['Impressions'].fillna('')

    # Group the data by 'User ID'
    grouped = df.groupby('User ID')

    # Iterate over each group
    for user_id, group_df in grouped:
        # Aggregate history items
        history_items = set()
        for history in group_df['History']:
            history_items.update(str(history).split())

        # Aggregate impressions
        impressions_items = set()
        for impression in group_df['Impressions']:
            impressions_items.update(str(impression).split())

        # Append the aggregated data to the list
        agg_data.append({'User ID': user_id, 'History': history_items, 'Impressions': impressions_items})

    # Convert the list of dictionaries to a DataFrame
    agg_data_df = pd.DataFrame(agg_data)

    return agg_data_df

# Function to generate history, and (user-item-rating) format

def generate_user_item_rating(df):
    user_item_ratings = []
    history = {}
    for index, row in df.iterrows():
        user_id = row['User ID']
        history_items = ' '.join(row['History']).split()
        impressions_items = ' '.join(row['Impressions']).split()
        if user_id not in history:
            history[user_id] = []
        for item_id in history_items:
            if item_id not in incomplete_ids_set and item_id not in history[user_id]:
                history[user_id].append(item_id)
        for impressions_item in impressions_items:
            item_id, rating = impressions_item.split('-')[0], 0
            if item_id not in incomplete_ids_set:
                if f"{item_id}-1" in impressions_items:
                    rating = 1
                user_item_ratings.append((user_id, item_id, rating))
    return history, user_item_ratings

def set_ratings_based_on_third_column(input_data):
    """
    Set ratings based on the third column of the input data.
    If there is any 1 in the third column, set rating to 1.
    If all values in the third column are 0, set rating to 0.

    Parameters
    ----------
    input_data : list of tuples
        List of tuples where each tuple contains three elements: (user, item_id, rating).

    Returns
    -------
    list of tuples
        List of tuples with modified ratings.
    """
    '''
    ratings = {}
    for user, item, rating in input_data:
        key = (user, item)
        # Update rating to 1 if it's 1 or if the key doesn't exist yet
        if rating == 1 or key not in ratings:
            ratings[key] = rating
    print('first part finish')
    # Update ratings with 0 values to 1 if any corresponding key has a rating of 1
    for user, item, rating in input_data:
        key = (user, item)
        if ratings[key] == 0 and any(r == 1 for u, i, r in input_data if u == user and i == item):
            ratings[key] = 1

    return [(user, item, rating) for (user, item), rating in ratings.items()]
    '''
    ratings = {}
    for user, item, rating in input_data:
        key = (user, item)
        # Update rating to 1 if it's 1 or if the key doesn't exist yet
        if rating == 1 or key not in ratings:
            ratings[key] = rating

    return [(user, item, rating) for (user, item), rating in ratings.items()]

#---------------------------------------------
# Aggregate train data
print('aggregate for train set begin.....')
df_train_aggregate = aggregate_data_by_userid(df_train_behaviors)
print('aggregate train set finish')
# Generate the (user-item-rating) format
print('generate train (user-item-rating) format begin')
train_history, train_user_item_ratings = generate_user_item_rating(df_train_aggregate)
print('generate train (user-item-rating) format finish')
print('set_ratings_based_on_third_column begin')
train_user_item_tuple = set_ratings_based_on_third_column(train_user_item_ratings)
print('set_ratings_based_on_third_column finish')

#---------------------------------------------
# Aggregate test data
print('aggregate for test set begin.....')
df_test_aggregate = aggregate_data_by_userid(df_val_behaviors)
print('aggregate test set finish')
# Generate the (user-item-rating) format
print('generate test (user-item-rating) format begin')
test_history, test_user_item_ratings = generate_user_item_rating(df_test_aggregate)
print('generate test (user-item-rating) format finish')
print('set_ratings_based_on_third_column begin')
test_user_item_tuple = set_ratings_based_on_third_column(test_user_item_ratings)
print('set_ratings_based_on_third_column finish')


#---------------------------------------------
# Combine train set and test set user history
combined_user_history = train_history.copy()

# Add users from test who are not already in train
for user, history in test_history.items():
    if user not in combined_user_history:
        combined_user_history[user] = history

print(f"Total users in combined history: {len(combined_user_history)}")

#---------------------------------------------
# For train impression U-I-R: removing duplicates
seen_train = set()
filtered_train_tuples = []
for user, item, rating in train_user_item_tuple:
    if (user, item) not in seen_train:
        seen_train.add((user, item))
        filtered_train_tuples.append((user, item, rating))


#---------------------------------------------
# Clean Test impression U-I-R: removing test users whose history is empty
unique_test_users = set(user for user, _, _ in test_user_item_tuple)
missing_users = unique_test_users - set(combined_user_history.keys())
print(missing_users)


#  Remove duplicates based on (user, item)
seen = set()
filtered_test_tuples = []
for user, item, rating in test_user_item_tuple:
    if (user, item) not in seen:
        seen.add((user, item))
        filtered_test_tuples.append((user, item, rating))

#  Remove tuples where user is in missing_users
filtered_test_tuples = [t for t in filtered_test_tuples if t[0] not in missing_users]




#---------------------------------------------
## Save train U-I-R impression csv file
train_uir_imp_path = os.path.join(dataset_result_folder,  "uir_impression_train.csv")
train_user_item_ratings_df = pd.DataFrame(filtered_train_tuples, columns=['UserID', 'ItemID', 'Rating'])

train_user_item_ratings_df.to_csv(train_uir_imp_path, index=False)


# ## Save test U-I-R impression csv file
test_uir_imp_path = os.path.join(dataset_result_folder,  "uir_impression_test.csv")
test_user_item_ratings_df = pd.DataFrame(filtered_test_tuples, columns=['UserID', 'ItemID', 'Rating'])

# Save the DataFrame to a CSV file
test_user_item_ratings_df.to_csv(test_uir_imp_path, index=False)


## Save user-item-history json file.
output_file_path = os.path.join(dataset_result_folder,  "combined_user_history.json")


with open(output_file_path, 'w') as file:
    json.dump(combined_user_history, file, indent=4)


# the unique item IDs in the Test impression Logs are used as our article pool in our experiment
# we saved the raw article ids
unique_item_ids = test_user_item_ratings_df['ItemID'].unique()
print(unique_item_ids)

output_articlePool_path = os.path.join(dataset_result_folder,  "article_pool.csv")

df = pd.DataFrame({'iid': unique_item_ids})

# Save to CSV
df.to_csv(output_articlePool_path, index=False)