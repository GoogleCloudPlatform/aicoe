#!/bin/bash

# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

source "$(dirname "$0")/load_environment_sh.sh"

if [ "x$1" == "xYES" ]; then
  for i in 00_bootstrap 01_realtime_ingestion 02_enrichment_dataflow 03_feature_store 04_anomaly_detection 05_bqml 06_visualization; do
    echo "$UTILS_DIR/../$i/.terraform"
    rm -rf "$UTILS_DIR/../$i/.terraform"
    echo "$UTILS_DIR/../$i/.terraform.lock.hcl"
    rm -rf "$UTILS_DIR/../$i/.terraform.lock.hcl"
  done
  echo "$UTILS_DIR/../00_bootstrap/backend.tf"
  rm -rf "$UTILS_DIR/../00_bootstrap/backend.tf"
  echo "$UTILS_DIR/../00_bootstrap/terraform.tfvars"
  rm -rf "$UTILS_DIR/../00_bootstrap/terraform.tfvars"
  echo "$UTILS_DIR/../04_anomaly_detection/terraform.tfvars"
  rm -rf "$UTILS_DIR/../04_anomaly_detection/terraform.tfvars"
else
  echo "This scripts deletes all terraform states stored locally (.terraform, .terraform.lock.hcl). Execute with YES as the first parameter to proceed."
fi
