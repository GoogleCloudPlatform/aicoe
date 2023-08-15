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


variable "sprints" {
  type = list(any)
  default = [
    "01_realtime_ingestion",
    "02_enrichment_dataflow",
    "03_feature_store",
    "04_anomaly_detection",
    "05_bqml",
    "06_visualization",
  ]
}

data "template_file" "environment_sh_tpl" {
  template = file("${path.module}/templates/environment.sh.tpl")
  vars = {
    project_id     = data.google_project.project.project_id
    project_number = data.google_project.project.number
    region         = var.region
    zone           = var.zone
    random_suffix  = random_string.random_suffix.result
  }
}

resource "local_file" "sprint_environment_sh_sprint_00" {
  content         = data.template_file.environment_sh_tpl.rendered
  filename        = "${path.module}/generated/environment.sh"
  file_permission = 0644
}

resource "local_file" "backend_tpl" {
  for_each = {
    "realtime_ingestion"  = "01_realtime_ingestion"
    "enrichment_dataflow" = "02_enrichment_dataflow"
    "feature_store"       = "03_feature_store"
    "anomaly_detection"   = "04_anomaly_detection"
    "bqml"                = "05_bqml"
    "visualization"       = "06_visualization"
  }
  content         = templatefile("${path.module}/../${each.value}/templates/backend.tf.tpl", { state_bucket = var.state_bucket, sprint_name = each.key })
  filename        = "${path.module}/../${each.value}/backend.auto.tf"
  file_permission = 0644
}
