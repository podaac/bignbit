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

output "process_harmony_results_arn" {
  value = aws_lambda_function.process_harmony_results.arn
}

output "apply_opera_hls_treatment_arn"{
  value = aws_lambda_function.apply_opera_hls_treatment.arn
}

output "pobit_build_image_sets_arn" {
  value = aws_lambda_function.build_image_sets.arn
}

output "pobit_send_to_gitc_arn" {
  value = aws_lambda_function.send_to_gitc.arn
}

output "pobit_save_cnm_message_arn" {
  value = aws_lambda_function.save_cnm_message.arn
}

output "workflow_definition" {
  value = templatefile("${path.module}/state_machine_definition.tpl", {
    GetDatasetConfigurationLambda = aws_lambda_function.get_dataset_configuration.arn,
    ConfigBucket                  = var.config_bucket,
    ConfigDir                     = var.config_dir,
    GetGranuleUmmJsonLambda       = aws_lambda_function.get_granule_umm_json.arn,
    IdentifyImageFileLambda       = aws_lambda_function.identify_image_file.arn,
    ApplyOperaHLSTreatmentLambda  = aws_lambda_function.apply_opera_hls_treatment.arn,
    GetCollectionConceptIdLambda  = aws_lambda_function.get_collection_concept_id.arn,
    SubmitHarmonyJobLambda        = aws_lambda_function.submit_harmony_job.arn,
    GetHarmonyJobStatusLambda     = aws_lambda_function.get_harmony_job_status.arn,
    ProcessHarmonyJobOutputLambda = aws_lambda_function.process_harmony_results.arn,
    GenerateImageMetadataLambda   = aws_lambda_function.generate_image_metadata.arn,
    BuildImageSetsLambda          = aws_lambda_function.build_image_sets.arn,
    SendToGITCLambda              = aws_lambda_function.send_to_gitc.arn,
    SaveCNMMessageLambda          = aws_lambda_function.save_cnm_message.arn,
    PobitAuditBucket              = var.pobit_audit_bucket,
    PobitAuditPath                = var.pobit_audit_path,
    HarmonyStagingBucket          = local.harmony_bucket_name,
    HarmonyStagingPath            = var.harmony_staging_path
  })
}

output "harmony_staging_bucket" {
  value = local.harmony_bucket_name
}

output "harmony_staging_path" {
  value = var.harmony_staging_path
}