terraform {
  backend "gcs" {
    bucket = "${state_bucket}"
    prefix = "terraform/02_enrichment_dataflow/state"
  }
}

data "terraform_remote_state" "bootstrap" {
  backend = "gcs"

  config = {
    bucket = "${state_bucket}"
    prefix = "terraform/bootstrap/state"
  }
}

data "terraform_remote_state" "s01_realtime_ingestion" {
  backend = "gcs"

  config = {
    bucket = "${state_bucket}"
    prefix = "terraform/01_realtime_ingestion/state"
  }
}
