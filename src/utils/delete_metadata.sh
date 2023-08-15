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

# Delete all metadata artifacts
TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/artifacts | jq -r '.artifacts[].name'`;
while [[ ! -z $TEMP_VAR ]]; do
    for i in $(curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/artifacts | jq -r '.artifacts[].name'); do \
        echo "Delete: $i"
        curl -X DELETE -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/$i; \
    done;
    TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/artifacts | jq -r '.artifacts[].name'`;
done;

# Delete all metadata contexts
TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/contexts | jq -r '.contexts[].name'`;
while [[ ! -z $TEMP_VAR ]]; do
    for i in $(curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/contexts | jq -r '.contexts[].name'); do \
        echo "Delete: $i"
        curl -X DELETE -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/$i; \
    done;
    TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/contexts | jq -r '.contexts[].name'`;
done

# Delete all metadata executions
TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/executions | jq -r '.executions[].name'`; \
while [[ ! -z $TEMP_VAR ]]; do \
    for i in $(curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/executions | jq -r '.executions[].name'); do \
        echo "Delete: $i"
        curl -X DELETE -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/$i; \
    done; \
    TEMP_VAR=`curl -X GET -H"Authorization: Bearer $TOKEN" https://$REGION-aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/metadataStores/default/executions | jq -r '.executions[].name'`; \
done
