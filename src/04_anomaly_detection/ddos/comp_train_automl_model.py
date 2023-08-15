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

from kfp.v2.dsl import Input, component, Artifact, Output, Model
from typing import NamedTuple
import collections

import pipeline_run_feature_store_train_deploy_automl_model
import comp_feature_store
import comp_train_automl_model

@component(
    base_image="python:3.8"
)
def resolve_params(ddos_settings: dict, training_task_params: dict) -> NamedTuple("Outputs", [
    ("DDOS_SETTINGS", dict),
    ("TRAINING_TASK_PARAMS", dict),
    ("PROJECT_ID", str),
    ("REGION", str),
    ("DATA_SOURCE_TABLE_URI", str),
    ("SUBNETWORK_SELF_LINK", str),
    ("SERVICE_ACCOUNT", str),
    ("BUCKET_URI", str),
    ("TRAINED_MODEL_NAME", str),
    ("statsexamplegen_root_dir", str),
    ("transformop_root_dir", str),
    ("stage1tuner_root_dir", str),
    ("cvtrainer_root_dir", str),
    ("ensemble_root_dir", str)
    ]):
    import collections

    output = None
    Outputs = collections.namedtuple('Outputs', 
                                     [
                                        'DDOS_SETTINGS',
                                        'TRAINING_TASK_PARAMS',
                                        'PROJECT_ID',
                                        'REGION',
                                        'DATA_SOURCE_TABLE_URI',
                                        'SUBNETWORK_SELF_LINK',
                                        'SERVICE_ACCOUNT',
                                        'BUCKET_URI',
                                        'TRAINED_MODEL_NAME',
                                        'statsexamplegen_root_dir',
                                        'transformop_root_dir',
                                        'stage1tuner_root_dir',
                                        'cvtrainer_root_dir',
                                        'ensemble_root_dir'
                                        ])
    output = Outputs(
        ddos_settings, 
        training_task_params,
        ddos_settings['PROJECT_ID'],
        ddos_settings['REGION'],
        training_task_params['DATA_SOURCE_TABLE_URI'],
        ddos_settings['SUBNETWORK_SELF_LINK'],
        ddos_settings['SERVICE_ACCOUNT'],
        ddos_settings['BUCKET_URI'],
        training_task_params['TRAINED_MODEL_NAME'],
        f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/statsexamplegen",
        f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/transformop",
        f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/stage1tuner",
        f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/cvtrainer",
        f"gs://{ddos_settings['BUCKET_NAME']}/automl_tabular_pipeline/ensemble"
        )
    print(f"resolve_params {ddos_settings=} {training_task_params=} {output=}")
    return output

@component(
    packages_to_install=["pandas", "google-cloud-bigquery", "scikit-learn", "numpy", 
                            "google-cloud-aiplatform==1.18.2", "pyarrow", 
                            "google-cloud-pipeline-components==1.0.28"],
    
    base_image="python:3.8",
)
def train_automl_model_init(run_automl_training_task_params: dict) -> NamedTuple("Outputs", [
    ("transform_config_path", str)]):
    import os
    import json
    import uuid
    from google.auth.compute_engine import Credentials
    import json
    import traceback
    from typing import Any, Dict, List
    from google.cloud import aiplatform, storage, bigquery
    import collections

    # By extracting variables at an early stage we fail fast in case of a missing key
    PROJECT_ID=run_automl_training_task_params['PROJECT_ID']
    SERVICE_ACCOUNT=run_automl_training_task_params['SERVICE_ACCOUNT']
    BUCKET_NAME=run_automl_training_task_params['BUCKET_NAME']
    DATA_SOURCE_DATASET=run_automl_training_task_params['DATA_SOURCE_DATASET']
    DATA_SOURCE_TABLE=run_automl_training_task_params['DATA_SOURCE_TABLE']

    def get_bucket_name_and_path(uri):
        no_prefix_uri = uri[len("gs://") :]
        splits = no_prefix_uri.split("/")
        return splits[0], "/".join(splits[1:])


    def write_to_gcs(project_id: str, uri: str, content: str, creds: Credentials):
        bucket_name, path = get_bucket_name_and_path(uri)
        storage_client = storage.Client(project=project_id, credentials=creds)
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(path)
        blob.upload_from_string(content)


    def generate_auto_transformation(column_names: List[str]) -> List[Dict[str, Any]]:
        transformations = []
        for column_name in column_names:
            transformations.append({"auto": {"column_name": column_name}})
        return transformations

    src_table_obj = bigquery.Client(project=PROJECT_ID).get_table('{}.{}.{}'.format(PROJECT_ID, DATA_SOURCE_DATASET, DATA_SOURCE_TABLE))
    features_for_ml = []
    features_for_ml.extend([s.name for s in src_table_obj.schema])
    features = features_for_ml[:-1]

    transformations = generate_auto_transformation(features)
    transform_config_path = f"gs://{BUCKET_NAME}/automl_tabular_pipeline/transform_config_{str(uuid.uuid1())}.json"
    creds = Credentials(SERVICE_ACCOUNT, PROJECT_ID, scopes='https://www.googleapis.com/auth/cloud-platform')
    write_to_gcs(PROJECT_ID, transform_config_path, json.dumps(transformations), creds)
    output = None
    Outputs = collections.namedtuple('Outputs', ['transform_config_path'])
    output = Outputs(transform_config_path)

    return output

@component(
    packages_to_install=["pandas", "google-cloud-bigquery", "scikit-learn", "numpy", 
                            "google-cloud-aiplatform==1.18.2", "pyarrow", 
                            "google-cloud-pipeline-components==1.0.28"],
    
    base_image="python:3.8",
)
def train_automl_model_gen_output(model_input: Input[Artifact], downsampled_test_split_json: list, test_split_json: list, model: Output[Artifact]) -> NamedTuple("Outputs", [
    ("downsampled_test_split_json", str), ("test_split_json", str)
]):
    import json
    import collections

    print(f'train_automl_model_gen_output {model_input=}')
    output = None
    Outputs = collections.namedtuple('Outputs', ['downsampled_test_split_json', 'test_split_json'])
    output = Outputs(
        json.dumps(downsampled_test_split_json),
        json.dumps(test_split_json)
        )
    model.metadata['resourceName'] = model_input.metadata['resourceName']
    model.metadata['downsampled_test_split_json'] = json.dumps(downsampled_test_split_json)
    model.metadata['test_split_json'] = json.dumps(test_split_json)
    return output
