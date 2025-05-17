# Party Classification Preprocessing for PLD and EPD Experiments

## Overview

For **Mind**, **Republican**, and **Democratic** party are defined in the experiments, the enriched raw party data can be used as-is.

However, for experiments on the **NeMig** (Germany) and **Eb-Nerd** (Denmark) datasets, party classification is based on **three categories**:
- `GOV_PARTIES` — government parties
- `OPP_PARTIES` — opposition parties
- `INDEP_FOREIGN_PARTIES` — independent or foreign entities

The current PLD and EPD processing scripts now best support two-party input formats. Therefore, a **preprocessing step is required** to map the raw enriched parties into the supported format.

---

## Step-by-Step: Example Conversion

### Input Format (Raw Party Enrichment)

```json
{
  "news_0": {
    "Christian Democratic Union": 1
  },
  "news_1": {},
  "news_2": {},
  "news_3": {
    "German Communist Party": 1,
    "Party of Democratic Socialism": 1,
    "Labour Party": 1
  },
  "news_4": {
    "Social Democratic Party of Switzerland": 1
  },
  "news_5": {
    "The Left": 2,
    "Die Linke": 2,
    "Party of Democratic Socialism": 2,
    "Social Democratic Party of Germany": 2
  }
}
````

### Configuration (e.g., for NeMig)

```python
gov_parties = {
    "Social Democratic Party of Germany", "Alliance '90/The Greens", "Free Democratic Party"
}

opp_parties = {
    "Christian Democratic Union", "Christian Social Union of Bavaria","Alternative for Germany", "The Left", "South Schleswig Voters' Association"
}
```

### Expected Output (Mapped Format)

```json
{
  "news_0": {
    "OPP_PARTIES": 1
  },
  "news_1": {},
  "news_2": {},
  "news_3": {
    "INDEP_FOREIGN_PARTIES": 3
  },
  "news_4": {
    "INDEP_FOREIGN_PARTIES": 1
  },
  "news_5": {
    "OPP_PARTIES": 2,
    "INDEP_FOREIGN_PARTIES": 4,
    "GOV_PARTIES": 2
  }
}
```

---

## Notes

- **Conversion is required** before running PLD/EPD experiment scripts on the **NeMig** and **Eb-Nerd** datasets.  
  This step is **not necessary** for the **Mind** dataset, where raw party enrichment can be used directly.

- Any party **not listed** in either the `gov_parties` or `opp_parties` sets will be automatically categorized as `INDEP_FOREIGN_PARTIES`.

- Party counts (i.e., the numeric values in the input) are **retained and summed** within each classified group (`GOV_PARTIES`, `OPP_PARTIES`, `INDEP_FOREIGN_PARTIES`).


## PLD Train U-I-R

PLD requires user-item interaction from train impression logs, train user history, and test user history.
Therefore, we provide a script for generating it:
**`PLD_train_uir_processing.py`**

The idea is it incorporates train impression logs, train user history, and test user history.

### Required Files

Before running the script, ensure the following files are prepared:

* `uir_impression_train.csv` — user–item–rating interactions from the training set impression logs
* `uir_impression_test.csv` — user–item–rating interactions from the test set impression logs
* `combined_user_history.json` — browsing history per user

Refer to `neural_preparation/README.md` for instructions on how to generate these files.

### Output

* The output file is:
  **`PLD_uir_trainImp_trainHis_testHis.csv`**
  
  By default, it is saved in the `{datasetname}_results` folder.