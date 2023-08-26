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
output "containersec_incidents_topic_id" {
  value = values(module.pubsub)[0].id
}

output "containersec_incidents_topic_name" {
  value = values(module.pubsub)[0].topic
}

output "ddos_incidents_topic_id" {
  value = values(module.pubsub)[1].id
}

output "ddos_incidents_topic_name" {
  value = values(module.pubsub)[1].topic
}

#output "alerting_notification_channels" {
#  value = [data.google_monitoring_notification_channel.notification_channel.name]
#}

output "alerting_notification_channels" {
  value = google_monitoring_notification_channel.notification_channel.*.id
}

output "ddos_alerting_policy_name" {
  value = google_monitoring_alert_policy.ddos_policy.name
}

output "endpoint_id" {
  value = google_vertex_ai_endpoint.endpoint.id
}

output "endpoint_name" {
  value = local.endpoint_name
}

output "model_upload_location" {
  value = "gs://${local.ddos_bucket}/${var.model_dst_dir}"
}

output "model_name_prefix" {
  value = "anomaly-detection-${local.random_suffix}"
}
