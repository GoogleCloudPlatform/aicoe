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

set -u

CUSTOM_STATE_BUCKET="${STATE_BUCKET:-}"

case "$#" in
  0)
    echo "Launched without parameters: using project settings from Google Cloud CLI and region us-central1 / zone us-central1-a"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null || true)
    REGION="us-central1"
    ZONE="us-central1-a"
    ;;
  1)
    PROJECT_ID="$1"
    REGION="us-central1"
    ZONE="us-central1-a"
    ;;
  2)
    PROJECT_ID="$1"
    REGION="$2"
    ZONE="${REGION}-a"
    ;;
  3)
    PROJECT_ID="$1"
    REGION="$2"
    ZONE="$3"
    ;;
  4)
    PROJECT_ID="$1"
    REGION="$2"
    ZONE="$3"
    CUSTOM_STATE_BUCKET="$4"
    ;;
  *)
    echo "Usage: $0 [<PROJECT_ID> [<REGION> [<ZONE> [<STATE_BUCKET>]]]]" >&2
    exit 1
    ;;
esac

case "${PROJECT_ID}" in
  ''|'(unset)'|*[!a-z0-9.:-]*)
    echo "Status: Failed. Reason: Invalid or empty PROJECT_ID '${PROJECT_ID}'" >&2
    exit 1
    ;;
esac

case "${REGION}" in
  ''|*[!a-z0-9-]*)
    echo "Status: Failed. Reason: Invalid REGION '${REGION}'" >&2
    exit 1
    ;;
esac

case "${ZONE}" in
  ''|*[!a-z0-9-]*)
    echo "Status: Failed. Reason: Invalid ZONE '${ZONE}'" >&2
    exit 1
    ;;
esac

if [ -n "${CUSTOM_STATE_BUCKET}" ]; then
  STATE_BUCKET="${CUSTOM_STATE_BUCKET}"
else
  STATE_BUCKET="tf-state-${PROJECT_ID}"
fi

BUCKET_LEN=${#STATE_BUCKET}
if [ "${BUCKET_LEN}" -lt 3 ] || [ "${BUCKET_LEN}" -gt 63 ]; then
  echo "Status: Failed. Reason: Invalid STATE_BUCKET length '${STATE_BUCKET}'" >&2
  exit 1
fi
case "${STATE_BUCKET}" in
  *[!a-z0-9._-]*|[!a-z0-9]*|*[!a-z0-9])
    echo "Status: Failed. Reason: Invalid characters in STATE_BUCKET '${STATE_BUCKET}'" >&2
    exit 1
    ;;
esac

STATE_BUCKET_URL="gs://${STATE_BUCKET}"

echo "Using project ${PROJECT_ID} and creating resources in region ${REGION} / zone ${ZONE}."
echo "Execute ./setup.sh <PROJECT_ID> <REGION> [<ZONE> [<STATE_BUCKET>]] to override."
echo "Press ENTER to continue!"
read -r _ || true

echo "Initializing using project ${PROJECT_ID} and state bucket ${STATE_BUCKET_URL} in region ${REGION}"
printf "Checking permissions ... "

EXPECTED_PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)" 2>/dev/null || true)
case "${EXPECTED_PROJECT_NUMBER}" in
  ''|*[!0-9]*)
    echo "Status: Failed. Reason: Failed to describe project ${PROJECT_ID}" >&2
    exit 1
    ;;
esac
echo "Status: OK"

get_bucket_owner_project_number() {
  gcloud storage buckets describe "$1" --raw --format="value(projectNumber)" 2>/dev/null
}

printf "Checking terraform state bucket ... "
if ACTUAL_PROJECT_NUMBER=$(get_bucket_owner_project_number "${STATE_BUCKET_URL}"); then
  case "${ACTUAL_PROJECT_NUMBER}" in
    ''|*[!0-9]*)
      echo "Status: Failed. Reason: Could not determine owning projectNumber for ${STATE_BUCKET_URL}" >&2
      exit 1
      ;;
  esac
  if [ "${ACTUAL_PROJECT_NUMBER}" != "${EXPECTED_PROJECT_NUMBER}" ]; then
    echo "Status: Failed. Reason: Bucket ${STATE_BUCKET_URL} is not owned by project ${PROJECT_ID} (expected projectNumber ${EXPECTED_PROJECT_NUMBER}, got ${ACTUAL_PROJECT_NUMBER}). Specify a project-owned bucket via STATE_BUCKET=<bucket-name>." >&2
    exit 1
  fi
  echo "Status: OK"
else
  if ! gcloud storage buckets create "${STATE_BUCKET_URL}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access \
    --public-access-prevention >/dev/null 2>&1; then
    echo "Status: Failed. Reason: Failed to create or verify ownership of ${STATE_BUCKET_URL} in project ${PROJECT_ID} (bucket name may already be taken globally or permissions are insufficient)." >&2
    exit 1
  fi

  if ! gcloud storage buckets update "${STATE_BUCKET_URL}" --versioning >/dev/null 2>&1; then
    echo "Status: Failed. Reason: Created ${STATE_BUCKET_URL}, but failed to enable object versioning." >&2
    exit 1
  fi

  ACTUAL_PROJECT_NUMBER=$(get_bucket_owner_project_number "${STATE_BUCKET_URL}" || true)
  if [ "${ACTUAL_PROJECT_NUMBER}" != "${EXPECTED_PROJECT_NUMBER}" ]; then
    echo "Status: Failed. Reason: Post-creation ownership check failed for ${STATE_BUCKET_URL}." >&2
    exit 1
  fi
  echo "Status: Created"
fi

printf "Creating backend configuration: backend.tf: "
if [ ! -f backend.tf ]; then
  cat >backend.tf <<EOF
terraform {
  backend "gcs" {
    bucket = "${STATE_BUCKET}"
    prefix = "terraform/bootstrap/state"
  }
}
EOF
  echo "OK"
else
  EXISTING_BUCKET=$(sed -n 's/^[[:space:]]*bucket[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' backend.tf | head -n 1)
  if [ "${EXISTING_BUCKET}" != "${STATE_BUCKET}" ]; then
    echo "Status: Failed. Reason: Existing backend.tf references bucket '${EXISTING_BUCKET}', expected '${STATE_BUCKET}'. Remove backend.tf or pass matching STATE_BUCKET." >&2
    exit 1
  fi
  echo "Status: Skipped. Reason: Already exists"
fi

printf "Creating terraform configuration: terraform.tfvars: "
if [ ! -f terraform.tfvars ]; then
  cat >terraform.tfvars <<EOF
project_id = "${PROJECT_ID}"
state_bucket = "${STATE_BUCKET}"
region = "${REGION}"
zone = "${ZONE}"
EOF
  echo "OK"
else
  EXISTING_TFVARS_PROJECT=$(sed -n 's/^[[:space:]]*project_id[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars | head -n 1)
  EXISTING_TFVARS_BUCKET=$(sed -n 's/^[[:space:]]*state_bucket[[:space:]]*=[[:space:]]*"\([^"]*\)".*/\1/p' terraform.tfvars | head -n 1)
  if [ "${EXISTING_TFVARS_PROJECT}" != "${PROJECT_ID}" ] || [ "${EXISTING_TFVARS_BUCKET}" != "${STATE_BUCKET}" ]; then
    echo "Status: Failed. Reason: Existing terraform.tfvars (project_id='${EXISTING_TFVARS_PROJECT}', state_bucket='${EXISTING_TFVARS_BUCKET}') does not match expected project '${PROJECT_ID}' and bucket '${STATE_BUCKET}'." >&2
    exit 1
  fi
  echo "Status: Skipped. Reason: Already exists"
fi

printf "\nCurrent configuration - backend.tf\n"
cat backend.tf

printf "\nCurrent configuration: terraform.tfvars\n"
cat terraform.tfvars
