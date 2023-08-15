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

resource "google_storage_bucket_object" "ddos_eval_dag_pipeline_util_object" {
  name   = "eval_dag_pipeline_util.py"
  source = "ddos/eval_dag_pipeline_util.py"
  bucket = local.ddos_bucket
}

resource "google_storage_bucket_object" "ddos_eval_dag_ddos_object" {
  name   = "dags/eval_dag_ddos.py"
  source = "ddos/eval_dag_ddos.py"
  bucket = local.composer_bucket
}

resource "google_storage_bucket_object" "ddos_setup_object" {
  name   = "dags/setup.py"
  source = "ddos/setup.py"
  bucket = local.composer_bucket
}

resource "google_storage_bucket_object" "eval_ddos_settings_object" {
  depends_on = [local_file.generated["eval_ddos_settings.json"]]

  name   = "eval_ddos_settings.json"
  source = "generated/eval_ddos_settings.json"
  bucket = local.ddos_bucket
}
