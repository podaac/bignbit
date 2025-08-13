# BIGnBIT Module In Cumulus Deployment (cumulus-tf)
- BIGnBIT Module used in `cumulus-deploy-tf/cumulus-tf`
  - Module Name: `big_and_bit_module`
    - Source ZIP: `https://github.com/podaac/bignbit/releases/download/0.1.2/bignbit-0.1.2-cumulus-tf.zip`
    - lambda_container_image_uri: `ghcr.io/podaac/bignbit/bignbit:0.1.2`

## Terraform ZIP

- variables.tf
- outputs.tf
- main.tf
- lambda_functions.tf
- state_machine_definition.json


# Deployment example

This terraform can be deployed from the local command line or via GitHub Actions.

## Local Deployment
If you are trying to deploy a local build, you must first build the docker image and tag it. For example:
```bash
# If building on a newer Mac, you will need to specify the platform
docker buildx build --platform linux/amd64 --load -t ghcr.io/podaac/bignbit/bignbit:0.4.0a2-cd2fbe2 -f docker/Dockerfile .

# Otherwise, you can just build it directly
docker build -t ghcr.io/podaac/bignbit/bignbit:0.4.0a2-cd2fbe2 -f docker/Dockerfile .
```

To deploy from the command line, you must obtain valid AWS credentials then run:
```bash
export AWS_PROFILE=ngap-service-sit
export tf_venue=sit

# backend-config should specify an s3 bucket that exists in the AWS account associated with the profile being used
# This is where terraform state will be stored. This example uses a bucket named `podaac-services-sit-terraform`
terraform init -reconfigure -input=false -backend-config="bucket=podaac-services-${tf_venue}-terraform"

# app_version should match the version of the software being deployed
export app_version=0.4.0a2+cd2fbe2
# lambda_container_image_uri should match the tag of the docker image that was built or pulled
# IMPORTANT: the '+' in the app_version must be replaced with '-' to be a valid docker tag
export lambda_container_image_uri=ghcr.io/podaac/bignbit/bignbit:0.4.0a2-cd2fbe2
terraform plan -input=false -var-file=tfvars/"${tf_venue}".tfvars -var="app_version=${app_version}" -var="lambda_container_image_uri"=${lambda_container_image_uri} -out="tfplan"

terraform apply -input=false -auto-approve tfplan
```

Alternatively, it is possible to deploy using the deploy.sh script, which will handle the above steps for you:
```bash
export AWS_PROFILE=ngap-service-sit
cd examples/cumulus-tf
./bin/deploy.sh --app-version 0.4.0a2+cd2fbe2 --tf-venue sit --lambda_container_image_uri ghcr.io/podaac/bignbit/bignbit:0.4.0a2-cd2fbe2
```

## GitHub Actions Deployment
The (CICD GitHub workflow)[https://github.com/podaac/bignbit/actions/workflows/cicd-pipeline.yml] is setup to allow deployments 
via workflow dispatch to the SIT environment from branches that match the following patterns:
- develop
- feature/*
- issue/*
- issues/*

If your work is being done on a feature or issue branch, the easiest way to deploy is to commit your changes and the use
the workflow dispatch option in the GitHub Actions UI to trigger a deployment to SIT.