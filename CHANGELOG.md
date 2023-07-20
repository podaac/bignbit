# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### LPDAAC July 2023
* Updated terraform files to also deploy "BIT" lambdas:
    * lambda_functions.tf was updated to include the additional lambda definitions needed for ‘bit’: build_image_sets, send_to_gitc, handle_gitc_response, save_cma_message.  It also adds aws_iam_policy_document gibs_response_topic_policy, aws_sns_topic_policy default, aws_sns_topic gibs_response_topic, aws_sqs_queue gibs_response_queue, aws_sqs_queue gibs_response_deadletter, aws_iam_policy_document gibs_response_queue_policy, aws_sqs_queue_policy gibs_response_queue_policy, aws_sns_topic_subscription gibs_topic_subscription, aws_iam_policy_document gibs_response_role_policy, aws_iam_role_policy allow_lambda_role_to_read_sqs_messages, aws_lambda_event_source_mapping gibs_response_event_trigger, aws_iam_policy_document gibs_request_queue_policy, aws_iam_role_policy allow_lambda_role_to_send_to_gitc.
    * main.tf was updated to add account_id definition. 
    * outputs.tf was updated to add the ‘bit’ output vars. 
    * variables.tf was updated to add the ‘bit’ vars.
* Updated examples for cumulus-tf/browse_image_module.tf and cumulus-tf/browse_image_workflow.tf to include transfer to GITC

### LPDAAC May 2023
* Modified apply_opera_treatment.py to account for grid codes that don't have a leading 'T'
* Updated README.md with build and deployment instructions. I tried to put some instructions in here on how to work with this and integrate it into a cumulus environment. It’s still missing pieces, and needs some cleanup (TODO’s, etc), but it’s a start. Note that some of it is specific to LPDAAC's Gitlab repo, and will need to be updated for Github. The goal is for the github.com/podaac/bignbit repository to host the source code and be able to build and serve the versioned artifacts including the cumulus module (similar to how other cumulus modules are being published). So someone who wants to use bignbit in their cumulus installation would just define the ‘module’ with source equal to something like https://github.com/podaac/bignbit/releases/download/v1.0.0/terraform-aws-cumulus-bignbit.zip
* Added `terraform` files from the old browse-image-generator repo for "BIG" deployment. I did modify the terraform/lambda_funtions.tf file from the original bitbucket repo. I was having issues with the ecr_login and ended up combining it with the upload_ecr_image.
* Added `docker` files from old browse-image-generator repo (possibly with some modifications) to build the docker image
* Added examples directory with workflow examples showing how to incorporate this into an ingest (and post-ingest) workflow
* Added scripts directory which contains scripts used in LPDAAC's gitlab build pipeline. If these are not needed by the GitHub build, they can be removed
* Added .github/workflows/browse-image-generator.yml and docker-publish.yml.  LPDAAC's Gitlab pipeline to build the docker image and terraform asset file and push them to Nexus, was ported by a Github tool that converts a gitlb pipeline to Github Actions, which created these two files. No work has been done on them yet to get them working. They might be useful, they might not. The github pipeline will/should publish the artifacts to github packages (ghcr.io for the docker image)

### Added 
- Initial port from JPL GHE to public GitHub.com



[unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/olivierlacan/keep-a-changelog/releases/tag/v0.0.1
