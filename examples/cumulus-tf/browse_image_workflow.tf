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
