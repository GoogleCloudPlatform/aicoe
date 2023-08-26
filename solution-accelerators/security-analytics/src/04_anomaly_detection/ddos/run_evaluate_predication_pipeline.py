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
 
 
import random
import string
import json
from google.cloud import storage
import google.cloud.aiplatform as aip
import kfp
from kfp.v2.dsl import Input, component, Artifact, Output
from kfp.v2 import compiler 
from typing import NamedTuple
import uuid

import pipeline_evaluate_do_online_prediction

with open("../generated/ddos_settings.json", 'r') as fd:
    ddos_settings = json.loads(fd.read())

aip.init(
    project=ddos_settings['PROJECT_ID'],
    staging_bucket=ddos_settings['BUCKET_URI']
    )

compiler.Compiler().compile(
    pipeline_func=pipeline_evaluate_do_online_prediction.pipeline,
    package_path="../generated/ddos-evaluate-do-online-prediction.json"
    )

job = aip.PipelineJob(
    display_name=f"s04-ddos-evaluate-do-online-prediction-{str(uuid.uuid1())}",
    template_path="../generated/ddos-evaluate-do-online-prediction.json",
    pipeline_root=ddos_settings['PIPELINE_ROOT'],
    enable_caching=False,
    parameter_values={
            'REGION': ddos_settings['REGION'],
            'PROJECT_ID': ddos_settings['PROJECT_ID'],
            'PREDICTION_DATASET': ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['PREDICTION_DATASET'],
            'PREDICTION_TABLE': ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['PREDICTION_TABLE'],
            'INCIDENT_TOPIC_NAME': ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['INCIDENT_TOPIC_NAME'],
            'SOURCE_DATASET': ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['SOURCE_DATASET'],
            'SOURCE_TABLE': ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['SOURCE_TABLE'],
            'BUCKET_URI': ddos_settings['BUCKET_URI'],
            'BUCKET_NAME': ddos_settings['BUCKET_NAME'],
            'ENDPOINT_ID': ddos_settings['ENDPOINT_ID'],
            'MODEL_NAME_PREFIX': ddos_settings['MODEL_NAME'],
            'OUTPUT_PREDICTION_DATASET': ddos_settings['RUN_AUTOML_TRAINING_TASK_PARAMS']['OUTPUT_PREDICTION_DATASET'],
            'SERVICE_ACCOUNT': ddos_settings['SERVICE_ACCOUNT'],
            'SUBNETWORK_SELF_LINK': ddos_settings['SUBNETWORK_SELF_LINK'],
            'AI_API_ENDPOINT': ddos_settings['AI_API_ENDPOINT'],
            'ROOT_DIR': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline",
            'SOURCE_INPUT_URI': f"bq://{ddos_settings['PROJECT_ID']}.{ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['SOURCE_DATASET']}.{ddos_settings['DO_ONLINE_PREDICTION_PARAMS']['SOURCE_TABLE']}",
            'DESTINATION_OUTPUT_URI': f"bq://{ddos_settings['PROJECT_ID']}.{ddos_settings['RUN_AUTOML_TRAINING_TASK_PARAMS']['OUTPUT_PREDICTION_DATASET']}",
            'EVALUATION_ROOT_DIR': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/modelevaluation"
        }
    )

job.run(service_account=ddos_settings['SERVICE_ACCOUNT'])
