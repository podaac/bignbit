#!/bin/bash

# construct a filename for the Terraform asset

base=${1}
branch=${2}
extension="zip"

if [[ "${branch}" =~ ^feature\/.* ]]; then
  branch_slug="${branch//\//-}"
elif [[ "${branch}" =~ ^develop$ ]]; then
  branch_slug="develop"
elif [[ "${branch}" =~ ^hotfix\/.* ]]; then
  branch_slug=$(echo "${branch}" | grep -Eo "[^hotfix\/v](.*)")
elif [[ "${branch}" =~ ^release\/.* ]]; then
  branch_slug=$(echo "${branch}" | grep -Eo "[^release\/v](.*)")
else
  branch_slug="${branch//\//-}"
fi

# replace any invalid charaters
match="[^A-Za-z0-9_\.\-]"
replace="-"
branch_slug=${branch_slug//$match/$replace}

echo "${base}-${branch_slug}.${extension}"
