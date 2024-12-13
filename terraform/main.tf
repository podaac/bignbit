terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.9.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 3"
    }
  }
}

provider "aws" {
  region = "us-west-2"

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }

  default_tags {
    tags = local.default_tags
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

#
# data "template_file" "workflow_definition" {
#   template = file("${path.module}/state_machine_definition.tpl")
#   vars = {
#     GetDatasetConfigurationLambda = aws_lambda_function.get_dataset_configuration.arn,
#     ConfigBucket                  = var.config_bucket,
#     ConfigDir                     = var.config_dir,
#     GetGranuleUmmJsonLambda       = aws_lambda_function.get_granule_umm_json.arn,
#     IdentifyImageFileLambda       = aws_lambda_function.identify_image_file.arn,
#     ApplyOperaHLSTreatmentLambda  = aws_lambda_function.apply_opera_hls_treatment.arn,
#     GetCollectionConceptIdLambda  = aws_lambda_function.get_collection_concept_id.arn,
#     SubmitHarmonyJobLambda        = aws_lambda_function.submit_harmony_job.arn,
#     GetHarmonyJobStatusLambda     = aws_lambda_function.get_harmony_job_status.arn,
#     GenerateImageMetadataLambda   = aws_lambda_function.generate_image_metadata.arn,
#     BuildImageSetsLambda          = aws_lambda_function.build_image_sets.arn,
#     SendToGITCLambda              = aws_lambda_function.send_to_gitc.arn,
#     SaveCNMMessageLambda          = aws_lambda_function.save_cnm_message.arn,
#     PobitAuditBucket              = var.pobit_audit_bucket,
#     PobitAuditPath                = var.pobit_audit_path,
#     HarmonyStagingBucket          = var.harmony_staging_bucket,
#     HarmonyStagingPath            = var.harmony_staging_path
#   }
# }


locals {
  environment = var.stage

  account_id = data.aws_caller_identity.current.account_id

  aws_resources_name = terraform.workspace == "default" ? "svc-${var.app_name}-${var.prefix}" : "svc-${var.app_name}-${var.prefix}-${terraform.workspace}"

  default_tags = length(var.default_tags) == 0 ? {
    team : "TVA",
    application : var.app_name,
    Environment = var.stage
  } : var.default_tags

}
