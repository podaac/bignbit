
data "aws_iam_policy_document" "states_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["states.${data.aws_region.current.name}.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "step" {
  name                 = "${local.ec2_resources_name}-sfn-steprole"
  assume_role_policy   = data.aws_iam_policy_document.states_assume_role_policy.json
  permissions_boundary = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/NGAPShRoleBoundary"
}

data "aws_iam_policy_document" "step_policy" {
  statement {
    actions = [
      "lambda:InvokeFunction",
      "ecr:*",
      "cloudtrail:LookupEvents",
      "ecs:RunTask",
      "ecs:StopTask",
      "ecs:DescribeTasks",
      "autoscaling:Describe*",
      "cloudwatch:*",
      "logs:*",
      "sns:*",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:GetRole",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "step" {
  name   = "${var.prefix}_step_policy"
  role   = aws_iam_role.step.id
  policy = data.aws_iam_policy_document.step_policy.json
}
