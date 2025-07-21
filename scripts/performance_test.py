"""
This script starts and monitors AWS Step Function executions, calculates execution statistics,
and outputs the results. It uses the boto3 library to interact with AWS Step Functions.

Usage:
    python performance_test.py --profile <AWS_PROFILE> --state-machine-arn <STATE_MACHINE_ARN> --count <NUMBER_OF_EXECUTIONS>

Arguments:
    --profile: The AWS CLI profile name to use for authentication.
    --state-machine-arn: The ARN of the Step Function state machine to execute.
    --count: The number of Step Function executions to submit (default is 1).
"""

import pathlib
from os.path import dirname, realpath, basename
import boto3
import datetime
import time
import argparse
import logging
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Start and monitor Step Function executions.")
parser.add_argument("--profile", required=True, help="boto3 profile name")
parser.add_argument("--state-machine-arn", required=True, help="Step Function state machine ARN")
parser.add_argument("--count", type=int, default=1, help="Number of Step Function executions to submit")
args = parser.parse_args()

# Create a boto3 session using the specified profile
session = boto3.Session(profile_name=args.profile)
client = session.client('stepfunctions')
now = datetime.datetime.now(tz=datetime.timezone.utc)

# Path to the sample message file
message = pathlib.Path(dirname(realpath(__file__))).joinpath('../tests/sample_messages').joinpath(
    'cma.uat.workflow-input.OPERA_L3_DSWx-S1_T45QYD_20241001T121219Z_20241206T065726Z_S1A_30_v1.0.json'
).read_text()

# Dictionary to store submission details
submissions: dict[str, dict] = {}

# Start the specified number of Step Function executions
for i in range(args.count):
    response = client.start_execution(
        stateMachineArn=args.state_machine_arn,
        name=f'{now.strftime("%Y%m%dT%H%M%S")}_{basename(__file__)}_{i}',
        input=message
    )
    logging.info(f"Started execution {i} with ARN: {response['executionArn']}")
    submissions[response['executionArn']] = {'i': i} | response

# Monitor the executions until all are complete
all_complete = False
while not all_complete:
    all_complete = True
    for executionArn, submission in submissions.items():
        # Check the status of each execution
        if 'status' not in submission or submission['status'] == 'RUNNING':
            response = client.describe_execution(
                executionArn=executionArn
            )
            submissions[executionArn].update(response)
            if response['status'] == 'RUNNING':
                all_complete = False
                break
        logging.info(f"Execution {submission['i']} is complete with status: {submission['status']}")
    if not all_complete:
        logging.info("Waiting for executions to complete...")
        time.sleep(10)

# Calculate statistics for execution durations
data = [
    (sub['stopDate'] - sub['startDate']).total_seconds()
    for sub in submissions.values()
    if 'stopDate' in sub and 'startDate' in sub
]

# Compute statistical metrics
mean_value = statistics.mean(data)
median_value = statistics.median(data)
try:
    mode_value = statistics.mode(data)  # Raises StatisticsError if no unique mode
except statistics.StatisticsError:
    mode_value = "No unique mode"
stdev_value = statistics.stdev(data)
variance_value = statistics.variance(data)

# Log the calculated statistics
logging.info(f"Count: {len(data)}")
logging.info(f"Mean: {mean_value}")
logging.info(f"Median: {median_value}")
logging.info(f"Mode: {mode_value}")
logging.info(f"Standard Deviation: {stdev_value}")
logging.info(f"Variance: {variance_value}")