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

data "template_file" "ddos_streaming_job_sql" {
  template = file("${path.module}/templates/dataflow_ddos_topic_query.sql.tpl")
  vars = {
    project_id    = data.google_project.project.project_id
    random_suffix = data.terraform_remote_state.bootstrap.outputs.random_suffix
    topic_id      = values(module.pubsub)[0].topic
  }
}

resource "google_dataflow_flex_template_job" "ddos_streaming_job" {
  provider                = google-beta
  name                    = "ddos-streaming-job-${local.random_suffix}"
  container_spec_gcs_path = "gs://dataflow-sql-templates-us-central1/latest/sql_launcher_flex_template"
  parameters = {
    serviceAccount  = google_service_account.dataflow_sa.email
    network         = google_compute_network.composer-vpc.self_link
    subnetwork      = google_compute_subnetwork.composer-subnet.self_link
    usePublicIps    = false
    dryRun          = false
    queryParameters = "[]"
    queryString     = data.template_file.ddos_streaming_job_sql.rendered
    outputs         = <<EOF
[
    {
        "type": "bigquery",
        "table": {
            "projectId": "${data.google_project.project.project_id}", 
            "datasetId": "${local.dataset_id}",
            "tableId": "ddos_streaming"
            },
        "writeDisposition": "WRITE_APPEND"
    }
]
EOF
  }

  lifecycle {
    ignore_changes = [labels["goog-dataflow-sql-version"]]
  }

}

data "template_file" "syn_streaming_job_sql" {
  template = file("${path.module}/templates/dataflow_syn_topic_query.sql.tpl")
  vars = {
    project_id    = data.google_project.project.project_id
    random_suffix = data.terraform_remote_state.bootstrap.outputs.random_suffix
    topic_id      = values(module.pubsub)[1].topic
  }
}

resource "google_dataflow_flex_template_job" "syn_streaming_job" {
  provider                = google-beta
  name                    = "syn-streaming-job-${local.random_suffix}"
  container_spec_gcs_path = "gs://dataflow-sql-templates-us-central1/latest/sql_launcher_flex_template"
  parameters = {
    serviceAccount  = google_service_account.dataflow_sa.email
    network         = google_compute_network.composer-vpc.self_link
    subnetwork      = google_compute_subnetwork.composer-subnet.self_link
    usePublicIps    = false
    dryRun          = false
    queryParameters = "[]"
    queryString     = data.template_file.syn_streaming_job_sql.rendered
    outputs         = <<EOF
[
    {
        "type": "bigquery",
        "table": {
            "projectId": "${data.google_project.project.project_id}", 
            "datasetId": "${local.dataset_id}",
            "tableId": "syn_streaming"
            },
        "writeDisposition": "WRITE_APPEND"
    }
]
EOF
  }

  lifecycle {
    ignore_changes = [labels["goog-dataflow-sql-version"]]
  }

}
