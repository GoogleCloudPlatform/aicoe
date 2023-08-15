"""
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
 """


import json
import kfp
import google.cloud.aiplatform as aip

from google.cloud import storage
from kfp.v2 import compiler  # noqa: F811
from kfp.v2.dsl import Input, Metrics, component, Artifact, Output
from uuid import uuid1

import pipeline_train_detect_publish

UUID = str(uuid1())

with open("../generated/containersec_settings.json") as config:
    containersec_settings = json.load(config)

aip.init(project=containersec_settings['PROJECT_ID'], staging_bucket=containersec_settings['BUCKET_URI'])

compiler.Compiler().compile(
    pipeline_func=pipeline_train_detect_publish.pipeline,
    package_path="../generated/tabular_regression_pipeline.json",
)

job_configuration_query = {
                "destination_table": {
                    "project_id": containersec_settings['PROJECT_ID'],
                    "dataset_id": containersec_settings['PIPELINE_LAUNCH_PARAMS']['ANOMALY_DATASET'],
                    "table_id": containersec_settings['PIPELINE_LAUNCH_PARAMS']['ANOMALY_TABLE'],
                }
            }

job = aip.PipelineJob(
    display_name=f"s05-containersec-train-detect-anomalies-{UUID}",
    template_path="../generated/tabular_regression_pipeline.json",
    pipeline_root=f"{containersec_settings['BUCKET_URI']}/pipeline_root/containersec_dataset",
    enable_caching=False,
    parameter_values={
        "publish_anomalies_to_pubsub_params": containersec_settings['PUBLISH_ANOMALIES_TO_PUBSUB_PARAMS'],
        "run_feature_store_task_params": containersec_settings['RUN_FEATURE_STORE_TASK'],
        "pipeline_launch_params": containersec_settings['PIPELINE_LAUNCH_PARAMS'],
        "create_model_query": containersec_settings['PIPELINE_LAUNCH_PARAMS']['CREATE_MODEL_QUERY'].format(
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['MODEL_TARGET_DATASET'],
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['MODEL_TARGET_NAME'],
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['PROJECT_ID'],
            # containersec_settings['PIPELINE_LAUNCH_PARAMS']['MODEL_SOURCE_DATASET'],
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['MODEL_TARGET_DATASET'],
            # containersec_settings['PIPELINE_LAUNCH_PARAMS']['MODEL_SOURCE_TABLE']
            containersec_settings['RUN_FEATURE_STORE_TASK']['TEMP_SRC_TABLE'],
        ),
        "detect_anomalies_query": containersec_settings['PIPELINE_LAUNCH_PARAMS']['GET_DETECT_ANOMALY_DATA'].format(
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['SRC_STREAMING_DATASET'],
            containersec_settings['PIPELINE_LAUNCH_PARAMS']['SRC_STREAMING_TABLE']
        ),
        "project_id": containersec_settings['PROJECT_ID'],
        "job_configuration_query": job_configuration_query,
        "bq_location": containersec_settings['PIPELINE_LAUNCH_PARAMS']['LOCATION'],
        "anomaly_table_id": f"{containersec_settings['PROJECT_ID']}.{containersec_settings['PIPELINE_LAUNCH_PARAMS']['ANOMALY_DATASET']}.{containersec_settings['PIPELINE_LAUNCH_PARAMS']['ANOMALY_TABLE']}"
    },
)

job.run(service_account=containersec_settings['SERVICE_ACCOUNT'])
