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

resource "google_pubsub_schema" "pubsub_schema" {
  name       = "${var.pubsub_schema}_${local.random_suffix}"
  project    = data.google_project.project.project_id
  type       = "AVRO"
  definition = file("./containers-security/pubsub_schema.avro")
}

resource "google_pubsub_topic" "pubsub_topic" {
  name    = "${var.pubsub_topic}_${local.random_suffix}"
  project = data.google_project.project.project_id
  depends_on = [
    google_pubsub_schema.pubsub_schema
  ]
  schema_settings {
    encoding = "JSON"
    schema   = "projects/${data.google_project.project.project_id}/schemas/${var.pubsub_schema}_${local.random_suffix}"
  }
  labels = local.labels_map
}

resource "google_pubsub_subscription" "pubsub_subscription" {
  name    = "${var.pubsub_subscription}_${local.random_suffix}"
  topic   = google_pubsub_topic.pubsub_topic.id
  project = data.google_project.project.project_id
  bigquery_config {
    table            = "${data.google_project.project.project_id}:streaming_${local.random_suffix}.${var.bq_table_streaming}_${local.random_suffix}"
    use_topic_schema = true
  }
  depends_on = [
    google_bigquery_table.bq_table
  ]

  labels = local.labels_map
}
