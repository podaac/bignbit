{
  "Comment": "Run BIG & BIT",
  "StartAt":"GetDatasetConfiguration",
  "States":{
    "GetDatasetConfiguration":{
      "Type":"Task",
      "Resource":"${GetDatasetConfigurationLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "config_bucket_name":"${ConfigBucket}",
            "config_key_name.$":"States.Format('${ConfigDir}/{}.cfg', $.meta.collection.name)",
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":6,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
            "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
        }
      ],
      "Next":"Get Granule umm_json"
    },
    "Get Granule umm_json":{
      "Type":"Task",
      "Resource":"${GetGranuleUmmJsonLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "cmr_environment":"{$.meta.cmr.cmrEnvironment}",
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException",
            "ReadTimeout",
            "HTTPError"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":16,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
             "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
        }
      ],
      "Next":"Send to Harmony?"
    },
    "Send to Harmony?":{
      "Type":"Choice",
      "Choices":[
        {
          "And":[
            {
              "Variable":"$.payload.datasetConfigurationForBIG.config.sendToHarmony",
              "IsPresent":true
            },
            {
              "Variable":"$.payload.datasetConfigurationForBIG.config.sendToHarmony",
              "BooleanEquals":true
            }
          ],
          "Comment":"If sendToHarmony is true",
          "Next":"Get Collection Concept Id"
        }
      ],
      "Default":"Identify Image File"
    },
    "Identify Image File":{
      "Type":"Task",
      "Resource":"${IdentifyImageFileLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":6,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
            "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
       }
      ],
      "Next":"Apply OPERA HLS Treatment?"
    },
    "Apply OPERA HLS Treatment?":{
      "Type":"Choice",
      "Choices":[
        {
          "And":[
            {
              "Variable":"$.payload.datasetConfigurationForBIG.config.operaHLSTreatment",
              "IsPresent":true
            },
            {
              "Variable":"$.payload.datasetConfigurationForBIG.config.operaHLSTreatment",
              "BooleanEquals":true
            }
          ],
          "Comment":"If operaHLSTreatment is true",
          "Next":"Apply OPERA HLS Treatment"
        }
      ],
      "Default":"Generate Image Metadata"
    },
    "Apply OPERA HLS Treatment":{
      "Type":"Task",
      "Resource":"${ApplyOperaHLSTreatmentLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":6,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
            "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
        }
      ],
      "Next":"Generate Image Metadata"
    },
    "Get Collection Concept Id":{
      "Type":"Task",
      "Resource":"${GetCollectionConceptIdLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "collection_shortname":"{$.meta.collection.name}",
            "cmr_provider":"{$.meta.cmr.provider}",
            "cmr_environment":"{$.meta.cmr.cmrEnvironment}",
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException",
            "ReadTimeout",
            "HTTPError"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":6,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
            "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
        }
      ],
      "Next":"Convert Variables To PNG"
    },
    "Convert Variables To PNG":{
      "Type":"Map",
      "ItemsPath":"$.payload.datasetConfigurationForBIG.config.imgVariables",
      "ItemSelector":{
        "cumulus_meta.$":"$.cumulus_meta",
        "meta.$":"$.meta",
        "payload.$":"$.payload",
        "task_config.$":"$.task_config",
        "current_item.$":"$$.Map.Item.Value"
      },
      "ItemProcessor":{
        "ProcessorConfig":{
          "Mode":"INLINE"
        },
        "StartAt":"Submit Harmony Job",
        "States":{
          "Submit Harmony Job":{
            "Type":"Task",
            "Parameters":{
              "cma":{
                "event.$":"$",
                "task_config":{
                  "granule":"{$.payload.granules[0]}",
                  "cmr_provider":"{$.cmr_provider}",
                  "collection":"{$.meta.collection}",
                  "collection_concept_id":"{$.payload.collection_concept_id}",
                  "cmr_environment":"{$.meta.cmr.cmrEnvironment}",
                  "cmr_clientid":"{$.meta.cmr.clientId}",
                  "current_item":"{$.current_item}",
                  "big_config":"{$.payload.datasetConfigurationForBIG}",
                  "cumulus_message":{
                    "input":"{$.payload}"
                  }
                }
              }
            },
            "Resource":"${SubmitHarmonyJobLambda}",
            "Next":"Wait 20 Seconds"
          },
          "Wait 20 Seconds":{
            "Type":"Wait",
            "Seconds":20,
            "Next":"Get Harmony Job Status"
          },
          "Get Harmony Job Status":{
            "Type":"Task",
            "Resource":"${GetHarmonyJobStatusLambda}",
            "Parameters":{
              "cma":{
                "event.$":"$",
                "task_config":{
                  "cmr_environment":"{$.meta.cmr.cmrEnvironment}",
                  "harmony_job":"{$.payload.harmony_job.job}",
                  "cumulus_message":{
                    "input":"{$.payload}"
                  }
                }
              }
            },
            "Retry":[
              {
                "ErrorEquals":[
                  "Lambda.ServiceException",
                  "Lambda.AWSLambdaException",
                  "Lambda.SdkClientException",
                  "Lambda.TooManyRequestsException"
                ],
                "IntervalSeconds":2,
                "MaxAttempts":6,
                "BackoffRate":2
              },
              {
                "ErrorEquals": [
                  "Lambda.Unknown"
               ],
                "BackoffRate": 2,
                "IntervalSeconds": 2,
                "MaxAttempts": 2
              }
            ],
            "Next":"Job Complete?"
          },
          "Job Complete?":{
            "Type":"Choice",
            "Choices":[
              {
                "Variable":"$.payload.harmony_job_status",
                "StringMatches":"successful",
                "Next":"Job Successful",
                "Comment":"Job successful"
              },
              {
                "And":[
                  {
                    "Not":{
                      "Variable":"$.payload.harmony_job_status",
                      "StringMatches":"running"
                    }
                  },
                  {
                    "Not":{
                      "Variable":"$.payload.harmony_job_status",
                      "StringMatches":"accepted"
                    }
                  }
                ],
                "Next":"Fail",
                "Comment":"Job not successful"
              }
            ],
            "Default":"Wait 20 Seconds"
          },
          "Job Successful":{
            "Type":"Succeed"
          },
          "Fail":{
            "Type":"Fail"
          }
        }
      },
      "MaxConcurrency":10,
      "ResultPath":"$.payload.big",
      "Next":"Generate Image Metadata"
    },
    "Generate Image Metadata":{
      "Type":"Task",
      "Resource":"${GenerateImageMetadataLambda}",
      "Parameters":{
        "cma":{
          "event.$":"$",
          "task_config":{
            "cumulus_message":{
              "input":"{$.payload}"
            }
          }
        }
      },
      "Retry":[
        {
          "ErrorEquals":[
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds":2,
          "MaxAttempts":6,
          "BackoffRate":2
        },
        {
          "ErrorEquals": [
            "Lambda.Unknown"
          ],
          "BackoffRate": 2,
          "IntervalSeconds": 2,
          "MaxAttempts": 2
        }
      ],
      "Next":"Clean Output"
    },
    "Clean Output":{
      "Type":"Pass",
      "Next":"BuildImageSets",
      "Parameters":{
        "cumulus_meta.$": "$.cumulus_meta",
        "meta": {
          "buckets.$": "$.meta.buckets",
          "cmr.$": "$.meta.cmr",
          "collection.$": "$.meta.collection",
          "provider.$": "$.meta.provider",
          "stack.$": "$.meta.stack"
        },
        "payload":{
          "granules.$":"$.payload.granules",
          "big.$":"$.payload.big"
        },
        "exception.$":"$.exception",
        "task_config.$":"$.task_config"
      },
      "Comment":"Removes extra data from payload that is no longer necessary"
    },
    "BuildImageSets": {
      "Parameters": {
        "cma": {
          "event.$": "$",
          "task_config": {
            "collection": "{$.meta.collection}",
            "cmr_provider": "{$.meta.cmr.provider}",
            "cumulus_message": {
              "input": "{$.payload}"
            }
          }
        }
      },
      "Type": "Task",
      "Resource": "${BuildImageSetsLambda}",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 3
        }
      ],
      "Next": "TransferImageSets"
    },
    "TransferImageSets": {
      "Type": "Map",
      "InputPath": "$",
      "ItemsPath": "$.payload.pobit",
      "MaxConcurrency": 20,
      "Iterator": {
        "StartAt": "SendToGITC",
        "States": {
          "SendToGITC": {
            "Parameters": {
              "FunctionName": "${SendToGITCLambda}",
              "Payload": {
                "cma": {
                  "event.$": "$",
                  "task_config": {
                    "collection": "{$.collection}",
                    "cmr_provider": "{$.cmr_provider}",
                    "cumulus_message": {
                      "input": "{$}"
                    }
                  }
                }
              }
            },
            "Type": "Task",
            "Resource": "arn:aws:states:::lambda:invoke",
            "TimeoutSeconds": 86400,
            "ResultPath": "$.cnm",
            "Next": "SaveCNMMessage"
          },
          "SaveCNMMessage": {
            "Type": "Task",
            "Resource": "${SaveCNMMessageLambda}",
            "Parameters": {
              "cma": {
                "event.$": "$",
                "task_config": {
                  "collection": "{$.collection_name}",
                  "granule_ur": "{$.granule_ur}",
                  "cnm": "{$.cnm.Payload.payload}",
                  "pobit_audit_bucket": "${PobitAuditBucket}",
                  "pobit_audit_path": "${PobitAuditPath}",
                  "cumulus_message": {
                    "input": "{$}"
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
          }
        }
      },
      "ResultPath": "$.payload.pobit",
      "Catch": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "ResultPath": "$.exception",
          "Next": "WorkflowFailed"
        }
      ],
      "Retry": [
        {
          "ErrorEquals": [
            "States.ALL"
          ],
          "IntervalSeconds": 2,
          "MaxAttempts": 3
        }
      ],
      "Next": "WorkflowSucceeded"
    },
    "WorkflowSucceeded": {
      "Type": "Succeed"
    },
    "WorkflowFailed": {
      "Type": "Fail",
      "Cause": "Workflow failed"
    }
  }
}
