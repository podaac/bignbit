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

locals {
  name = var.app_name
  environment = var.prefix

  account_id = data.aws_caller_identity.current.account_id

  tags = length(var.default_tags) == 0 ? {
    team: "PODAAC TVA",
    application: var.app_name,
  } : var.default_tags

  lambda_resources_name = terraform.workspace == "default" ? "svc-${local.name}-${local.environment}" : "svc-${local.name}-${local.environment}-${terraform.workspace}"
}
