resource "null_resource" "temp_resource" {}

resource "time_sleep" "wait_in_seconds" {
  triggers = {
    always_run = "${timestamp()}"
  }
  depends_on = [null_resource.temp_resource]

  create_duration = var.sleep_in_seconds
}
