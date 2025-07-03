import pathlib
from os.path import dirname, realpath

import boto3
import datetime

import time
import argparse

parser = argparse.ArgumentParser(description="Start and monitor Step Function executions.")
parser.add_argument("--profile", required=True, help="boto3 profile name")
parser.add_argument("--state-machine-arn", required=True, help="Step Function state machine ARN")
parser.add_argument("--count", type=int, default=1, help="Number of Step Function executions to submit")
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
client = session.client('stepfunctions')
now = datetime.datetime.now(tz=datetime.timezone.utc)

message = pathlib.Path(dirname(realpath(__file__))).joinpath('sample_messages').joinpath('cma.uat.workflow-input.OPERA_L3_DSWx-S1_T45QYD_20241001T121219Z_20241206T065726Z_S1A_30_v1.0.json')

submissions: dict[str, dict] = {}
for i in range(args.count):
    response = client.start_execution(
        stateMachineArn=args.state_machine_arn,
        name=f'{now.strftime("%Y%m%dT%H%M%S")}_{i}_fg',
        input=message
    )
    print(f"Started execution {i} with ARN: {response['executionArn']}")
    submissions[response['executionArn']] = {'i': i} | response

all_complete = False
while not all_complete:
    all_complete = True
    for executionArn, submission in submissions.items():
        if 'status' not in submission or submission['status'] == 'RUNNING':
            response = client.describe_execution(
                executionArn=executionArn
            )
            submissions[executionArn].update(response)
            if response['status'] == 'RUNNING':
                all_complete = False
                break
        print(f"Execution {submission['i']} is complete with status: {submission['status']}")
    if not all_complete:
        print("Waiting for executions to complete...")
        time.sleep(10)

import statistics

data = [
    (sub['stopDate'] - sub['startDate']).total_seconds()
    for sub in submissions.values()
    if 'stopDate' in sub and 'startDate' in sub
]

mean_value = statistics.mean(data)
median_value = statistics.median(data)
try:
    mode_value = statistics.mode(data) # Raises StatisticsError if no unique mode
except statistics.StatisticsError:
    mode_value = "No unique mode"
stdev_value = statistics.stdev(data)
variance_value = statistics.variance(data)

print(f"Count: {len(data)}")
print(f"Mean: {mean_value}")
print(f"Median: {median_value}")
print(f"Mode: {mode_value}")
print(f"Standard Deviation: {stdev_value}")
print(f"Variance: {variance_value}")