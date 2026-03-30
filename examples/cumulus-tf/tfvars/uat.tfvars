# stage: dev, sandbox, sit, uat, prod
bignbit_stage = "uat"
bignbit_cmr_environment = "UAT"
prefix = "podaac-uat-svc"

gibs_region="us-east-1"
gibs_queue_name="gitc-uat-PODAAC-IN.fifo"

harmony_job_status_max_attempts = 40
harmony_job_status_backoff_rate = 1.1
harmony_job_status_max_delay_seconds = 60