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
resource "google_vertex_ai_endpoint" "endpoint" {
  display_name = local.endpoint_name
  name         = local.endpoint_name
  location     = local.region
}

# Upload model files to the bucket - in case the user wants to use an uploaded model
resource "google_storage_bucket_object" "upload_model" {
  for_each = fileset(var.model_src_dir, "**/*")

  source = "${path.module}/${var.model_src_dir}/${each.value}"
  bucket = local.ddos_bucket
  name   = "${var.model_dst_dir}/${each.key}"
}
