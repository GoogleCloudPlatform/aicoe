data "google_project" "project" {
  project_id = data.terraform_remote_state.bootstrap.outputs.project_id
}

data "google_pubsub_topic" "containersec_pubsub_topic" {
  name = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_pubsub_topic_name
}

data "google_pubsub_subscription" "containersec_pubsub_subscription" {
  name = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_pubsub_subscription_name
}

data "google_pubsub_topic" "ddos_pubsub_topic" {
  name = data.terraform_remote_state.s02_enrichment_dataflow.outputs.ddos_topic_name
}

data "google_pubsub_topic" "syn_pubsub_topic" {
  name = data.terraform_remote_state.s02_enrichment_dataflow.outputs.syn_topic_name
}

data "google_compute_network" "composer-vpc" {
  name = data.terraform_remote_state.s02_enrichment_dataflow.outputs.network_name
}

data "google_compute_subnetwork" "composer-subnet" {
  self_link = data.terraform_remote_state.s02_enrichment_dataflow.outputs.subnet_self_link
}

data "google_service_account" "dataflow_sa" {
  account_id = data.terraform_remote_state.s02_enrichment_dataflow.outputs.dataflow_sa_email
}

locals {
  random_suffix = data.terraform_remote_state.bootstrap.outputs.random_suffix
  labels_map    = data.terraform_remote_state.bootstrap.outputs.labels_map
  dataset_id    = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_bigquery_dataset_id
  region        = data.terraform_remote_state.bootstrap.outputs.region
}
