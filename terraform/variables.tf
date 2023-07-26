variable "aws_profile" {
  type    = string
  default = null
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

variable "profile" {
  type    = string
  default = null
}

variable "lambda_container_image_uri" {
  type = string
  default = ""
}