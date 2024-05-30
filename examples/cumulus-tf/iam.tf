data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "iam_assume_role_policy" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com", "lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "iam_policy" {

  statement {
    actions = [
       "autoscaling:CompleteLifecycleAction",
       "autoscaling:DescribeAutoScalingInstances",
       "autoscaling:DescribeLifecycleHooks",
       "autoscaling:RecordLifecycleActionHeartbeat",
       "cloudformation:DescribeStacks",
       "cloudwatch:GetMetricStatistics",
       "dynamodb:ListTables",
       "ec2:CreateNetworkInterface",
       "ec2:DeleteNetworkInterface",
       "ec2:DescribeInstances",
       "ec2:DescribeNetworkInterfaces",
       "ecr:BatchCheckLayerAvailability",
       "ecr:BatchGetImage",
       "ecr:GetAuthorizationToken",
       "ecr:GetDownloadUrlForLayer",
       "ecs:DeregisterContainerInstance",
       "ecs:DescribeClusters",
       "ecs:DescribeContainerInstances",
       "ecs:DescribeServices",
       "ecs:DiscoverPollEndpoint",
       "ecs:ListContainerInstances",
       "ecs:ListServices",
       "ecs:ListTaskDefinitions",
       "ecs:ListTasks",
       "ecs:Poll",
       "ecs:RegisterContainerInstance",
       "ecs:RunTask",
       "ecs:StartTelemetrySession",
       "ecs:Submit*",
       "ecs:UpdateContainerInstancesState",
       "events:DeleteRule",
       "events:DescribeRule",
       "events:DisableRule",
       "events:EnableRule",
       "events:ListRules",
       "events:PutRule",
       "kinesis:DescribeStream",
       "kinesis:GetRecords",
       "kinesis:GetShardIterator",
       "kinesis:ListStreams",
       "kinesis:PutRecord",
       "lambda:GetFunction",
       "lambda:GetLayerVersion",
       "lambda:invokeFunction",
       "logs:CreateLogGroup",
       "logs:CreateLogStream",
       "logs:DescribeLogStreams",
       "logs:PutLogEvents",
       "s3:ListAllMyBuckets",
       "sns:List*",
       "sns:publish",
       "ssm:GetParameter",
       "states:DescribeActivity",
       "states:DescribeExecution",
       "states:GetActivityTask",
       "states:GetExecutionHistory",
       "states:ListStateMachines",
       "states:SendTaskFailure",
       "states:SendTaskSuccess",
       "states:StartExecution",
       "states:StopExecution",
    ]
    resources = ["*"]
  }

  statement {
    actions = [
       "s3:AbortMultipartUpload",
       "s3:DeleteObject",
       "s3:DeleteObjectVersion",
       "s3:GetAccelerateConfiguration",
       "s3:GetBucket*",
       "s3:GetLifecycleConfiguration",
       "s3:GetObject*",
       "s3:GetReplicationConfiguration",
       "s3:ListBucket*",
       "s3:ListMultipartUploadParts",
       "s3:PutAccelerateConfiguration",
       "s3:PutBucket*",
       "s3:PutLifecycleConfiguration",
       "s3:PutObject*",
       "s3:PutReplicationConfiguration"
    ]
    #resources = [for b in local.all_bucket_names : "arn:aws:s3:::${b}/*"]
    resources = ["arn:aws:s3:::${local.ec2_resources_name}-*/*"]
  }

  statement {
    actions = [
      "s3:GetObject*",
    ]
    resources = ["arn:aws:s3:::*"]
  }

}

resource "aws_iam_role" "iam_execution" {
  name                 = "${var.prefix}_iam_execution_role"
  assume_role_policy   = data.aws_iam_policy_document.iam_assume_role_policy.json
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
}

resource "aws_iam_role_policy" "policy_attachment" {
  name   = "${var.prefix}_iam_role_policy"
  role   = aws_iam_role.iam_execution.id
  policy = data.aws_iam_policy_document.iam_policy.json
}