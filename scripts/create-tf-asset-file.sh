#!/bin/bash

# construct the Terraform module zip file

filename=${1}
cp terraform/* .
zip -r ${filename} lambda_functions.tf main.tf outputs.tf variables.tf

# TESTING ONLY
zipinfo ${filename}
