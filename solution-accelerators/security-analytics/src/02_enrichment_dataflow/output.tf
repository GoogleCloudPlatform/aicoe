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

output "network_self_link" {
  value       = google_compute_network.composer-vpc.self_link
  description = "VPC network"
}
output "subnet_self_link" {
  value       = google_compute_subnetwork.composer-subnet.self_link
  description = "Subnet"
}
output "network_id" {
  value       = google_compute_network.composer-vpc.id
  description = "VPC network"
}
output "subnet_id" {
  value       = google_compute_subnetwork.composer-subnet.id
  description = "Subnet"
}
output "network_name" {
  value       = google_compute_network.composer-vpc.name
  description = "VPC network"
}
output "subnet_name" {
  value       = google_compute_subnetwork.composer-subnet.name
  description = "Subnet"
}
output "dataflow_sa_email" {
  value       = google_service_account.dataflow_sa.email
  description = "dataflow service account"
}
output "ddos_topic_name" {
  value       = values(module.pubsub)[0].topic
  description = "dos topic name"
}
output "syn_topic_name" {
  value       = values(module.pubsub)[1].topic
  description = "syn topic name"
}
