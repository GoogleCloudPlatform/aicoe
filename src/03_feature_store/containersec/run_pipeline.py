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
import google.cloud.aiplatform as aip

from uuid import uuid4
from kfp.v2 import compiler 

from pipeline import pipeline


UUID = str(uuid4())


with open("../generated/containersec_settings.json") as config:
    containersec_settings = json.load(config)

PIPELINE_ROOT = f"{containersec_settings['BUCKET_URI']}/pipeline_root/containersec_dataset"
PIPELINE_DISPLAY_NAME = f"s03-containersec_run_feature_store-{UUID}"

aip.init(project=containersec_settings['PROJECT_ID'], staging_bucket=containersec_settings['BUCKET_URI'])

compiler.Compiler().compile(
    pipeline_func=pipeline,
    package_path="../generated/containersec-tabular_regression_pipeline.json",
)

job = aip.PipelineJob(
    display_name=PIPELINE_DISPLAY_NAME,
    template_path="../generated/containersec-tabular_regression_pipeline.json",
    pipeline_root=PIPELINE_ROOT,
    enable_caching=False,
    parameter_values={
        'run_feature_store_task_params': containersec_settings['RUN_FEATURE_STORE_TASK']
    }
)

job.run(service_account=containersec_settings['SERVICE_ACCOUNT'])
