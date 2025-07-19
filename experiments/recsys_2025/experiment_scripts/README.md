# Recommendation Model Execution

This folder contains scripts for running recommendation models.

## Usage Instructions

* Follow the instructions provided in each script.
* For different datasets, if you have followed the **data preparation scripts** beforehand, the **file naming conventions are unified**.
* Simply specify the **input path** to the correct `{datasetname}_results` folder when executing a script.

## Notes on Hyperparameters

* Hyperparameter differences across datasets or models are commented within each `{model}_experiment.py` script.
* D-DRDW Prerequisites:  Before running D-DRDW, ensure that enriched features for the diversity dimensions you want to diversify are complete for all articles included in the graph.
Incomplete features may limit the model’s ability to promote diversity.

<!--
## Citation

If you use any code or data from this repository in a scientific publication, we ask you to cite the following paper:

* [D-RDW: Diversity-Driven Random Walks for News Recommender Systems](TBD), Li *et al.*, Proceedings of the 19th ACM Conference on Recommender Systems, 2025.

  ```
  @inproceedings{li2025diversity,
    title={D-RDW: Diversity-Driven Random Walks for News Recommender Systems},
    author={Li, Runze and Heitz, Lucien and Inel, Oana and Bernstein, Abraham},
    booktitle={Proceedings of the 19th ACM Conference on Recommender Systems},
    pages={TBD},
    year={2025}
  }
  ```
  -->
