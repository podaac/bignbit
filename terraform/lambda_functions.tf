data "aws_ecr_authorization_token" "token" {}

locals {
  lambda_container_image_uri_split = split("/", var.lambda_container_image_uri)
  ecr_image_name_and_tag           = split(":", element(local.lambda_container_image_uri_split, length(local.lambda_container_image_uri_split) - 1))
  ecr_image_name                   = "${local.environment}-${element(local.ecr_image_name_and_tag, 0)}"
  ecr_image_tag                    = element(local.ecr_image_name_and_tag, 1)
  build_image_sets_function_name = "${local.lambda_resources_name}-build_image_sets-lambda"
  send_to_gitc_function_name = "${local.lambda_resources_name}-send_to_gitc-lambda"
  handle_gitc_response_function_name = "${local.lambda_resources_name}-handle_gitc_response-lambda"
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
data "aws_ecr_image" "lambda_image" {
  depends_on = [
    null_resource.upload_ecr_image
  ]
  repository_name = aws_ecr_repository.lambda-image-repo.name
  image_tag       = local.ecr_image_tag
}

resource "aws_lambda_function" "get_dataset_configuration" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.get_dataset_configuration.lambda_handler"]
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
    command = ["bignbit.get_granule_umm_json.lambda_handler"]
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
    command = ["bignbit.get_collection_concept_id.lambda_handler"]
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
    command = ["bignbit.identify_image_file.lambda_handler"]
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
    command = ["bignbit.submit_harmony_job.lambda_handler"]
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
    command = ["bignbit.generate_image_metadata.lambda_handler"]
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
    command = ["bignbit.get_harmony_job_status.lambda_handler"]
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

resource "aws_lambda_function" "copy_harmony_output_to_s3" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.copy_harmony_output_to_s3.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-copy_harmony_output_to_s3"
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
    command = ["bignbit.apply_opera_treatment.lambda_handler"]
  }
  function_name = "${local.lambda_resources_name}-apply_opera_treatment"
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


resource "aws_lambda_function" "build_image_sets" {

  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.build_image_sets.lambda_handler"]
  }

  function_name    = local.build_image_sets_function_name
  role             = var.lambda_role.arn
  timeout          = 15
  memory_size      = 128

  environment {
    variables = {
      STACK_NAME                  = local.lambda_resources_name
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      GIBS_REGION                 = var.gibs_region
      GIBS_SQS_URL                = "https://sqs.${var.gibs_region}.amazonaws.com/${var.gibs_account_id}/${var.gibs_queue_name}"
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = local.tags
}

resource "aws_lambda_function" "send_to_gitc" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.send_to_gitc.lambda_handler"]
  }
  function_name    = "${local.lambda_resources_name}-send_to_gitc-lambda"
  role             = var.lambda_role.arn
  timeout          = 15
  memory_size      = 128

  environment {
    variables = {
      STACK_NAME                  = local.lambda_resources_name
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
      GIBS_REGION                 = var.gibs_region
      GIBS_SQS_URL                = "https://sqs.${var.gibs_region}.amazonaws.com/${var.gibs_account_id}/${var.gibs_queue_name}"
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = local.tags
}


resource "aws_lambda_function" "handle_gitc_response" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.handle_gitc_response.handler"]
  }
  function_name    = "${local.lambda_resources_name}-handle_gitc_response-lambda"
  role             = var.lambda_role.arn
  timeout          = 5
  memory_size      = 128

  environment {
    variables = {
      STACK_NAME                  = local.lambda_resources_name
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = local.tags
}

resource "aws_lambda_function" "save_cma_message" {
  depends_on = [
    null_resource.upload_ecr_image
  ]

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.lambda-image-repo.repository_url}:${local.ecr_image_tag}"
  image_config {
    command = ["bignbit.save_cma_message.lambda_handler"]
  }
  function_name    = "${local.lambda_resources_name}-save_cma_message-lambda"
  role             = var.lambda_role.arn
  timeout          = 15
  memory_size      = 128

  environment {
    variables = {
      STACK_NAME                  = local.lambda_resources_name
      CUMULUS_MESSAGE_ADAPTER_DIR = "/opt/"
      REGION                      = var.region
    }
  }

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = var.security_group_ids
  }

  tags = local.tags
}

data "aws_iam_policy_document" "gibs_response_topic_policy" {
  statement {
    sid       = "${local.lambda_resources_name}-grant-gitc-publish-sns"
    effect    = "Allow"
    principals {
      identifiers = compact([
        var.gibs_account_id,
        data.aws_caller_identity.current.account_id
      ])
      type        = "AWS"
    }
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.gibs_response_topic.arn]
  }
}

resource "aws_sns_topic_policy" "default" {
  arn = aws_sns_topic.gibs_response_topic.arn
  policy = data.aws_iam_policy_document.gibs_response_topic_policy.json
}

resource "aws_sns_topic" "gibs_response_topic" {
  name   = "${local.lambda_resources_name}-gibs-response-topic"
  tags   = local.tags
}

resource "aws_sqs_queue" "gibs_response_queue" {
  name = "${local.lambda_resources_name}-gibs-response-queue"
  tags = local.tags
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.gibs_response_deadletter.arn
    maxReceiveCount     = 4
  })
}

resource "aws_sqs_queue" "gibs_response_deadletter" {
  name = "${local.lambda_resources_name}-gibs-response-dlq"
  redrive_allow_policy = jsonencode({
    redrivePermission = "byQueue",
    # Cannot use reference to aws_sqs_queue.gibs_response_queue.arn because it causes a cycle https://github.com/hashicorp/terraform-provider-aws/issues/22577
    sourceQueueArns   = ["arn:aws:sqs:${var.region}:${local.account_id}:${local.lambda_resources_name}-gibs-response-queue"]
  })
}

data "aws_iam_policy_document" "gibs_response_queue_policy" {
  statement {
    sid       = "${local.lambda_resources_name}-grant-topic-send-sqs"
    effect    = "Allow"
    principals {
      identifiers = [
        data.aws_caller_identity.current.account_id
      ]
      type        = "AWS"
    }
    principals {
      identifiers = ["sns.amazonaws.com"]
      type        = "Service"
    }
    actions   = ["sqs:SendMessage"]
    resources = [aws_sqs_queue.gibs_response_queue.arn]
    condition {
      test     = "ArnEquals"
      values   = [aws_sns_topic.gibs_response_topic.arn]
      variable = "aws:SourceArn"
    }
  }
}

resource "aws_sqs_queue_policy" "gibs_response_queue_policy" {
  queue_url = aws_sqs_queue.gibs_response_queue.id
  policy    = data.aws_iam_policy_document.gibs_response_queue_policy.json
}

resource "aws_sns_topic_subscription" "gibs_topic_subscription" {
  topic_arn            = aws_sns_topic.gibs_response_topic.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.gibs_response_queue.arn
  raw_message_delivery = true
}

data "aws_iam_policy_document" "gibs_response_role_policy" {
  statement {
    sid       = "${replace(title(replace(local.lambda_resources_name, "-", " ")), " ", "")}GrantReadGitcResponse"
    effect    = "Allow"
    actions   = ["sqs:GetQueueAttributes",
      "sqs:GetQueueUrl",
      "sqs:DeleteMessage",
      "sqs:ChangeMessageVisibility",
      "sqs:PurgeQueue",
      "sqs:ReceiveMessage"
    ]
    resources = [aws_sqs_queue.gibs_response_queue.arn]
  }
  statement {
    sid       = "${replace(title(replace(local.lambda_resources_name, "-", " ")), " ", "")}GrantReadGitcResponse2"
    effect    = "Allow"
    actions   = ["sqs:ListQueues"]
    resources = ["arn:aws:sqs:*:${local.account_id}:*"]
  }
}

resource "aws_iam_role_policy" "allow_lambda_role_to_read_sqs_messages" {
  name_prefix   = local.lambda_resources_name
  role   = var.lambda_role.id
  policy = data.aws_iam_policy_document.gibs_response_role_policy.json
}

resource "aws_lambda_event_source_mapping" "gibs_response_event_trigger" {
  event_source_arn = aws_sqs_queue.gibs_response_queue.arn
  function_name    = aws_lambda_function.handle_gitc_response.arn
}

data "aws_iam_policy_document" "gibs_request_queue_policy" {
  statement {
    sid       = "${replace(title(replace(local.lambda_resources_name, "-", " ")), " ", "")}GrantSendToGitc"
    effect    = "Allow"
    actions   = ["sqs:SendMessage"]
    resources = ["arn:aws:sqs:*:${var.gibs_account_id}:${var.gibs_queue_name}"]
  }
}

resource "aws_iam_role_policy" "allow_lambda_role_to_send_to_gitc" {
  name_prefix   = local.lambda_resources_name
  role   = var.lambda_role.id
  policy = data.aws_iam_policy_document.gibs_request_queue_policy.json
}
