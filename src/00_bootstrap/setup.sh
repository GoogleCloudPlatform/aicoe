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

# Get project name from arguments
if [ $# -eq 0 ]; then
  echo "Launched without parameters: using project settings from Google Cloud CLI and region us-central1 / zone us-central1-a"
  PROJECT_ID=$(gcloud config get-value project)
  REGION=us-central1
  ZONE=us-central1-a
fi

# Get project name from arguments
if [ $# -eq 1 ]; then
  PROJECT_ID=$1
  REGION=us-central1
  ZONE=us-central1-a
fi

# Get project name and region from arguments
if [ $# -eq 2 ]; then
  PROJECT_ID=$1
  REGION=$2
  ZONE="${REGION}-a"
fi

# Get project name region and zone from arguments
if [ $# -eq 3 ]; then
  PROJECT_ID=$1
  REGION=$2
  ZONE=$3
fi

STATE_BUCKET="tf-state-${PROJECT_ID}"
STATE_BUCKET_URL="gs://${STATE_BUCKET}"

echo "Using project $PROJECT_ID and creating resources in region $REGION / zone $ZONE."
echo "Execute ./setup.sh <PROJECT_ID> <REGION> to override."
echo "Press ENTER to continue!"
read

echo "Initializing using project ${PROJECT_ID} and state bucket ${STATE_BUCKET_URL} in region $REGION"
echo -n "Checking permissions ... "

gcloud projects describe ${PROJECT_ID} 2>&1 >/dev/null
if [ $? -gt 0 ]; then
  echo "Status: Failed. Reason: Failed to describe project"
  exit
else
  echo "Status: OK"
fi

echo -n "Checking terraform state bucket ... "
gsutil ls $STATE_BUCKET_URL 2>&1 >/dev/null
if [ $? -gt 0 ]; then
  gsutil mb -p $PROJECT_ID -l $REGION $STATE_BUCKET_URL 2>&1 >/dev/null
  if [ $? -gt 0 ]; then
    echo "Status: Failed. Reason: Failed to create bucket"
  else
    echo "Status: Created"
  fi
else
  echo "Status: OK"
fi

echo -n "Creating backend configuration: backend.tf: "
if [ ! -f backend.tf ]; then
  echo "terraform {" >backend.tf
  echo "  backend \"gcs\" {" >>backend.tf
  echo "    bucket = \"${STATE_BUCKET}\"" >>backend.tf
  echo "    prefix = \"terraform/bootstrap/state\"" >>backend.tf
  echo "  }" >>backend.tf
  echo "}" >>backend.tf
  echo "OK"
else
  echo "Status: Skipped. Reason: Already exists"
fi

echo -n "Creating terraform configuration: terraform.tfvars: "
if [ ! -f terraform.tfvars ]; then
  echo "project_id = \"$PROJECT_ID\"" >terraform.tfvars
  echo "state_bucket = \"$STATE_BUCKET\"" >>terraform.tfvars
  echo "region = \"$REGION\"" >>terraform.tfvars
  echo "zone = \"$ZONE\"" >>terraform.tfvars
  echo "OK"
else
  echo "Status: Skipped. Reason: Already exists"
fi

echo -e "\nCurrent configuration - backend.tf"
cat backend.tf

echo -e "\nCurrent configuration: terraform.tfvars"
cat terraform.tfvars
