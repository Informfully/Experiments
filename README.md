# Informfully Experiments

![Informfully](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/logo_banner.png)

Welcome to Informfully ([GitHub](https://github.com/orgs/Informfully) & [Website](https://informfully.ch/))!
Informfully is an open-source reproducibility platform for content distribution and user experiments.

**Links and Resources:** [GitHub](https://github.com/orgs/Informfully) | [Website](https://informfully.ch) | [X](https://x.com/informfully) | [Documentation](https://informfully.readthedocs.io) | [DDIS@UZH](https://www.ifi.uzh.ch/en/ddis.html) | [Google Play](https://play.google.com/store/apps/details?id=ch.uzh.ifi.news) | [App Store](https://apps.apple.com/us/app/informfully/id1460234202)

## Overview

This repository contains all the experiment scripts (configuration files and hyperparameters) to reproduce the findings of our papers and research that use the [Informfully Recommenders](https://github.com/Informfully/Recommenders).
For an overview of how to run the experiment workflows shared here, please follow go through the tutorial below.
The tutorial includes a step-by-step instructions to download the codebase necessary for running all the models listed here.

| Experiment | Resources |
|-|-|
| Benefits of Diverse News Recommendations for Democracy (DJ '22) | [Paper](https://www.tandfonline.com/doi/full/10.1080/21670811.2021.2021804), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/epd) |
| Deliberative Diversity for News Recommendations (RecSys '23) | [Paper](https://dl.acm.org/doi/abs/10.1145/3604915.3608834), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/epd), [Scripts](https://github.com/Informfully/Experiments/tree/main/experiments/recsys_2023) |
| Random Walks for Diverse News Recommendations (RecSys '24) | [Paper](https://dl.acm.org/doi/abs/10.1145/3687151.3687155), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/rp3_beta), [Scripts](https://github.com/Informfully/Experiments/tree/main/experiments/recsys_2024) |
| Position and Accessibility Nudges for Environmental News (NORMalize '24) | [Paper](https://ceur-ws.org/Vol-3898/paper1.pdf), [Scripts](https://github.com/Informfully/Experiments/tree/main/experiments/normalize_2024), [Dataset](https://github.com/Informfully/Datasets/tree/main/IDEA)|
| Diversity-Driven Random Walks (RecSys '25) | [Paper](https://github.com/lucienheitz/lucienheitz/blob/main/papers/li2025drdw.pdf), [Model](https://github.com/Informfully/Recommenders/tree/main/cornac/models/drdw), [Scripts](https://github.com/Informfully/Experiments/blob/main/experiments/recsys_2025/graph_preparation/README.md) |

## Tutorial

Please see the [Informfully Recommenders Tutorial](https://github.com/Informfully/Experiments/tree/main/experiments/recsys_2025) for instructions on how to work with our scripts and recommendation pipelines.
To get started, you first need to download codebase we share in the repository of the [Recommender Framework](https://github.com/Informfully/Recommenders).

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
