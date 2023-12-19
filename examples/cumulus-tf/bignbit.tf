module "bignbit_module" {
    source = "../../terraform"
    prefix = var.prefix
    stage = var.stage
    region = var.region
    lambda_role = aws_iam_role.iam_execution
    security_group_ids = []
    subnet_ids = []
    app_name = var.app_name
    #lambda_container_image_uri = "ghcr.io/podaac/podaac-big:${var.app_version}"
    lambda_container_image_uri = var.lambda_container_image_uri

    default_tags = local.default_tags

    config_bucket = aws_s3_bucket.internal.bucket
    config_dir = "dataset-config"

    edl_user_ssm = var.edl_user_ssm
    edl_pass_ssm = var.edl_pass_ssm

    pobit_audit_bucket = aws_s3_bucket.internal.bucket
    gibs_region = var.gibs_region == "mocked" ? "us-west-2" : var.gibs_region
    gibs_queue_name = var.gibs_queue_name == "mocked" ? aws_sqs_queue.gitc_input_queue[0].name : var.gibs_queue_name
    gibs_account_id = var.gibs_account_id == "mocked" ? local.account_id : var.gibs_account_id
}
