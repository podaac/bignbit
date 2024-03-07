output "config_bucket_name"{
  value = var.config_bucket
}

output "config_path"{
  value = var.config_dir
}

output "pobit_handle_gitc_response_arn" {
  value = aws_lambda_function.handle_gitc_response.arn
}

output "pobit_gibs_topic" {
  value = aws_sns_topic.gibs_response_topic.arn
}

output "pobit_gibs_queue" {
  value = aws_sqs_queue.gibs_response_queue.arn
}

output "pobit_audit_bucket"{
  value = var.pobit_audit_bucket
}

output "pobit_audit_path"{
  value = var.pobit_audit_path
}

output "browse_image_state_machine_definition"{
  value = aws_sfn_state_machine.sfn_state_machine.definition
}
