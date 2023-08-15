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

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}
variable "region" {
  description = "Default GCP Region"
  type        = string
}
variable "zone" {
  description = "Default GCP Zone"
  type        = string
}
variable "state_bucket" {
  description = "TF State Bucket"
  type        = string
}
variable "apis_list" {
  description = "List of APIs to be enabled"
  type        = list(string)
  default = [
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "composer.googleapis.com",
    "compute.googleapis.com",
    "datacatalog.googleapis.com",
    "dataflow.googleapis.com",
    "datastream.googleapis.com",
    "iam.googleapis.com",
    "sourcerepo.googleapis.com",
  ]
}
variable "labels_map" {
  description = "Key value pairs in a map for labels"
  type        = map(string)
  default = {
    env     = "gcp_workshop"
    project = "security_analytics"
  }
}
