# Informfully Experiments

![Informfully](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/logo_banner.png)

Welcome to Informfully ([GitHub](https://github.com/orgs/Informfully) & [Website](https://informfully.ch/))!
Informfully is an open-source reproducibility platform for content distribution and user experiments.

**Links and Resources:** [GitHub](https://github.com/orgs/Informfully) | [Website](https://informfully.ch) | [X](https://x.com/informfully) | [Documentation](https://informfully.readthedocs.io) | [DDIS@UZH](https://www.ifi.uzh.ch/en/ddis.html) | [Google Play](https://play.google.com/store/apps/details?id=ch.uzh.ifi.news) | [App Store](https://apps.apple.com/us/app/informfully/id1460234202)

## Overview

This repository contains all the experiment configuration files and hyperparameters to reproduce the findings of our papers and research that use the [Informfully Recommenders](https://github.com/Informfully/Recommenders).
For an overview of how to run the experiment workflows shared here, please follow go through the tutorial below.
The tutorial includes a step-by-step instructions to download the codebase necessary for running all the models listed here.

| Experiment | Documentation | Resources |
|-|-|-|
| Informfully Recommenders Tutorial (forthcoming) | [README](https://github.com/Informfully/Experiments/tree/main/experiments/tutorial) | [Codebase](https://github.com/Informfully/Recommenders) |
| [ACM RecSys '23 Paper](https://dl.acm.org/doi/abs/10.1145/3604915.3608834) | [README](https://github.com/Informfully/Experiments/tree/main/experiments/recsys_paper_2023) | [Parameters](TBD), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/epd) |
| [ACM RecSys '24 Challenge](https://dl.acm.org/doi/abs/10.1145/3687151.3687155) | [README](https://github.com/Informfully/Experiments/tree/main/experiments/recsys_challenge_2024) | [Parameters](TBD), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/rp3_beta) |
| ACM RecSys '25 Paper (forthcoming) | [README](https://github.com/Informfully/Experiments/blob/main/experiments/tutorial/experiment_scripts/README.md) | [Parameters](https://github.com/Informfully/Experiments/blob/main/experiments/tutorial/experiment_scripts/drdw_experiment.py), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/drdw) |
<!-- | [Digital Journalism Paper](https://www.tandfonline.com/doi/full/10.1080/21670811.2021.2021804) | [README](TBD) | [Parameters](TBD),[Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/pld) | -->
<!-- | [Journal of Communication Paper](TBD) | [README](TBD) | [Parameters](TBD),[Model](TBD) | -->

## Citation

If you use any code or data from this repository in a scientific publication, we ask you to cite the following paper:

- [Informfully - Research Platform for Reproducible User Studies](https://dl.acm.org/doi/10.1145/3640457.3688066), Heitz *et al.*, Proceedings of the 18th ACM Conference on Recommender Systems, 2024.

  ```
  @inproceedings{heitz2024informfully,
    title={Informfully - Research Platform for Reproducible User Studies},
    author={Heitz, Lucien and Croci, Julian A and Sachdeva, Madhav and Bernstein, Abraham},
    booktitle={Proceedings of the 18th ACM Conference on Recommender Systems},
    pages={660--669},
    year={2024}
  }
  ```

## Contributing

You are welcome to contribute to the Informfully ecosystem and become a part of our community.
Feel free to:

- Fork any of the [Informfully repositories](https://github.com/Informfully/Documentation).
- Suggest new features in [Future Release](https://github.com/orgs/Informfully/projects/1).
- Make changes and create pull requests.

Please post your feature requests and bug reports in our [GitHub issues](https://github.com/Informfully/Documentation/issues) section.

## License

Released under the [MIT License](LICENSE). (Please note that the respective copyright licenses of third-party libraries and dependencies apply.)

![Screenshots](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/app_screens.png)
