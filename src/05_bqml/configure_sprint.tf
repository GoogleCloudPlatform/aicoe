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
    "environment.sh"             = "environment.sh.tpl",
    "containersec_settings.json" = "containersec_settings.json.tpl",
  }
}

data "template_file" "generated" {
  for_each = local.templates

  template = file("${path.module}/templates/${each.value}")
  vars = {
    project_id                        = data.google_project.project.project_id
    project_number                    = data.google_project.project.number
    region                            = local.region
    random_suffix                     = local.random_suffix
    network_id                        = data.google_compute_network.composer-vpc.id
    network_self_link                 = data.google_compute_network.composer-vpc.self_link
    subnet_id                         = data.google_compute_subnetwork.composer-subnet.id
    subnet_self_link                  = data.google_compute_subnetwork.composer-subnet.self_link
    service_account_email             = data.google_service_account.dataflow_sa.email
    ddos_bucket                       = local.ddos_bucket
    containersec_bucket               = local.containersec_bucket
    composer_dag_path                 = local.composer_dag_path
    containersec_incidents_topic_name = data.google_pubsub_topic.containersec_incidents_pubsub_topic.name
    containersec_incidents_topic_id   = data.google_pubsub_topic.containersec_incidents_pubsub_topic.id
    ddos_incidents_topic_name         = data.google_pubsub_topic.ddos_incidents_pubsub_topic.name
    ddos_incidents_topic_id           = data.google_pubsub_topic.ddos_incidents_pubsub_topic.id
    ddos_topic                        = data.google_pubsub_topic.ddos_pubsub_topic.name
    model_name                        = "%model_name%"
    model_endpoint_name               = "%model_endpoint_name%"
    model_upload_location             = "%model_upload_location%"
  }
}

resource "local_file" "generated" {
  for_each = local.templates

  content         = data.template_file.generated[each.key].rendered
  filename        = "${path.module}/generated/${each.key}"
  file_permission = 0644
}
