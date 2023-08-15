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

import kfp
import uuid

@kfp.dsl.pipeline(name="s04-ddos-feature-store-train-deploy-automl-model-" + str(uuid.uuid1()))
def pipeline(
    PROJECT_ID: str,
    REGION: str,
    DATA_SOURCE_TABLE_URI: str,
    SUBNETWORK_SELF_LINK: str,
    SERVICE_ACCOUNT: str,
    TRAINED_MODEL_NAME: str,
    ENDPOINT_ARTIFACT_URI: str,
    ENDPOINT_ID: str,
    statsexamplegen_root_dir: str,
    transformop_root_dir: str,
    stage1tuner_root_dir: str,
    cvtrainer_root_dir: str,
    ensemble_root_dir: str,
    RUN_FEATURE_STORE_TASK_PARAMS: dict,
    RUN_AUTOML_TRAINING_TASK_PARAMS: dict
):
    from google.auth.compute_engine import Credentials
    import json
    import traceback
    from typing import Any, Dict, List
    from google.cloud import aiplatform, storage
    from google.cloud import bigquery
    from google.cloud.bigquery.job import LoadJobConfig
    from google_cloud_pipeline_components.experimental.automl.tabular import utils as automl_tabular_utils
    from google_cloud_pipeline_components.types.artifact_types import VertexModel
    from google.cloud.aiplatform_v1.services.pipeline_service import PipelineServiceClient
    from google.cloud.aiplatform_v1.types import GetPipelineJobRequest
    import os
    import uuid
    from kfp.v2 import compiler
    import collections
    import random
    import string
    from google_cloud_pipeline_components.experimental.automl.tabular import StatsAndExampleGenOp, TransformOp, Stage1TunerOp, CvTrainerOp, EnsembleOp
    from google_cloud_pipeline_components.aiplatform import ModelUploadOp
    from google_cloud_pipeline_components.v1.batch_predict_job import ModelBatchPredictOp
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
    from kfp import dsl
    from kubernetes.client.models import V1EnvVar, V1SecretKeySelector
    from kfp.v2.dsl import Artifact
    from google_cloud_pipeline_components.types import artifact_types
    from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp, ModelDeployOp)
    from comp_feature_store import run_feature_store_task
    from comp_train_automl_model import train_automl_model_init, resolve_params, train_automl_model_gen_output
    
    fs_op = run_feature_store_task(run_feature_store_task_params=RUN_FEATURE_STORE_TASK_PARAMS)

    init_op = train_automl_model_init(run_automl_training_task_params=RUN_AUTOML_TRAINING_TASK_PARAMS).after(fs_op)

    op = StatsAndExampleGenOp(
        project=PROJECT_ID,
        location=REGION,
        root_dir=statsexamplegen_root_dir,
        target_column_name='label', 
        transformations='[]',
        prediction_type='classification', 
        optimization_objective='minimize-log-loss', 
        transformations_path=init_op.outputs['transform_config_path'], 
        data_source_bigquery_table_path=DATA_SOURCE_TABLE_URI,
        dataflow_machine_type = 'n1-standard-16', 
        dataflow_max_num_workers = '25', 
        dataflow_disk_size_gb = '40', 
        dataflow_subnetwork = SUBNETWORK_SELF_LINK,
        dataflow_use_public_ips = 'false', 
        dataflow_service_account = SERVICE_ACCOUNT,
        run_distillation = 'false', 
        stratified_split_key = 'label', 
        training_fraction = '0.7', 
        validation_fraction = '0.2', 
        test_fraction = '0.1'
    )

    op1 = TransformOp(
        project=PROJECT_ID,
        location=REGION,
        root_dir=transformop_root_dir,
        metadata=op.outputs['metadata'],
        dataset_schema=op.outputs['dataset_schema'],
        train_split=op.outputs['train_split'],
        eval_split=op.outputs['eval_split'],
        test_split=op.outputs['test_split'],
        dataflow_subnetwork=SUBNETWORK_SELF_LINK,
        dataflow_use_public_ips=False,
        dataflow_service_account=SERVICE_ACCOUNT
    )

    op2 = Stage1TunerOp(
        project=PROJECT_ID,
        location=REGION,
        root_dir=stage1tuner_root_dir,
        reduce_search_space_mode='minimal',
        num_selected_trials=35,
        deadline_hours=0.78,
        num_parallel_trials=35,
        single_run_max_secs=650,
        metadata=op.outputs['metadata'],
        transform_output=op1.outputs['transform_output'],
        materialized_train_split=op1.outputs['materialized_train_split'],
        materialized_eval_split=op1.outputs['materialized_eval_split']
    )

    op3 = CvTrainerOp(
        project=PROJECT_ID,
        location=REGION,
        root_dir=cvtrainer_root_dir,
        worker_pool_specs_override_json='[{"machine_spec": {"machine_type": "n1-standard-8"}}, {}, {}, {"machine_spec": {"machine_type": "n1-standard-8"}}]',
        deadline_hours=0.23,
        num_parallel_trials=35,
        single_run_max_secs=635,
        num_selected_trials=5,
        transform_output=op1.outputs['transform_output'],
        metadata=op.outputs['metadata'],
        materialized_cv_splits=op1.outputs['materialized_train_split'],
        tuning_result_input=op2.outputs['tuning_result_output']
    )

    op4 = EnsembleOp(
        project=PROJECT_ID,
        location=REGION,
        root_dir=ensemble_root_dir,
        transform_output=op1.outputs['transform_output'],
        metadata=op.outputs['metadata'],
        dataset_schema=op.outputs['dataset_schema'],
        tuning_result_input=op3.outputs['tuning_result_output'],
        instance_baseline=op.outputs['instance_baseline'],
        warmup_data=op.outputs['eval_split'],
        export_additional_model_without_custom_ops=True
    )

    op5 = ModelUploadOp(
        project=PROJECT_ID,
        location=REGION,
        display_name=TRAINED_MODEL_NAME,
        unmanaged_container_model=op4.outputs['unmanaged_container_model'],
        explanation_metadata=op4.outputs['explanation_metadata'],
        explanation_parameters=op4.outputs['explanation_parameters']
    )

    automl_output = train_automl_model_gen_output(
        model_input=op5.outputs['model'],
        downsampled_test_split_json=op.outputs['downsampled_test_split_json'],
        test_split_json=op.outputs['test_split_json']
    )

    importer = kfp.v2.dsl.importer(
        artifact_uri=ENDPOINT_ARTIFACT_URI,
        artifact_class=artifact_types.VertexEndpoint,
        metadata={
              "resourceName": ENDPOINT_ID
            }
      )
    importer.set_display_name("import-vertexai-endpoint")
    endpoint = importer.output

    model_deployop = ModelDeployOp(
        endpoint=endpoint,
        model=automl_output.outputs['model'],
        deployed_model_display_name=TRAINED_MODEL_NAME,
        dedicated_resources_machine_type="n1-standard-8",
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
    )
