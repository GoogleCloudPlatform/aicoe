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
from google.cloud import bigquery
import kfp
from kfp.v2.dsl import Input, component, Artifact, Output
from kfp.v2 import compiler 
from typing import List, Any, Dict
import os
import uuid
from google.auth.compute_engine import Credentials


UUID = str(uuid.uuid1())


@kfp.dsl.pipeline(name="s04-ddos-do-online-prediction-" + UUID)
def pipeline(
    REGION: str,
    PROJECT_ID: str,
    PREDICTION_DATASET: str,
    PREDICTION_TABLE: str,
    SOURCE_DATASET: str,
    SOURCE_TABLE: str,
    INCIDENT_TOPIC_NAME: str,
    BUCKET_URI: str,
    BUCKET_NAME: str,
    ENDPOINT_ID: str,
    MODEL_NAME_PREFIX: str,
    OUTPUT_PREDICTION_DATASET: str,
    SERVICE_ACCOUNT: str,
    SUBNETWORK_SELF_LINK: str,
    AI_API_ENDPOINT: str,
    ROOT_DIR: str,
    SOURCE_INPUT_URI: str,
    DESTINATION_OUTPUT_URI: str,
    EVALUATION_ROOT_DIR: str,
):
    from kfp import dsl
    from kubernetes.client.models import V1EnvVar, V1SecretKeySelector
    from kfp.v2.dsl import Artifact
    from google_cloud_pipeline_components.v1.endpoint import (EndpointCreateOp, ModelDeployOp)
    from google_cloud_pipeline_components.experimental.automl.tabular import StatsAndExampleGenOp, TransformOp, Stage1TunerOp, CvTrainerOp, EnsembleOp
    from google_cloud_pipeline_components.aiplatform import ModelUploadOp
    from google_cloud_pipeline_components.v1.batch_predict_job import ModelBatchPredictOp
    from google_cloud_pipeline_components.experimental.evaluation import ModelEvaluationFeatureAttributionOp, ModelEvaluationOp, ModelImportEvaluationOp
    import os

    from comp_evaluate_online_prediction import find_latest_model_with_prefix_and_create_model_object,create_endpoint_object,do_online_prediction
    
    eop = create_endpoint_object(
        endpoint_id=ENDPOINT_ID
        )

    op11 = do_online_prediction(
            region=REGION,
            project_id=PROJECT_ID,
            prediction_dataset=PREDICTION_DATASET,
            prediction_table=PREDICTION_TABLE,
            source_dataset=SOURCE_DATASET,
            source_table=SOURCE_TABLE,
            incident_topic_name=INCIDENT_TOPIC_NAME,
            endpoint=eop.outputs['endpoint']
            )
    op11.set_cpu_limit('4.0').set_memory_limit('16G')
