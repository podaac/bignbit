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
  environment = var.stage

  account_id = data.aws_caller_identity.current.account_id

  lambda_resources_name = terraform.workspace == "default" ? "svc-${local.name}-${local.environment}" : "svc-${local.name}-${local.environment}-${terraform.workspace}"

  tags = length(var.default_tags) == 0 ? {
    team: "PODAAC TVA",
    application: local.lambda_resources_name,
    Environment = var.stage
  } : var.default_tags

}
