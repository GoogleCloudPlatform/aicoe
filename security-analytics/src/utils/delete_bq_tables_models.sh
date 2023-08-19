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

echo "Delete table $PROJECT_ID:batching_$RANDOM_SUFFIX.containersec_before_fs"
bq --headless --project_id $PROJECT_ID rm -f "batching_$RANDOM_SUFFIX.containersec_before_fs"

echo "Delete table $PROJECT_ID:batching_$RANDOM_SUFFIX.containersec"
bq --headless --project_id $PROJECT_ID rm -f "batching_$RANDOM_SUFFIX.containersec"

echo "Delete table $PROJECT_ID:batching_$RANDOM_SUFFIX.ddos"
bq --headless --project_id $PROJECT_ID rm -f "batching_$RANDOM_SUFFIX.ddos"

echo "Delete model $PROJECT_ID:batching_$RANDOM_SUFFIX.containersec_model_$RANDOM_SUFFIX"
bq --headless --project_id $PROJECT_ID rm -f -m "batching_$RANDOM_SUFFIX.containersec_model_$RANDOM_SUFFIX"

echo "Delete table $PROJECT_ID:stg_modeling_$RANDOM_SUFFIX.containersec_served_fs"
bq --headless --project_id $PROJECT_ID rm -f "stg_modeling_$RANDOM_SUFFIX.containersec_served_fs"

echo "Delete table $PROJECT_ID:stg_modeling_$RANDOM_SUFFIX.ddos_served_fs"
bq --headless --project_id $PROJECT_ID rm -f "stg_modeling_$RANDOM_SUFFIX.ddos_served_fs"

for tableId in $(bq --headless --project_id $PROJECT_ID --format json ls "inferenced_$RANDOM_SUFFIX" 2>/dev/null | jq -r '.[] | [.tableReference.tableId] | @tsv')
do
    echo "Delete $PROJECT_ID:inferenced_$RANDOM_SUFFIX.$tableId"
    bq --headless --project_id $PROJECT_ID rm -f "inferenced_$RANDOM_SUFFIX.$tableId"
done

echo "Truncate table $PROJECT_ID:streaming_$RANDOM_SUFFIX.containersec_streaming_$RANDOM_SUFFIX"
bq --headless --project_id $PROJECT_ID query --use_legacy_sql=false "TRUNCATE TABLE \`$PROJECT_ID.streaming_$RANDOM_SUFFIX.containersec_streaming_$RANDOM_SUFFIX\`"

echo "Truncate table $PROJECT_ID:streaming_$RANDOM_SUFFIX.ddos_streaming"
bq --headless --project_id $PROJECT_ID query --use_legacy_sql=false "TRUNCATE TABLE \`$PROJECT_ID.streaming_$RANDOM_SUFFIX.ddos_streaming\`"

echo "Truncate table $PROJECT_ID:streaming_$RANDOM_SUFFIX.syn_streaming"
bq --headless --project_id $PROJECT_ID query --use_legacy_sql=false "TRUNCATE TABLE \`$PROJECT_ID.streaming_$RANDOM_SUFFIX.syn_streaming\`"
