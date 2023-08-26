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

variable "datasets" {
  type = list(string)
}
variable "df_roles" {
  type = list(string)
}

variable "custom_firewall_rules_direction" {
  default = "INGRESS"
}
variable "custom_firewall_rules_ranges" {
  default = ["35.235.240.0/20"]
}
variable "custom_firewall_rules_allow_protocol" {
  default = "TCP"
}
variable "custom_firewall_rules_allow_ports" {
  default = [22, 3389]
}
variable "custom_firewall_rules_log_config_metadata" {
  default = "INCLUDE_ALL_METADATA"
}
variable "topics" {
  type = list(string)
}
