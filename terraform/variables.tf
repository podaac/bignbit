variable "aws_profile" {
  type    = string
  default = null
}

variable "stage" {
  type = string
}

variable "prefix" {
  type = string
}

# The location of dataset-config file. Ex. s3://my-internal/datset-config/
variable "config_bucket" {
  type = string
}

variable "config_dir" {
  type = string
  default = "datset-config"
}

variable "pobit_audit_bucket" {
  type = string
  description = "S3 bucket where messages exchanged with GITC will be saved. Typically the cumulus internal bucket"
}

variable "pobit_audit_path" {
  type = string
  description = "Path relative to pobit_audit_bucket where messages exchanged with GITC will be saved."
  default = "pobit-cma-output"
}

variable "gibs_region" {
  type = string
}

variable "gibs_queue_name" {
  type = string
}

variable "gibs_account_id" {
  type = string
}

variable "edl_user_ssm" {
  type = string
}

variable "edl_pass_ssm" {
  type = string
}

variable "lambda_role" {
  type = object({
    id = string
    arn = string
  })
}

variable "security_group_ids" {
  type = list(string)
}

variable "subnet_ids" {
  type = list(string)
}

variable "region" {
  type = string
}

variable "app_name" {
  default = "big"
}

variable "default_tags" {
  type = map(string)
  default = {}
}

variable task_logs_retention_in_days{
  description = "Log retention days"
  type = number
  default = 30
}

variable tags{
  description = "tags"
  type = map(string)
  default = {}
}



variable "lambda_container_image_uri" {
  type = string
  default = ""
}
