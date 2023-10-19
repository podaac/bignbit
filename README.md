# About

bignbit combines the Browse Image Generator (BIG) and the PO.DAAC Browse Image Transfer (pobit) modules


# Assumptions
 - Using `ContentBasedDeduplication` strategy for GITC input queue

# Local Development
## MacOS

1. Install miniconda (or conda) and [poetry](https://python-poetry.org/)
2. Run `conda env create -f conda-environment.yml` to install GDAL
3. Activate the bignbit conda environment `conda activate bignbit`
4. Install python package and dependencies `poetry install`
5. Verify tests pass `poetry run pytest tests/`