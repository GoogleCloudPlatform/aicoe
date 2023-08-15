/*
 Copyright 2023 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

data "google_project" "project" {
  project_id = data.terraform_remote_state.bootstrap.outputs.project_id
}

data "google_pubsub_topic" "pubsub_topic" {
  name = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_pubsub_topic_name
}

data "google_pubsub_subscription" "pubsub_subscription" {
  name = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_pubsub_subscription_name
}

locals {
  random_suffix = data.terraform_remote_state.bootstrap.outputs.random_suffix
  labels_map    = data.terraform_remote_state.bootstrap.outputs.labels_map
  dataset_id    = data.terraform_remote_state.s01_realtime_ingestion.outputs.google_bigquery_dataset_id
}
