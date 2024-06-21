variable prefix{
  description = "prefix to aws resources"
  type = string
  default = ""
}

variable region{
  description = "aws region"
  type = string
  default = "us-west-2"
}



variable "cma_version" {
  type    = string
  default = "v2.0.2"
}

variable "app_name" {
  default = "bignbit"
}

variable "default_tags" {
  type = map(string)
  default = {}
}

variable "stage" {}
variable "app_version" {}

variable "edl_user_ssm" {
  type = string
  default = "urs_podaaccloud_user"
  description = "Earth Data login username ssm parameter from shared infrastructure"
}

variable "edl_pass_ssm" {
  type = string
  default = "urs_podaaccloud_pass"
  description = "Earth Data login password ssm parameter from shared infrastructure"
}

variable "gibs_account_id" {
  type = string
}

variable "lambda_container_image_uri" {
  type = string
  default = ""
}

variable "edl_user" {
  type = string
  default = "urs_podaaccloud_user"
  description = "Earth Data login username ssm parameter from shared infrastructure"
}

variable "edl_pass" {
  type = string
  default = "urs_podaaccloud_pass"
  description = "Earth Data login password ssm parameter from shared infrastructure"
}

variable "gibs_region" {
  type = string
}

variable "gibs_queue_name" {
  type = string
}