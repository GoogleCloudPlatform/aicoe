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

source ../generated/environment.sh

wait_for_operation() {
  _REGION=$1
  _OP_ID=$2
  echo "Waiting for operation $_OP_ID"
  _DONE=$(gcloud ai operations describe --region $_REGION --format 'table[no-heading](done)' $_OP_ID 2>/dev/null | tr -d '\n')
  echo "Waiting for operation $_OP_ID [Done: $_DONE]"
  while [ ! "x$_DONE" == "xTrue" ]; do
    _DONE=$(gcloud ai operations describe --region $_REGION --format 'table[no-heading](done)' $_OP_ID 2>/dev/null | tr -d '\n')
    echo "Waiting for operation $_OP_ID [Done: $_DONE]"
    sleep 10
  done
}

TMPFILE=$(mktemp)
echo -n "Creating model $UPLOADED_MODEL_NAME from ... ${MODEL_UPLOAD_LOCATION} "
CNT=$(gcloud ai models list --filter="displayName ~ ${UPLOADED_MODEL_NAME}" --sort-by "~createTime" --format "table[no-heading](displayName,name)" --project $PROJECT_ID --region $REGION 2>/dev/null | wc -l)
if [ $CNT -eq 0 ]; then
  echo "CREATING"
  curl \
    -H "Authorization: Bearer $(gcloud auth print-access-token)" \
    -X POST \
    -H "Content-Type: application/json" \
    https://${REGION}-aiplatform.googleapis.com/v1/projects/${PROJECT_ID}/locations/${REGION}/models:upload --data "@../generated/model_upload.json" 2>/dev/null | tee $TMPFILE
  echo "CREATED"
  OPERATION_ID=$(cat $TMPFILE | jq -r '.name | split("/")[-1]' | tr -d '\n')
  wait_for_operation $REGION $OPERATION_ID
else
  echo "ALREADY_EXISTS"
fi

MODEL_ID=$(gcloud ai models list --filter="displayName ~ ${UPLOADED_MODEL_NAME}" --format "table[no-heading,no-transforms](name)" --project $PROJECT_ID --region $REGION 2>/dev/null | head -n 1)
if [ "x$MODEL_ID" != "x" ]; then
  echo "Deploying model $UPLOADED_MODEL_NAME with id $MODEL_ID to endpoint $ENDPOINT_NAME ... "

  DEPLOYED_MODEL_ID=$(gcloud ai endpoints describe $ENDPOINT_NAME --project $PROJECT_ID --region $REGION --format 'table[no-heading](deployedModels[0].model)' 2>/dev/null)
  if [ "x$DEPLOYED_MODEL_ID" == "x$MODEL_ID" ]; then
    echo "ALREADY_DEPLOYED"
  else
    if [ ! "x$DEPLOYED_MODEL_ID" == "x" ]; then
      echo "DEPLOYING $MODEL_ID instead of $DEPLOYED_MODEL_ID"
    else
      echo "DEPLOYING $MODEL_ID"
    fi
    gcloud ai endpoints deploy-model \
      $ENDPOINT_ID \
      --project $PROJECT_ID \
      --model=$MODEL_ID \
      --machine-type n1-standard-16 \
      --min-replica-count 1 \
      --max-replica-count 1 \
      --traffic-split 0=100 \
      --display-name $UPLOADED_MODEL_NAME \
      --region $REGION
    echo "DEPLOYED"
    if [ ! "x$DEPLOYED_MODEL_ID" == "x" ]; then
      DEPLOYED_MODEL_ID_NUM=$(echo -n $DEPLOYED_MODEL_ID | awk '{print $6}')
      echo "UNDEPLOYING $DEPLOYED_MODEL_ID [ $DEPLOYED_MODEL_ID_NUM ]"
      gcloud ai endpoints undeploy-model \
        $ENDPOINT_ID \
        --region $REGION \
        --project $PROJECT_ID \
        --deployed-model-id $DEPLOYED_MODEL_ID_NUM
    fi
  fi
else
  echo "ERROR: can't find model $UPLOADED_MODEL_NAME"
fi
rm $TMPFILE
