#!/bin/bash

if [[ "${cumulus_env_id}" == "SNDBX" ]]; then
  secrets_file="${LP_CUMULUS_SNDBX_EXPORTS_FILE}"
elif [[ "${cumulus_env_id}" == "SIT" ]]; then
  secrets_file="${LP_CUMULUS_SIT_EXPORTS_FILE}"
elif [[ "${cumulus_env_id}" == "UAT" ]]; then
  secrets_file="${LP_CUMULUS_UAT_EXPORTS_FILE}"
elif [[ "${cumulus_env_id}" == "PROD" ]]; then
  secrets_file="${LP_CUMULUS_PROD_EXPORTS_FILE}"
else
  echo "cumulus_env_id ${cumulus_env_id} is not supported!"
  exit 1
fi
