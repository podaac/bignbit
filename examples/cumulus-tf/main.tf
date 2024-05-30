terraform {
  required_providers {
    aws  = ">= 2.31.0"
    null = "~> 2.1"
  }
}

provider "aws" {
  region = "us-west-2"

  ignore_tags {
    key_prefixes = ["gsfc-ngap"]
  }
}

locals {
  name = var.app_name
  environment = var.stage

  # This is the convention we use to know what belongs to each other
  ec2_resources_name = terraform.workspace == "default" ? "svc-${local.environment}-${local.name}" : "svc-${local.environment}-${local.name}-${terraform.workspace}"

  # Account ID used for getting the ECR host
  account_id = data.aws_caller_identity.current.account_id

  default_tags = length(var.default_tags) == 0 ? {
    team: "TVA",
    application: local.ec2_resources_name,
    Environment = var.stage
    Version = var.app_version
  } : var.default_tags
}
