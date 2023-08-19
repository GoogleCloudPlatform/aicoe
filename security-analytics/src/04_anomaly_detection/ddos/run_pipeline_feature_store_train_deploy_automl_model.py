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

import pipeline_run_feature_store_train_deploy_automl_model

with open("../generated/ddos_settings.json", 'r') as fd:
    ddos_settings = json.loads(fd.read())

aip.init(
    project=ddos_settings['PROJECT_ID'],
    staging_bucket=ddos_settings['BUCKET_URI']
    )

compiler.Compiler().compile(
    pipeline_func=pipeline_run_feature_store_train_deploy_automl_model.pipeline,
    package_path="../generated/ddos-feature-store-train-deploy-automl-model.json"
    )

job = aip.PipelineJob(
    display_name=f"s04-ddos-feature-store-train-deploy-automl-model-{str(uuid.uuid1())}",
    template_path="../generated/ddos-feature-store-train-deploy-automl-model.json",
    pipeline_root=ddos_settings['PIPELINE_ROOT'],
    enable_caching=False,
    parameter_values={
            'PROJECT_ID': ddos_settings['PROJECT_ID'],
            'REGION': ddos_settings['REGION'],
            'SUBNETWORK_SELF_LINK': ddos_settings['SUBNETWORK_SELF_LINK'],
            'SERVICE_ACCOUNT': ddos_settings['SERVICE_ACCOUNT'],
            'ENDPOINT_ARTIFACT_URI': ddos_settings['ENDPOINT_ARTIFACT_URI'],
            'ENDPOINT_ID': ddos_settings['ENDPOINT_ID'],
            'DATA_SOURCE_TABLE_URI': ddos_settings['RUN_AUTOML_TRAINING_TASK_PARAMS']['DATA_SOURCE_TABLE_URI'],
            'TRAINED_MODEL_NAME': ddos_settings['RUN_AUTOML_TRAINING_TASK_PARAMS']['TRAINED_MODEL_NAME'],
            'RUN_FEATURE_STORE_TASK_PARAMS': ddos_settings['RUN_FEATURE_STORE_TASK_PARAMS'],
            'RUN_AUTOML_TRAINING_TASK_PARAMS': ddos_settings['RUN_AUTOML_TRAINING_TASK_PARAMS'],
            'statsexamplegen_root_dir': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/statsexamplegen",
            'transformop_root_dir': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/transformop",
            'stage1tuner_root_dir': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/stage1tuner",
            'cvtrainer_root_dir': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/cvtrainer",
            'ensemble_root_dir': f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/ensemble"
        }
    )

job.run(service_account=ddos_settings['SERVICE_ACCOUNT'])
