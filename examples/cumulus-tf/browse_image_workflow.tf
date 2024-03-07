module "browse_image_workflow" {
  source = "../../terraform"
  prefix          = var.prefix
  name            = "BrowseImageWorkflow"
  workflow_config = module.cumulus.workflow_config
  system_bucket   = var.system_bucket

  definition = module.bignbit_module.browse_image_state_machine_definition
}
