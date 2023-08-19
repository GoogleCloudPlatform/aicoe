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
resource "google_monitoring_notification_channel" "notification_channel" {
  count        = length(var.notification_email_addresses)
  project      = data.google_project.project.project_id
  enabled      = true
  display_name = "Send email to ${element(var.notification_email_addresses, count.index)}"
  type         = "email"

  labels = {
    email_address = "${element(var.notification_email_addresses, count.index)}"
  }
}

resource "google_monitoring_alert_policy" "ddos_policy" {
  display_name          = "ddos"
  notification_channels = google_monitoring_notification_channel.notification_channel.*.id
  combiner              = "OR"
  conditions {
    display_name = "Cloud Pub/Sub Topic - Publish requests"
    condition_threshold {
      filter          = "resource.type = \"pubsub_topic\" AND resource.labels.topic_id = \"${values(module.pubsub)[1].topic}\" AND metric.type = \"pubsub.googleapis.com/topic/send_request_count\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = var.notification_threshold
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_SUM"
        cross_series_reducer = "REDUCE_SUM"
        group_by_fields = [
          "metric.label.response_class",
          "metric.label.response_code"
        ]
      }
      trigger {
        count = 1
      }
    }
  }
}
