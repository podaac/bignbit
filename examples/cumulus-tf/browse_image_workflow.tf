# In a typical cumulus installation, this is how you would define the workflow:
/*
module "browse_image_workflow" {
  source          = "https://github.com/nasa/cumulus/releases/download/v16.1.2/terraform-aws-cumulus-workflow.zip"
  prefix          = var.prefix
  name            = "BrowseImageWorkflow"
  workflow_config = module.cumulus.workflow_config
  system_bucket   = var.system_bucket
  tags            = merge(local.tags, { application = "BrowseImageWorkflow" })

  state_machine_definition = module.bignbit_module.workflow_definition
}
*/

# This example is deployable without cumulus installed for the purpose of testing the module in isolation; so it does not use terraform-aws-cumulus-workflow.zip
resource "aws_sfn_state_machine" "sfn_state_machine" {
  name     = "${local.ec2_resources_name}-BrowseImageWorkflow"
  role_arn = aws_iam_role.step.arn

  definition = module.bignbit_module.workflow_definition
}
