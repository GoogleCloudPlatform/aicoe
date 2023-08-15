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

# Un-deploy models from endpoints and delete all endpoints
for e in $(gcloud ai endpoints list --project $PROJECT_ID --region $REGION --format json | jq -r '.[].name' | cut -d'/' -f6); do \
    echo "Endpoint: $e"
    for m in $(gcloud ai endpoints describe $e --project $PROJECT_ID --region $REGION --format json | jq -r '.deployedModels[].id'); do \
        echo "Undeploy model: $e"
        gcloud ai endpoints undeploy-model $e --project $PROJECT_ID --region $REGION --deployed-model-id $m; \
    done; \
    yes | gcloud ai endpoints delete $e --project $PROJECT_ID --region $REGION;
done

# Delete all models
for i in $(gcloud ai models list --project $PROJECT_ID --region $REGION --format json | jq -r '.[].name' | cut -d'/' -f6); do 
    echo "Delete model: $i"
    gcloud ai models delete $i --project $PROJECT_ID --region $REGION; 
done
