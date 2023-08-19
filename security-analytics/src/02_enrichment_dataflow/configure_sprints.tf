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
    project_id      = data.google_project.project.project_id
    project_number  = data.google_project.project.number
    region          = data.terraform_remote_state.bootstrap.outputs.region
    random_suffix   = data.terraform_remote_state.bootstrap.outputs.random_suffix
    dataflow_sa_id  = google_service_account.dataflow_sa.email
    network_id      = google_compute_network.composer-vpc.id
    subnetwork_id   = google_compute_subnetwork.composer-subnet.id
    dataset_id      = local.dataset_id
    ddos_topic_name = values(module.pubsub)[0].topic
    syn_topic_name  = values(module.pubsub)[1].topic
    ddos_topic_id   = values(module.pubsub)[0].id
    syn_topic_id    = values(module.pubsub)[1].id
    ddos_table_id   = google_bigquery_table.ddos_streaming.table_id
    syn_table_id    = google_bigquery_table.syn_streaming.table_id
  }
}

resource "local_file" "environment_sh" {
  content         = data.template_file.environment_sh_tpl.rendered
  filename        = "${path.module}/generated/environment.sh"
  file_permission = 0644
}
