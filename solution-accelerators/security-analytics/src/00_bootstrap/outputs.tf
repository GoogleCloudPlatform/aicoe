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

output "project_id" {
  description = "Project ID"
  value       = data.google_project.project.project_id
}
output "project_number" {
  description = "Project Number"
  value       = data.google_project.project.number
}
output "region" {
  description = "Default GCP region"
  value       = var.region
}
output "zone" {
  description = "Default GCP zone"
  value       = var.zone
}
output "state_bucket" {
  description = "Random suffix"
  value       = var.state_bucket
}
output "random_suffix" {
  description = "Random suffix used across resources"
  value       = random_string.random_suffix.result
}
output "labels_map" {
  value = var.labels_map
}
