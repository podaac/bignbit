# About

bignbit is a Cumulus module that can be installed as a post-ingest workflow to generate browse imagery via Harmony and then transfer that imagery to GIBS.

See an example of how to use this cumulus module in [browse_image_workflow.tf](/examples/cumulus-tf/browse_image_workflow.tf).

_Visual representation of the bignbit step function state machine:_  
![image](https://github.com/podaac/bignbit/assets/89428916/4db5ae4b-ca74-4bee-bee7-2d7d1a342bd7)

# Assumptions
 - Using `ContentBasedDeduplication` strategy for GITC input queue

# Local Development
## MacOS

1. Install miniconda (or conda) and [poetry](https://python-poetry.org/)
2. Run `conda env create -f conda-environment.yaml` to install GDAL
3. Activate the bignbit conda environment `conda activate bignbit`
4. Install python package and dependencies `poetry install`
5. Verify tests pass `poetry run pytest tests/`
