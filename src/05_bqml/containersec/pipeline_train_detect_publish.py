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

from comp_publish_anomalies import delete_inference_table,publish_anomalies_to_pubsub
from comp_run_feature_store_task import run_feature_store_task

@kfp.dsl.pipeline(name=f"s05-containersec-train-detect-anomalies-{str(uuid1())}")
def pipeline(
    publish_anomalies_to_pubsub_params: dict,
    run_feature_store_task_params: dict,
    pipeline_launch_params: dict,
    create_model_query: str,
    detect_anomalies_query: str,
    job_configuration_query: dict,
    project_id: str,
    bq_location: str,
    anomaly_table_id: str
):
    import json
    from google_cloud_pipeline_components.v1.custom_job import CustomTrainingJobOp
    from google_cloud_pipeline_components.v1.endpoint import (
        EndpointCreateOp,
        ModelDeployOp,
    )
    from google_cloud_pipeline_components.v1.model import ModelUploadOp
    from kfp.v2.components import importer_node
    from google_cloud_pipeline_components.v1.batch_predict_job import (
        ModelBatchPredictOp,
    )
    from google_cloud_pipeline_components.experimental.evaluation import (
        ModelEvaluationOp,
    )
    from google_cloud_pipeline_components.v1.bigquery import (
        BigqueryCreateModelJobOp,
        BigqueryEvaluateModelJobOp,
        BigqueryDetectAnomaliesModelJobOp,
    )

    run_fs_task = run_feature_store_task(run_feature_store_task_params=run_feature_store_task_params)
    create_model_op = BigqueryCreateModelJobOp(
        project=project_id,
        location=bq_location,
        query=create_model_query,
    ).after(run_fs_task)

    delete_inf_table = delete_inference_table(
        table_id=anomaly_table_id
    ).after(create_model_op)

    anomaly_detection = BigqueryDetectAnomaliesModelJobOp(
        project=project_id,
        location=bq_location,
        model=create_model_op.outputs["model"],
        query_statement=detect_anomalies_query,
        contamination=0.5,
        anomaly_prob_threshold=0.0,
        job_configuration_query=job_configuration_query
    ).after(delete_inf_table)

    op = publish_anomalies_to_pubsub(
        destination_table=anomaly_detection.outputs["destination_table"],
        params=publish_anomalies_to_pubsub_params,
    ).after(anomaly_detection)
