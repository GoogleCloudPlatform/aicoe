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

resource "google_bigquery_dataset" "dataset" {
  dataset_id    = "streaming_${local.random_suffix}"
  friendly_name = "streaming_${local.random_suffix}"
  description   = "All real-time data from PubSub ingested into this dataset"
  location      = "US"
  project       = data.google_project.project.project_id
  labels        = local.labels_map
}

resource "google_bigquery_table" "bq_table" {
  dataset_id          = google_bigquery_dataset.dataset.dataset_id
  schema              = file("./containers-security/bq_schema.json")
  table_id            = "${var.bq_table_streaming}_${local.random_suffix}"
  deletion_protection = false
  project             = data.google_project.project.project_id
  labels              = local.labels_map
  depends_on = [
    google_bigquery_dataset.dataset
  ]
}
