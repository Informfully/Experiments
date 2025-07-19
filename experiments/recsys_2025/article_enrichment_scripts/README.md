
# Article Enrichment Scripts

This folder contains scripts for generating enriched textual features used in experiments such as running diversity models, re-ranking, and diversity metric evaluation.


## Step 1: Clean the Dataset

Before enrichment, you must clean the input dataset to remove incomplete articles. Each article must have the following columns in the CSV file:

- `id`
- `title`
- `text`
- `category`
- `date`

Any article missing one or more of these fields is considered **incomplete** and will be removed.

### Output:
Two files will be saved to the `{{datasetname}}_results/` folder:

1. `cleaned_articles.csv` — all valid articles
2. `incomplete_article_ids.txt` — IDs of removed/incomplete articles




## Step 2: Run Article Enrichment

Use `article_enrich.py` to enrich the cleaned dataset. First, choose the appropriate config file for your dataset:

```python
import config_ebnerd as config
# or
import config_nemig as config
# or
import config_mind as config
```

Then, make sure that:

* The path to input_file_path `cleaned_articles.csv` is correctly set.
* The output path for the enriched JSON files is defined (typically inside the same `{{datasetname}}_results/` folder).

### Note

* The enrichment script is the same for all datasets.
* Just make sure the correct `config_*.py` file is imported and properly configured.

---

## Enrichment Output Files

Each enrichment step produces a corresponding `.json` file containing structured annotations for each article:

| File                           | Description |
|-------------------------------|-------------|
| `category.json`                | Classifies articles into categories using Zero-Shot classification, or if category metadata is available, it is used directly. |
| `readability.json`             | Computes readability metrics such as Flesch-Kincaid Grade Level. |
| `sentiment.json`              | Assigns sentiment scores in the range **-1 to 1**, where negative values indicate negative sentiment, positive values indicate positive sentiment, and values near 0 indicate neutrality. |
| `named_entities.json`          | Extracts named entities (e.g., persons, organizations, locations). |
| `enriched_named_entities.json` | Augments extracted entities with metadata from Wikidata (e.g., occupation, affiliations for persons and organizations). |
| `region.json`                  | Maps geopolitical entities (countries, cities, regions) to predefined regions using Wikidata lookups. |
| `party.json`                   | Identifies and quantifies the political affiliations and ideologies expressed in the text, whether through individuals or organizations.|
| `min_maj_ratio.json`           | Computes **minority-majority ratios** by enriching named persons with demographic attributes (e.g., gender, ethnicity, citizenship, place of birth). |
| `story.json`                   | Groups articles into **story chains**—clusters of articles reporting on the same event.  |
