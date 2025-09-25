# Recommendation Files

We share the item recommendations for the following datasets:

* EB-NeRD ([Website](https://recsys.eb.dk), small version used)
* MIND ([Website](https://msnews.github.io), small version used)
* NeMig ([Website](https://github.com/andreeaiana/nemig), full version used)

The following pre-processing steps were applied

* Removal of invalid articles/items (i.e., articles without text, such as slideshows or videos/trailers).
* Removal of invalid article ID from all user histories.
* Removal of all users with empty history.

Each recommendation file is structured as follows:

* [userID_1]: [itemID_A, itemID_B, ...]
* [userID_2]: [itemID_X, itemID_Y, ...]

Items are ordered by their prediction score in descending order.
The values for each 'userID' and 'itemID' to the IDs of the original dataset.

## Collection

This folder contains the following two collections

* Top 20 (shared as part of this repository)
* Full (requires download from [external server](https://seafile.ifi.uzh.ch/d/fe211ba2fcfd4551aa1a))

'Top 20' includes the top 20 items for each user (i.e., the items with the highest prediction score).
'Full' contains the complete ranked ordering of **ALL** items in the respective dataset for **ALL** users.

## Models

The folders of 'Top 20' and 'Full' contain recommendations from the following algorithms:

* DRDW ([Paper](https://arxiv.org/abs/2508.13035))
* EPD ([Paper](https://doi.org/10.1145/3604915.3608834), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/epd))
* LSTUR ([Paper](https://aclanthology.org/P19-1033), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/lstur))
* NPA ([Paper](https://dl.acm.org/doi/abs/10.1145/3292500.3330665), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/npa))
* NRMS ([Paper](https://aclanthology.org/D19-1671), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/nrms))
* PLD ([Paper](https://doi.org/10.1080/21670811.2021.2021804), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/pld))
* RP3B ([Paper](https://dl.acm.org/doi/abs/10.1145/2792838.2800180), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/rp3_beta))
* RWED ([Paper](https://dl.acm.org/doi/abs/10.1145/3442381.3449970), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/models/rwe_d))
* RANDOM

## Re-rankers

The folder of 'Top 20' contains re-ranked recommendations with the following combination of models and re-rankers:

* LSTUR_DYN_ATT ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* LSTUR_DYN_POS ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* LSTUR_GKL ([Paper](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/greedy_kl), [Code](https://github.com/Informfully/Recommenders/blob/main/cornac/metrics/diversity.py))
* LSTUR_MMR ([Paper](https://dl.acm.org/doi/pdf/10.1145/290941.291025), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/mmr))
* LSTUR_PM2 ([Paper](https://dl.acm.org/doi/abs/10.1145/2348283.2348296), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/pm2))
* NPA_DYN_ATT ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* NPA_DYN_POS ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* NPA_GKL ([Paper](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/greedy_kl), [Code](https://github.com/Informfully/Recommenders/blob/main/cornac/metrics/diversity.py))
* NPA_MMR ([Paper](https://dl.acm.org/doi/pdf/10.1145/290941.291025), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/mmr))
* NPA_PM2 ([Paper](https://dl.acm.org/doi/abs/10.1145/2348283.2348296), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/pm2))
* NRMS_DYN_ATT ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* NRMS_DYN_POS ([Paper](https://arxiv.org/abs/2508.13035), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/dynamic_attribute_penalization))
* NRMS_GKL ([Paper](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/greedy_kl), [Code](https://github.com/Informfully/Recommenders/blob/main/cornac/metrics/diversity.py))
* NRMS_MMR ([Paper](https://dl.acm.org/doi/pdf/10.1145/290941.291025), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/mmr))
* NRMS_PM2 ([Paper](https://dl.acm.org/doi/abs/10.1145/2348283.2348296), [Code](https://github.com/Informfully/Recommenders/tree/main/cornac/rerankers/pm2))
