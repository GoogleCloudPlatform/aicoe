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
variable "topics" {
  type = list(string)
}

variable "notification_email_addresses" {
  type = list(string)
}

variable "notification_threshold" {
  type = string
}

variable "model_src_dir" {
  description = "Directory containing model files to upload (relative to the module)"
  type        = string
}

variable "model_dst_dir" {
  description = "Directory (within ddos bucket) to upload model to"
  type        = string
}
