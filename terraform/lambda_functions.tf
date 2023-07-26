data "aws_ecr_authorization_token" "token" {}

locals {
  lambda_container_image_uri_split = split("/", var.lambda_container_image_uri)
  ecr_image_name_and_tag           = split(":", element(local.lambda_container_image_uri_split, length(local.lambda_container_image_uri_split) - 1))
  ecr_image_name                   = "${local.environment}-${element(local.ecr_image_name_and_tag, 0)}"
  ecr_image_tag                    = element(local.ecr_image_name_and_tag, 1)
}

resource aws_ecr_repository "lambda-image-repo" {
  name = local.ecr_image_name
  tags = var.default_tags
}


resource null_resource ecr_login {
  triggers = {
    image_uri = var.lambda_container_image_uri
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-e", "-c"]
    command = <<EOF
      docker login ${data.aws_ecr_authorization_token.token.proxy_endpoint} -u AWS -p ${data.aws_ecr_authorization_token.token.password}
      EOF
  }
}

resource null_resource upload_ecr_image {
  depends_on = [null_resource.ecr_login]
  triggers = {
    image_uri = var.lambda_container_image_uri
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-e", "-c"]
    command = <<EOF
      docker pull ${var.lambda_container_image_uri}
      docker tag ${var.lambda_container_image_uri} ${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}
      docker push ${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}
      EOF
  }
}

# This doesn't work in terraform 0.13.x because it tries to resolve the image during the plan phase instead of the
# apply phase. Once IA updates to a newer terraform version, this can be used instead of having every lambda
# function depend on the null_resource.upload_ecr_image resource.
#data aws_ecr_image lambda_image {
#  depends_on = [
#    null_resource.upload_ecr_image
#  ]
#  repository_name = aws_ecr_repository.lambda-image-repo.name
#  image_tag       = local.ecr_image_tag
#
#}

resource "aws_lambda_function" "get_dataset_configuration" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.get_dataset_configuration.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-get_dataset_configuration-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "get_granule_umm_json" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.get_granule_umm_json.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-get_granule_umm_json-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "get_collection_concept_id" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.get_collection_concept_id.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-get_collection_concept_id-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "identify_image_file" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.identify_image_file.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-identify_image_file-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "submit_harmony_job" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.submit_harmony_job.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-submit_harmony_job-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "generate_image_metadata" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.generate_image_metadata.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-generate_image_metadata-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "get_harmony_job_status" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.get_harmony_job_status.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-get_harmony_job_status-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "copy_harmony_results_to_s3" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.copy_harmony_results_to_s3.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-copy_harmony_results_to_s3-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 256

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}

resource "aws_lambda_function" "apply_opera_treatment" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["podaac.big.apply_opera_treatment.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-apply_opera_treatment-lambda"
  role          = var.lambda_role.arn
  timeout       = 30
  memory_size   = 512

  environment {
    variables = {
      STACK_NAME                  = var.prefix
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      EDL_USER_SSM                = var.edl_user_ssm
      EDL_PASS_SSM                = var.edl_pass_ssm
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = var.default_tags
}