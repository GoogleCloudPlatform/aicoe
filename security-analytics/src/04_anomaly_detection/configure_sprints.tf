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
locals {
  templates = {
    "environment.sh"     = "environment.sh.tpl",
    "ddos_settings.json" = "ddos_settings.json.tpl",
    "model_upload.json"  = "model_upload.json.tpl",
  }
}

data "template_file" "generated" {
  for_each = local.templates

  template = file("${path.module}/templates/${each.value}")
  vars = {
    project_id            = data.google_project.project.project_id
    project_number        = data.google_project.project.number
    region                = local.region
    random_suffix         = local.random_suffix
    network_id            = data.google_compute_network.composer-vpc.id
    subnetwork_id         = data.google_compute_subnetwork.composer-subnet.id
    subnetwork_self_link  = data.google_compute_subnetwork.composer-subnet.self_link
    service_account_email = data.google_service_account.dataflow_sa.email
    ddos_bucket           = local.ddos_bucket
    containersec_bucket   = local.containersec_bucket
    composer_dag_path     = local.composer_dag_path
    ddos_incidents_topic  = values(module.pubsub)[1].id
    endpoint_name         = local.endpoint_name
    endpoint_id           = google_vertex_ai_endpoint.endpoint.id
    model_name            = local.model_name
    model_upload_location = "gs://${local.ddos_bucket}/${var.model_dst_dir}"
  }
}

resource "local_file" "generated" {
  for_each = local.templates

  content         = data.template_file.generated[each.key].rendered
  filename        = "${path.module}/generated/${each.key}"
  file_permission = 0644
}
