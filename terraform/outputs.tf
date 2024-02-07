
output "get_dataset_configuration_arn" {
  value = aws_lambda_function.get_dataset_configuration.arn
}

output "get_granule_umm_json_arn" {
  value = aws_lambda_function.get_granule_umm_json.arn
}

output "get_collection_concept_id_arn" {
  value = aws_lambda_function.get_collection_concept_id.arn
}

output "identify_image_file_arn" {
  value = aws_lambda_function.identify_image_file.arn
}

output "generate_image_metadata_arn" {
  value = aws_lambda_function.generate_image_metadata.arn
}

output "submit_harmony_job_arn" {
  value = aws_lambda_function.submit_harmony_job.arn
}

output "submit_harmony_job_function_name" {
  value = aws_lambda_function.submit_harmony_job.function_name
}

output "get_harmony_job_status_arn" {
  value = aws_lambda_function.get_harmony_job_status.arn
}

output "copy_harmony_output_to_s3_arn"{
  value = aws_lambda_function.copy_harmony_output_to_s3.arn
}

output "apply_opera_treatment_arn"{
  value = aws_lambda_function.apply_opera_treatment.arn
}

output "config_bucket_name"{
  value = var.config_bucket
}

output "config_path"{
  value = var.config_dir
}

output "pobit_build_image_sets_arn" {
  value = aws_lambda_function.build_image_sets.arn
}

output "pobit_send_to_gitc_arn" {
  value = aws_lambda_function.send_to_gitc.arn
}

output "pobit_handle_gitc_response_arn" {
  value = aws_lambda_function.handle_gitc_response.arn
}

output "pobit_save_cma_message_arn" {
  value = aws_lambda_function.save_cma_message.arn
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
