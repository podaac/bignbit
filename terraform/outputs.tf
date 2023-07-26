
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

output "copy_harmony_results_to_s3_arn"{
  value = aws_lambda_function.copy_harmony_results_to_s3.arn
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