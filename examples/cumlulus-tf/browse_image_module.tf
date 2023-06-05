locals {
    big_appname = "big"
    repo_url = "<repo>"
    big_docker_image_url = "${local.repo_url}/${var.big_image_name}/${local.big_appname}:${var.big_version}"
    
}

module "browse_image_module" {
    # Variables are not allowed in module source string. MAKE SURE THIS MATCHES THE big_version!!
    source = "https://<repo>/browse-image-gen/terraform-big-mod-0.1.0.zip"

    prefix = var.prefix
    region = var.region
    lambda_role = aws_iam_role.pobit_lambda_processing
    security_group_ids = [aws_security_group.no_ingress_all_egress.id]
    subnet_ids = var.subnet_ids
    app_name = local.big_appname
    lambda_container_image_uri = local.big_docker_image_url

    default_tags = merge(local.tags, {
        application = local.big_appname,
        Version = var.big_version
    })
    profile = var.aws_profile

    config_bucket = var.buckets.internal.name
    config_dir = "dataset-config"

    edl_user_ssm = data.aws_ssm_parameter.ed-user.name
    edl_pass_ssm = data.aws_ssm_parameter.ed-pass.name

    depends_on = [
        aws_iam_role.pobit_lambda_processing
    ]
}
