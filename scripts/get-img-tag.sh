#!/bin/bash

# construct a tag for the Docker image

branch=${1}

if [[ "${branch}" =~ ^feature\/.* ]]; then
  tag="${branch//\//-}"
elif [[ "${branch}" =~ ^develop$ ]]; then
  tag="develop"
elif [[ "${branch}" =~ ^hotfix\/.* ]]; then
  tag=$(echo "${branch}" | grep -Eo "[^hotfix\/v](.*)")
elif [[ "${branch}" =~ ^release\/.* ]]; then
  tag=$(echo "${branch}" | grep -Eo "[^release\/v](.*)")
else
  tag="${branch//\//-}"
fi

# replace any invalid charaters
match="[^A-Za-z0-9_\.\-]"
replace="-"
tag=${tag//$match/$replace}

echo "${tag}"
