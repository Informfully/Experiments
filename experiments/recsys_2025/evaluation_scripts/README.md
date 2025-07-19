
# Evaluation Scripts

This folder contains scripts for evaluating recommendations across **accuracy** and **diversity** dimensions.

---

## Accuracy Evaluation

We use **AUC** and **pairwise comparison** based on impression logs:

- For each test impression, if the **a clicked article's score** is higher than **an unclicked articles**, it is counted as a **correct pair**.

## Diversity Evaluation

Diversity is measured using the **Top-20 recommendation list** per user.

### Step 1: Generate Top-20 Lists

For recommendation models that generate a candidate list, this step is required to have a top20 list. For Models like D-RDW that directly generate a recommendation list at target size, this step is not needed.

This script filters out:

* Articles the user has already clicked (from user history or training impression logs)
* Then saves the top-20 articles per user.

### Step 2: Prepare Feature Vectors

Diversity metrics such as **intra-list diversity** require feature vectors for:

* **Sentiment**
* **Party**
* **Category**

Use the following scripts:

* `generate_party_one_hot.py`
* `generate_senti_one_hot.py`

>  Note:
>
> * For **NeMig**, we use a **2D sentiment vector**.

```
def sentiment_to_one_hot(score):
    if -1 <= score < 0:
        return [1, 0]
    elif 0 <= score < 1.01:
        return [0, 1]
```

> * For **Mind** and **EB-NERD**, we use a **4D sentiment vector** (see `generate_senti_one_hot.py`).

## Party One-Hot Encoding
The provided script processes EB_NERD dataset.

For NeMig Dataset, only the definitions of party categories differ. Use the same processing scripts.

```python
gov_parties = {
    "Social Democratic Party of Germany", "Alliance '90/The Greens", "Free Democratic Party"
}

opp_parties = {
    "Christian Democratic Union", "Christian Social Union of Bavaria",
    "Alternative for Germany", "The Left", "South Schleswig Voters' Association"
}
```

For MIND, 

```python
DEM = "democratic party"
REP = "republican party"

def party_to_one_hot(mentions):
    if not isinstance(mentions, dict):
        return [0, 0, 0, 0, 1]  # No party

    mentions_lower = {key.lower(): value for key, value in mentions.items()}
    has_dem = DEM in mentions_lower
    has_rep = REP in mentions_lower
    has_other = any(p not in [DEM, REP] for p in mentions_lower)

    if has_dem and not has_rep and not has_other:
        return [1, 0, 0, 0, 0]
    elif has_rep and not has_dem and not has_other:
        return [0, 1, 0, 0, 0]
    elif has_dem and has_rep and not has_other:
        return [0, 0, 1, 0, 0]
    elif has_other:
        return [0, 0, 0, 1, 0]
    return [0, 0, 0, 0, 1]
```

## RADio Metrics

### Setup

* The **article pool** (from train + test sets) is saved in a `.csv` file.
* **User history** is generated during data preparation.

## For Representation Metric

Use `party_binary.py` to convert `party.json` into `entities_binary_count.json`.

### Example

**Input (`party.json`):**

```json
{
  "article_1": {},
  "article_2": { "partyA": 2, "partyC": 3 }
}
```

**Output (`entities_binary_count.json`):**

```json
{
  "article_1": { "No party": 1 },
  "article_2": { "partyA": 1, "partyC": 1 }
}
```

This binary format indicates which parties are **present** in each article (ignoring frequency), and assigns `"No party"` if none are present.
