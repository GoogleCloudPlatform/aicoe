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

resource "google_service_account" "dataflow_sa" {
  account_id   = "dataflow-sa-${local.random_suffix}"
  display_name = "Dataflow Service Account"
}

resource "google_project_iam_member" "dataflow-account" {
  for_each = toset(var.df_roles)
  project  = data.google_project.project.project_id
  role     = each.value
  member   = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "composer-worker" {
  project = data.google_project.project.project_id
  role    = "roles/composer.worker"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_project_iam_member" "cloudservices-account" {
  project = data.google_project.project.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${data.google_project.project.number}@cloudservices.gserviceaccount.com"
}

resource "google_project_iam_member" "composer-worker-account" {
  project = data.google_project.project.project_id
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.dataflow_sa.email}"
}

resource "google_service_account_iam_member" "custom_service_account" {
  service_account_id = google_service_account.dataflow_sa.name
  role               = "roles/composer.ServiceAgentV2Ext"
  member             = "serviceAccount:service-${data.google_project.project.number}@cloudcomposer-accounts.iam.gserviceaccount.com"
}
