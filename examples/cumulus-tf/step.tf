# This example is deployable without cumulus installed for the purpose of testing the module in isolation; so it does not use terraform-aws-cumulus-workflow.zip
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "${local.ec2_resources_name}-BrowseImageWorkflow"
  role_arn = aws_iam_role.step.arn

  definition = module.bignbit_module.workflow_definition
}
