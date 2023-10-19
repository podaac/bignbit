resource "null_resource" "get_newest_CMA" {
  triggers = {
    always_run = var.cma_version
  }
  provisioner "local-exec" {
    command = "curl -L -o cumulus-message-adapter.zip https://github.com/nasa/cumulus-message-adapter/releases/download/${var.cma_version}/cumulus-message-adapter.zip"
  }
}

resource "aws_lambda_layer_version" "cumulus_message_adapter" {
  depends_on  = [null_resource.get_newest_CMA]
  filename    = "cumulus-message-adapter.zip"
  layer_name  = "${var.prefix}_Cumulus_Message_Adapter"
  description = "Layer supporting the Cumulus Message Adapter https://github.com/nasa/cumulus-message-adapter version ${var.cma_version}"
}