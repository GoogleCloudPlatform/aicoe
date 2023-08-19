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

UTILS_DIR=$(dirname "$0")

if [ -f "$UTILS_DIR/../00_bootstrap/generated/environment.sh" ]
then
    source $UTILS_DIR/../00_bootstrap/generated/environment.sh
fi
if [ -f "$UTILS_DIR/../01_realtime_ingestion/generated/environment.sh" ]
then
    source $UTILS_DIR/../01_realtime_ingestion/generated/environment.sh
fi
if [ -f "$UTILS_DIR/../02_enrichment_dataflow/generated/environment.sh" ]
then
    source $UTILS_DIR/../02_enrichment_dataflow/generated/environment.sh
fi
if [ -f "$UTILS_DIR/../03_feature_store/generated/environment.sh" ]
then
    source $UTILS_DIR/../03_feature_store/generated/environment.sh
fi
if [ -f "$UTILS_DIR/../04_anomaly_detection/generated/environment.sh" ]
then
    source $UTILS_DIR/../04_anomaly_detection/generated/environment.sh
fi
TOKEN=$(gcloud auth print-access-token)

echo "PROJECT_ID=$PROJECT_ID"
echo "REGION=$REGION"
echo "RANDOM_SUFFIX=$RANDOM_SUFFIX"
echo "SUBNETWORK_ID=$SUBNETWORK_ID"
echo "DDOS_BUCKET=$DDOS_BUCKET"
echo "CONTAINERSEC_BUCKET=$CONTAINERSEC_BUCKET"
echo "SERVICE_ACCOUNT_EMAIL=$SERVICE_ACCOUNT_EMAIL"
echo "DDOS_INCIDENT_TOPIC=$DDOS_INCIDENT_TOPIC"
echo "COMPOSER_DAG_PATH=$COMPOSER_DAG_PATH"
