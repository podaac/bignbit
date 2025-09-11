terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.9.0"
    }
    null = {
      source  = "hashicorp/null"
      version = "~> 2.1"
    }
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}


locals {
  environment = var.stage
  cmr_environment = var.cmr_environment == "" ? (upper(var.stage) == "OPS" ? "OPS" : "UAT") : upper(var.cmr_environment)

  account_id = data.aws_caller_identity.current.account_id

  aws_resources_name = terraform.workspace == "default" ? "svc-${var.app_name}-${var.prefix}" : "svc-${var.app_name}-${var.prefix}-${terraform.workspace}"

  default_tags = length(var.default_tags) == 0 ? {
    team : "TVA",
    application : var.app_name,
    Environment = var.stage
  } : var.default_tags

  current_aws_region = try(
    data.aws_region.current.region,
    data.aws_region.current.name
  )

}
