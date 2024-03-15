

# In a typcial cumulus installation, this is how you would define the workflow:

module "browse_image_workflow" {
  source          = "https://github.com/nasa/cumulus/releases/download/v16.1.2/terraform-aws-cumulus-workflow.zip"
  prefix          = var.prefix
  name            = "BrowseImageWorkflow"
  workflow_config = module.cumulus.workflow_config
  system_bucket   = var.system_bucket
  tags            = merge(local.tags, { application = "BrowseImageWorkflow" })

  definition = templatefile("${path.module}/.terraform/modules/bignbit_module/state_machine_definition.json", {
      GetDatasetConfigurationLambda = module.bignbit_module.get_dataset_configuration_arn,
      ConfigBucket                  = module.bignbit_module.config_bucket_name,
      ConfigDir                     = module.bignbit_module.config_path,
      GetGranuleUmmJsonLambda       = module.bignbit_module.get_granule_umm_json_arn,
      IdentifyImageFileLambda       = module.bignbit_module.identify_image_file_arn,
      ApplyOperaTreatmentLambda     = module.bignbit_module.apply_opera_treatment_arn,
      GetCollectionConceptIdLambda  = module.bignbit_module.get_collection_concept_id_arn,
      SubmitHarmonyJobLambda        = module.bignbit_module.submit_harmony_job_arn,
      GetHarmonyJobStatusLambda     = module.bignbit_module.get_harmony_job_status_arn,
      CopyHarmonyOutputToS3Lambda   = module.bignbit_module.copy_harmony_output_to_s3_arn,
      GenerateImageMetadataLambda   = module.bignbit_module.generate_image_metadata_arn,
      BuildImageSetsLambda          = module.bignbit_module.pobit_build_image_sets_arn,
      SendToGITCLambda              = module.bignbit_module.pobit_send_to_gitc_arn,
      SaveCMAMessageLambda          = module.bignbit_module.pobit_save_cma_message_arn,
      PobitAuditBucket              = module.bignbit_module.pobit_audit_bucket,
      PobitAuditPath                = module.bignbit_module.pobit_audit_path
     }
  )
}

/*
# This example is deployable without cumulus installed for the purpose of testing the module in isolation; so it does not use terraform-aws-cumulus-workflow.zip


resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "${local.ec2_resources_name}-BrowseImageWorkflow"
  role_arn = aws_iam_role.iam_execution.arn

  definition = templatefile("../../terraform/state_machine_definition.json", {
      GetDatasetConfigurationLambda = module.bignbit_module.get_dataset_configuration_arn,
      ConfigBucket                  = module.bignbit_module.config_bucket_name,
      ConfigDir                     = module.bignbit_module.config_path,
      GetGranuleUmmJsonLambda       = module.bignbit_module.get_granule_umm_json_arn,
      IdentifyImageFileLambda       = module.bignbit_module.identify_image_file_arn,
      ApplyOperaTreatmentLambda     = module.bignbit_module.apply_opera_treatment_arn,
      GetCollectionConceptIdLambda  = module.bignbit_module.get_collection_concept_id_arn,
      SubmitHarmonyJobLambda        = module.bignbit_module.submit_harmony_job_arn,
      GetHarmonyJobStatusLambda     = module.bignbit_module.get_harmony_job_status_arn,
      CopyHarmonyOutputToS3Lambda   = module.bignbit_module.copy_harmony_output_to_s3_arn,
      GenerateImageMetadataLambda   = module.bignbit_module.generate_image_metadata_arn,
      BuildImageSetsLambda          = module.bignbit_module.pobit_build_image_sets_arn,
      SendToGITCLambda              = module.bignbit_module.pobit_send_to_gitc_arn,
      SaveCMAMessageLambda          = module.bignbit_module.pobit_save_cma_message_arn,
      PobitAuditBucket              = module.bignbit_module.pobit_audit_bucket,
      PobitAuditPath                = module.bignbit_module.pobit_audit_path
     }
  )
}
*/
