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

resource "google_bigquery_table" "ddos_streaming" {
  dataset_id          = local.dataset_id
  schema              = file("./ddos/bq_schema.json")
  table_id            = "ddos_streaming"
  deletion_protection = false
  project             = data.google_project.project.project_id
  labels              = local.labels_map
}

resource "google_bigquery_table" "syn_streaming" {
  dataset_id          = local.dataset_id
  schema              = file("./syn/bq_schema.json")
  table_id            = "syn_streaming"
  deletion_protection = false
  project             = data.google_project.project.project_id
  labels              = local.labels_map
}
