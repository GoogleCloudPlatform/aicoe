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

module "projects_iam_account" {
  source                = "../modules/security/projects_iam_account"
  project_id            = data.google_project.project.project_id
  role_name             = var.project_iam_sa_role
  service_account_email = "${data.google_project.project.number}@cloudservices.gserviceaccount.com"
}

module "service_account" {
  source = "../modules/security/service_account"

  count                 = length(var.pubsub_service_account_roles)
  project_id            = data.google_project.project.project_id
  role_name             = var.pubsub_service_account_roles[count.index]
  service_account_email = "${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

locals {
  random_suffix = data.terraform_remote_state.bootstrap.outputs.random_suffix
  labels_map    = data.terraform_remote_state.bootstrap.outputs.labels_map
}
