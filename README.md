# About

bignbit combines the Browse Image Generator (BIG) and the PO.DAAC Browse Image Transfer (pobit) modules. BIG is used to generate browse imagery via GDAL harmony image creation service. Pobit transfers the images to GITC.

# Developers
  * clone the repo
  * create a virtual environment:  conda env create -f conda-environment.yaml

# Implementation
    TODO: Gitlab pipeline was ported to Github Actions. It's in .github/workflows/browse-image-generator.yml. No work has been done on it yet to get it running. The CI/CD documentation below will need to be updated as well. The gitlab pipeline pushed the image to Nexus. Use Github instead?
    TODO: Get Nexus credentials out of the pipeline

  * Use commands below to add values to the AWS Systems Manager Parameter store:
    ```
    aws ssm put-parameter --region us-west-2 --profile `<your profile>`  --name "<prefix>-urs_<daac>cloud_user" --value "<var.cmr_username>" --type "String"
    aws ssm put-parameter --region us-west-2 --profile `<your profile>`  --name "<prefix>-urs_<daac>cloud_pass" --value "<var.cmr_password>" --type "String"
    ```

  * run deployment pipeline to build docker image and push it to <Nexus>, and build terraform asset file and push it to <Nexus> repo.
    To run a pipeline for a feature branch, set the pipeline variable `CI_COMMIT_MESSAGE` to the value `[build-asset-for-feature]`. When the pipeline completes, retrieve the zip file name from the output of the `store` stage. 

    If the pipeline fails, you may need to update pipeline values NEXUS_USERNAME and NEXUS_PASSWORD. Also note, that using a $ symbol in your password will cause the 'store tf asset..' step to fail to push to the <Nexus> repo, even though the job will show as passed.

    See `CI/CD` below for further details.
  
  * update cumulus-tf/main.tf:
    ```
    add this definition to `throttled_queues`:
      {
        url = aws_sqs_queue.big_background_job_queue.id,
        execution_limit = var.big_throttled_execution_limit
      }

    if not present, add local `tags` variable:
       `tags = merge(var.tags, { Deployment = var.prefix })`
       
    after `public_bucket_names =` add:
      all_bucket_names       = [for k, v in var.buckets : v.name]

    add:
      # SSM Parameter values
      data "aws_ssm_parameter" "ed-user" {
        name = var.edl_user
      }

      data "aws_ssm_parameter" "ed-pass" {
        name = var.edl_pass
      }
    ```
  * update cumulus-tf/variables.tf 
    ```
    if not present, add:
    variable "tags" {
      description = "Tags to be applied to Cumulus resources that support tags"
      type        = map(string)
      default     = {}
    }
    
    add:
    variable "edl_user" {
      type = string
      default = "urs_<daac>cloud_user"
      description = "Earth Data login username ssm parameter from shared infrastructure"
    }
    variable "edl_pass" {
      type = string
      default = "urs_<daac>cloud_pass"
      description = "Earth Data login password ssm parameter from shared infrastructure"
    }
    variable "big_throttled_execution_limit" {
      type    = number
      default = 50
    }
    variable "big_throttled_message_limit" {
      type    = number
      default = 50
    }
    variable "big_throttled_time_limit" {
      type    = number
      default = 60
    }
    variable "big_image_name" {
      default = null
    }
    variable "big_version" {
      type = string
      default = "0.3.2"
    }     
    ####################################################################
    #  POBIT variables
    ####################################################################
    variable "gibs_region" {
      type        = string
      description = "Region GIBS endpoints reside in."
      default     = "us-west-2"
    }

    variable "gibs_account_id" {
      type        = string
      description = "Account ID for GIBS."
      default     = ""
    }

    variable "gibs_queue_name" {
      type        = string
      description = "Queue name for GIBS SQS queue that pobit will publish messages to."
      default     = "gitc-prod-<daac>-IN.fifo"
    }

    ```

  * Declare variables in cumulus-tf/cumulus.<prefix>.tfvars for:
    ```
    edl_user = "<prefix>-urs_<daac>cloud_user"
    edl_pass = "<prefix>-urs_<daac>cloud_pass"
    big_image_name = "browse-image-generator"
    big_version = "feature-lpcumulus-1581-bignbit"
    big_throttled_execution_limit = 20      (sandbox=20, SIT=, UAT=, PROD=)
    big_throttled_message_limit = 2
    big_throttled_time_limit = 60
    ```
  
  * Define `module "browse_image_module"` in your `cumulus-tf` folder.  An example can be found under `examples/cumulus-tf/browse_image_module.tf`
    You may need to change the `source` to pull the correct version. You'll need to insert your repo for repo_url.

  * Add `resource "aws_iam_role_policy" "pobit_lambda_processing"` in a file named pobit_lambda.iam.tf to your `cumulus-tf` folder. An example can be found under `examples/cumulus-tf/pobit_lambda.iam.tf`

  * Add a browse_image_workflow.tf to your Cumlulus repo to define the browse image post ingest workflow. An example can be found under `examples/cumulus-tf/browse_image_workflow.tf`.  You may need to update the `source` in `module "browse_image_module"` to use the zip file built by the pipeline.

  * Update your Cumulus ingest workflow to run the post ingest workflow defined in browse_image_workflow.tf

  Dataset Configuration
  ```
  The dataset configuration is loaded from the bucket specified by `config_bucket` under the prefix specified by `config_dir` in in your `browse_image_module` definition (see above).
 
  So in that bucket named in `config_bucket`, create a path with the value contained in `config_dir`  (ex ‘dataset-config’). In there you place the configuration file for each collection. The name of the file should be the shortname of the collection ($.meta.collection.name) with “.cfg” suffix. The content is a json document. Add new or updated config files to the config folder in the repo.
  
  Here is an example of an OPERA_L3_DSWX-HLS_PROVISIONAL_V1.cfg config file:

  {
    "convertToPNG":false,
    "operaTreatment": true,
    "imageFilenameRegex": ".*BROWSE.tif",
    "imgVariables":[
            {"id":"all"}
    ],
    "variables":[]
 }

 TODO: Question for Frank - What do these fields mean, valid values, etc. Any information useful to an integrator...
   convertToPNG:
   operaTreatment:
   imageFilenameRegex: a regex to apply to the filenames to determine which file should be used for browse image generation
   imgVariables:
   variables: 

# Development
If you make changes to the files in the bignbit folder that make up the image, which is used to create the lambdas, they don't seem to pick up the changes upon redeployment. You may have to delete the lambda from the AWS console and then deploy.

## Unit Testing
TODO: Add instructions for kicking off the unit tests

## Cumulus Testing
If you've added a Choice in the workflow, set the configuration accordingly, then ingest a granule that will trigger the workflow

# CI/CD

## Overview

A GitLab CI/CD pipeline exists for the project.  It primarily exists to: 

1) build a Terraform module zip file and store it as an asset in the Nexus repository. 
2) create a Docker image for the reconciliation task in the Nexus repo

It currently pushes to NEXUS and the pipeline needs values for NEXUS_USERNAME and NEXUS_PASSWORD
```
---------------------------------------------
Creating the Terraform module zip file has two stages: 
---------------------------------------------

A `build` stage (build tf asset) builds the zip file based on the state of the code at that commit. That files is stored as an artifact and passed to the next stage, `store`.

In `store`, (store-tf-asset) that artifact is uploaded as an asset. The nexus-client Docker container is leveraged for Nexus interaction.

The `cloud-migration` repo is used to store this raw asset within the browse-image-gen group.

Note that `store` relies upon the ‘nexus-client’ Docker image, which is used to push assets to a Nexus registry, that client image may not be in the LP Nexus registry if an aging policy has removed it.

---------------------------------------------
Creating the docker image has one stage:
---------------------------------------------

A `build` stage (build image) builds the docker image and stores it in the Nexus repo.

By default, this pipeline run for commits on `release/*`, `hotfix/*` and `develop` branches.  You'll see assets in that group that indicate they are for a particular version (release or hotfix) or for the `develop` branch.

You can enable this functionality on `feature/*` branches by using the value `[build-asset-for-feature]` in the commit message.  In GitLab, you can run a pipeline on your feature branch with the [CI_COMMIT_MESSAGE](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) variable that includes that value.
