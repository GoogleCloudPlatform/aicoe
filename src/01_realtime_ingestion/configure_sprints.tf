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

data "template_file" "environment_sh_tpl" {
  template = file("${path.module}/templates/environment.sh.tpl")
  vars = {
    project_id         = data.google_project.project.project_id
    project_number     = data.google_project.project.number
    region             = data.terraform_remote_state.bootstrap.outputs.region
    random_suffix      = local.random_suffix
    pubsub_topic_id    = google_pubsub_topic.pubsub_topic.id
    pubsub_topic_name  = google_pubsub_topic.pubsub_topic.name
    bq_dataset_id      = google_bigquery_dataset.dataset.dataset_id
    bq_table_id        = google_bigquery_table.bq_table.table_id
    pubsub_schema_id   = google_pubsub_schema.pubsub_schema.id
    pubsub_schema_name = google_pubsub_schema.pubsub_schema.name
  }
}

resource "local_file" "environment_sh" {
  content         = data.template_file.environment_sh_tpl.rendered
  filename        = "${path.module}/generated/environment.sh"
  file_permission = 0644
}
