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

# Leaving here for reference - does not work
#resource "google_data_catalog_entry" "ddos_topic_entry" {
#  provider = google-beta
#  entry_id = "my-entity"
#
#  entry_group = "@pubsub"
#  user_specified_type = "DATA_STREAM"
#  linked_resource = "//pubsub.googleapis.com/projects/${data.google_project.project.project_id}/topics/${values(module.pubsub)[0].topic}"
#  schema = file("${path.module}/ddos/catalog_schema.json")
#}

module "gcloud-data-catalog-ddos" {
  source  = "terraform-google-modules/gcloud/google"
  version = "~> 2.0"

  platform = "linux"

  create_cmd_entrypoint  = "gcloud"
  create_cmd_body        = "data-catalog entries update --lookup-entry=\"pubsub.topic.\\`${data.google_project.project.project_id}\\`.\\`${values(module.pubsub)[0].topic}\\`\" --schema-from-file=\"${path.module}/./ddos/catalog_schema.yaml\""
  destroy_cmd_entrypoint = "gcloud"
  destroy_cmd_body       = "version"
}

module "gcloud-data-catalog-syn" {
  source  = "terraform-google-modules/gcloud/google"
  version = "~> 2.0"

  platform = "linux"

  create_cmd_entrypoint  = "gcloud"
  create_cmd_body        = "data-catalog entries update --lookup-entry=\"pubsub.topic.\\`${data.google_project.project.project_id}\\`.\\`${values(module.pubsub)[1].topic}\\`\" --schema-from-file=\"${path.module}/./syn/catalog_schema.yaml\""
  destroy_cmd_entrypoint = "gcloud"
  destroy_cmd_body       = "version"
}
