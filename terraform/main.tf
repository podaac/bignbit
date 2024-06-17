terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.0,!= 3.14.0"
    }
    null = "~> 2.1"
  }
}

data "aws_caller_identity" "current" {}


data "template_file" "workflow_definition" {
  template = file("${path.module}/state_machine_definition.tpl")
  vars     = {
    GetDatasetConfigurationLambda = aws_lambda_function.get_dataset_configuration.arn,
    ConfigBucket                  = var.config_bucket,
    ConfigDir                     = var.config_dir,
    GetGranuleUmmJsonLambda       = aws_lambda_function.get_granule_umm_json.arn,
    IdentifyImageFileLambda       = aws_lambda_function.identify_image_file.arn,
    ApplyOperaHLSTreatmentLambda  = aws_lambda_function.apply_opera_hls_treatment.arn,
    GetCollectionConceptIdLambda  = aws_lambda_function.get_collection_concept_id.arn,
    SubmitHarmonyJobLambda        = aws_lambda_function.submit_harmony_job.arn,
    GetHarmonyJobStatusLambda     = aws_lambda_function.get_harmony_job_status.arn,
    CopyHarmonyOutputToS3Lambda   = aws_lambda_function.copy_harmony_output_to_s3.arn,
    GenerateImageMetadataLambda   = aws_lambda_function.generate_image_metadata.arn,
    BuildImageSetsLambda          = aws_lambda_function.build_image_sets.arn,
    SendToGITCLambda              = aws_lambda_function.send_to_gitc.arn,
    SaveCNMMessageLambda          = aws_lambda_function.save_cnm_message.arn,
    PobitAuditBucket              = var.pobit_audit_bucket,
    PobitAuditPath                = var.pobit_audit_path
  }
}


locals {
name = var.app_name
environment = var.stage

account_id = data.aws_caller_identity.current.account_id

lambda_resources_name = terraform.workspace == "default" ? "svc-${local.name}-${local.environment}" : "svc-${local.name}-${local.environment}-${terraform.workspace}"

ec2_resources_name = terraform.workspace == "default" ? "svc-${local.environment}-${local.name}" : "svc-${local.environment}-${local.name}-${terraform.workspace}"

tags = length(var.default_tags) == 0 ? {
team : "PODAAC TVA",
application : local.lambda_resources_name,
Environment = var.stage
} : var.default_tags

}
