terraform {
  backend "gcs" {
    bucket = "${state_bucket}"
    prefix = "terraform/05_bqml/state"
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

data "terraform_remote_state" "s02_enrichment_dataflow" {
  backend = "gcs"

  config = {
    bucket = "${state_bucket}"
    prefix = "terraform/02_enrichment_dataflow/state"
  }
}

data "terraform_remote_state" "s03_feature_store" {
  backend = "gcs"

  config = {
    bucket = "${state_bucket}"
    prefix = "terraform/03_feature_store/state"
  }
}

data "terraform_remote_state" "s04_anomaly_detection" {
  backend = "gcs"

  config = {
    bucket = "${state_bucket}"
    prefix = "terraform/04_anomaly_detection/state"
  }
}
