# RecSys '24 Challenge

These results are part of a RecSys'24 Challenge submission.
As we are unable to redistribute any of the challenge datasets, please go and download the required datasets at: https://recsys.eb.dk/#dataset

## Overview

This submission uses RP3 Beta random walks from the [Recommenders Repository](https://github.com/Informfully/Recommenders).
To calculate the article ranking shared in the prediction folder, please run the script `sample.py` located in the [Recommender Algorithm Folder](https://github.com/Informfully/Recommenders/tree/main/cornac/models/rp3_beta) folder.
We structure the input data to match the following format (please see the augmentation script and notebook shared in this folder for details):

```python
  # List of articles to populate the graph with article nodes.
  # The labels can be anything as long as the are unique identifiers.
  articleCollection = ["A", "B", "C"]

  # List of users to populate the graph with user nodes.
  # Scores allow to label similar and dissimilar user.
  # The closer the score, the more similar the users.
  # However, scoring is disabled in the current submission. 
  # I.e., all users have the same score.
  userScores = [1, 1, 1]

  # List of user-item interactions to create edges between user and item nodes.
  # The position in the userHistory array indicates the user in userScores.
  # E.g., the third user in userScores read articles B and C.
  userHistory = [["A"], ["B"], ["B", "C"]]
```

## Citation

If you use any code or data of this repository in a scientific publication, we ask you to cite the following papers:

- [Recommendations for the Recommenders: Reflections on Prioritizing Diversity in the RecSys Challenge](https://dl.acm.org/doi/abs/10.1145/3687151.3687155), Heitz *et al.*, Proceedings of the Recommender Systems Challenge 2024, 2024.

  ```
  @inproceedings{heitz2024recommendations,
    title={Recommendations for the Recommenders: Reflections on Prioritizing Diversity in the RecSys Challenge},
    author={Heitz, Lucien and Inel, Oana and Vrijenhoek, Sanne},
    booktitle={Proceedings of the Recommender Systems Challenge 2024},
    pages={22--26},
    year={2024}
  }
  ```

- [Updatable, Accurate, Diverse, and Scalable Recommendations for Interactive Applications](https://dl.acm.org/doi/abs/10.1145/2955101), Paudel *et al.*, ACM Transactions on Interactive Intelligent Systems, 2016.

  ```
  @article{paudel2016updatable,
    title={Updatable, accurate, diverse, and scalable recommendations for interactive applications},
    author={Paudel, Bibek and Christoffel, Fabian and Newell, Chris and Bernstein, Abraham},
    journal={ACM Transactions on Interactive Intelligent Systems (TiiS)},
    volume={7},
    number={1},
    pages={1--34},
    year={2016},
    publisher={ACM New York, NY, USA}
  }
  ```
