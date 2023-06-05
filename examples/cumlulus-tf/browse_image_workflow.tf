module "browse_image_workflow" {
  source = "https://github.com/nasa/cumulus/releases/download/v15.0.1/terraform-aws-cumulus-workflow.zip"

  prefix          = var.prefix
  name            = "BrowseImageWorkflow"
  workflow_config = module.cumulus.workflow_config
  system_bucket   = var.system_bucket
  tags            = local.tags

  state_machine_definition = <<JSON
  {
    "Comment": "Run BIG and POBIT",
    "StartAt": "GetDatasetConfiguration",
    "States": {
        "GetDatasetConfiguration": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.get_dataset_configuration_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "config_bucket_name": "${module.browse_image_module.config_bucket_name}",
                        "config_key_name.$": "States.Format('${module.browse_image_module.config_path}/{}.cfg', $.meta.collection.name)",
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Get Granule umm_json"
        },
        "Get Granule umm_json": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.get_granule_umm_json_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "cmr_environment": "{$.meta.cmr.cmrEnvironment}",
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Convert to PNG?"
        },
        "Convert to PNG?": {
            "Type": "Choice",
            "Choices": [
                {
                    "And": [
                        {
                            "Variable": "$.payload.datasetConfigurationForBIG.config.convertToPNG",
                            "IsPresent": true
                        },
                        {
                            "Variable": "$.payload.datasetConfigurationForBIG.config.convertToPNG",
                            "BooleanEquals": true
                        }
                    ],
                    "Comment": "If convertToPNG is true",
                    "Next": "Get Collection Concept Id"
                }
            ],
            "Default": "Identify Image File"
        },
        "Identify Image File": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.identify_image_file_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Apply OPERA Treatment?"
        },
        "Apply OPERA Treatment?": {
            "Type": "Choice",
            "Choices": [
                {
                    "And": [
                        {
                            "Variable": "$.payload.datasetConfigurationForBIG.config.operaTreatment",
                            "IsPresent": true
                        },
                        {
                            "Variable": "$.payload.datasetConfigurationForBIG.config.operaTreatment",
                            "BooleanEquals": true
                        }
                    ],
                    "Comment": "If operaTreatment is true",
                    "Next": "Apply OPERA Treatment"
                }
            ],
            "Default": "Generate Image Metadata"
        },
        "Apply OPERA Treatment": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.apply_opera_treatment_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Generate Image Metadata"
        },
        "Get Collection Concept Id": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.get_collection_concept_id_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "collection_shortname": "{$.meta.collection.name}",
                        "cmr_provider": "{$.meta.cmr.provider}",
                        "cmr_environment": "{$.meta.cmr.cmrEnvironment}",
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Convert Variables To PNG"
        },
        "Convert Variables To PNG": {
            "Type": "Map",
            "ItemsPath": "$.payload.datasetConfigurationForBIG.config.imgVariables",
            "ItemSelector": {
                "cumulus_meta.$": "$.cumulus_meta",
                "meta.$": "$.meta",
                "payload.$": "$.payload",
                "task_config.$": "$.task_config",
                "current_item.$": "$$.Map.Item.Value"
            },
            "ItemProcessor": {
                "ProcessorConfig": {
                    "Mode": "INLINE"
                },
                "StartAt": "Submit Harmony Job",
                "States": {
                    "Submit Harmony Job": {
                        "Type": "Task",
                        "Parameters": {
                            "cma": {
                                "event.$": "$",
                                "task_config": {
                                    "granule": "{$.payload.granules[0]}",
                                    "cmr_provider": "{$.cmr_provider}",
                                    "collection": "{$.meta.collection}",
                                    "collection_concept_id": "{$.payload.collection_concept_id}",
                                    "cmr_environment": "{$.meta.cmr.cmrEnvironment}",
                                    "cmr_clientid": "{$.meta.cmr.clientId}",
                                    "current_item": "{$.current_item}",
                                    "big_config": "{$.payload.datasetConfigurationForBIG}",
                                    "cumulus_message": {
                                        "input": "{$.payload}"
                                    }
                                }
                            }
                        },
                        "Resource": "${module.browse_image_module.submit_harmony_job_arn}",
                        "Next": "Wait 20 Seconds"
                    },
                    "Wait 20 Seconds": {
                        "Type": "Wait",
                        "Seconds": 20,
                        "Next": "Get Harmony Job Status"
                    },
                    "Get Harmony Job Status": {
                        "Type": "Task",
                        "Resource": "${module.browse_image_module.get_harmony_job_status_arn}",
                        "Parameters": {
                            "cma": {
                                "event.$": "$",
                                "task_config": {
                                    "cmr_environment": "{$.meta.cmr.cmrEnvironment}",
                                    "harmony_job": "{$.payload.harmony_job.job}",
                                    "cumulus_message": {
                                        "input": "{$.payload}"
                                    }
                                }
                            }
                        },
                        "Retry": [
                            {
                                "ErrorEquals": [
                                    "Lambda.ServiceException",
                                    "Lambda.AWSLambdaException",
                                    "Lambda.SdkClientException",
                                    "Lambda.TooManyRequestsException"
                                ],
                                "IntervalSeconds": 2,
                                "MaxAttempts": 6,
                                "BackoffRate": 2
                            }
                        ],
                        "Next": "Job Complete?"
                    },
                    "Job Complete?": {
                        "Type": "Choice",
                        "Choices": [
                            {
                                "Variable": "$.payload.harmony_job_status",
                                "StringMatches": "successful",
                                "Next": "Copy Harmony Results to S3",
                                "Comment": "Job successful"
                            },
                            {
                                "And": [
                                    {
                                        "Not": {
                                            "Variable": "$.payload.harmony_job_status",
                                            "StringMatches": "running"
                                        }
                                    },
                                    {
                                        "Not": {
                                            "Variable": "$.payload.harmony_job_status",
                                            "StringMatches": "accepted"
                                        }
                                    }
                                ],
                                "Next": "Harmony Fail",
                                "Comment": "Job not successful"
                            }
                        ],
                        "Default": "Wait 20 Seconds"
                    },
                    "Copy Harmony Results to S3": {
                        "Type": "Task",
                        "Resource": "${module.browse_image_module.copy_harmony_results_to_s3_arn}",
                        "Parameters": {
                            "cma": {
                                "event.$": "$",
                                "task_config": {
                                    "cmr_environment": "{$.meta.cmr.cmrEnvironment}",
                                    "harmony_job": "{$.payload.harmony_job.job}",
                                    "current_item": "{$.current_item}",
                                    "cumulus_message": {
                                        "input": "{$.payload}"
                                    }
                                }
                            }
                        },
                        "Retry": [
                            {
                                "ErrorEquals": [
                                    "Lambda.ServiceException",
                                    "Lambda.AWSLambdaException",
                                    "Lambda.SdkClientException",
                                    "Lambda.TooManyRequestsException"
                                ],
                                "IntervalSeconds": 2,
                                "MaxAttempts": 6,
                                "BackoffRate": 2
                            }
                        ],
                        "End": true
                    },
                    "Harmony Fail": {
                        "Type": "Fail"
                    }
                }
            },
            "MaxConcurrency": 10,
            "ResultPath": "$.payload.big",
            "Next": "Generate Image Metadata"
        },
        "Generate Image Metadata": {
            "Type": "Task",
            "Resource": "${module.browse_image_module.generate_image_metadata_arn}",
            "Parameters": {
                "cma": {
                    "event.$": "$",
                    "task_config": {
                        "cumulus_message": {
                            "input": "{$.payload}"
                        }
                    }
                }
            },
            "Retry": [
                {
                    "ErrorEquals": [
                        "Lambda.ServiceException",
                        "Lambda.AWSLambdaException",
                        "Lambda.SdkClientException",
                        "Lambda.TooManyRequestsException"
                    ],
                    "IntervalSeconds": 2,
                    "MaxAttempts": 6,
                    "BackoffRate": 2
                }
            ],
            "Next": "Clean Output"
        },
        "Clean Output": {
            "Type": "Pass",
            "Next": "WorkflowSucceeded",
            "Parameters": {
                "cumulus_meta.$": "$.cumulus_meta",
                "meta": {
                    "buckets.$": "$.meta.buckets",
                    "cmr.$": "$.meta.cmr",
                    "collection.$": "$.meta.collection",
                    "provider.$": "$.meta.provider",
                    "stack.$": "$.meta.stack"
                },
                "payload": {
                    "granules.$": "$.payload.granules",
                    "big.$": "$.payload.big"
                },
                "exception.$": "$.exception",
                "task_config.$": "$.task_config"
            },
            "Comment": "Removes extra data from payload that is no longer necessary"
        },
        "WorkflowSucceeded": {
            "Type": "Succeed"
        }
    }
}
JSON
}