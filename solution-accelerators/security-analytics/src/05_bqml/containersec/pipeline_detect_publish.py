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

@kfp.dsl.pipeline(name=f"s05-containersec-detect-anomalies-{str(uuid1())}")
def pipeline(
    publish_anomalies_to_pubsub_params: dict,
    detect_anomalies_query: str,
    job_configuration_query: dict,
    project_id: str,
    bq_location: str,
    anomaly_table_id: str,
    bqml_artifact_uri: str,
    bqml_dataset_id: str,
    bqml_model_id: str
):
    import kfp
    from google_cloud_pipeline_components.v1.bigquery import BigqueryDetectAnomaliesModelJobOp
    from google_cloud_pipeline_components.types import artifact_types

    delete_inf_table = delete_inference_table(
        table_id=anomaly_table_id
    )

    importer = kfp.v2.dsl.importer(
        artifact_uri=bqml_artifact_uri,
        artifact_class=artifact_types.BQMLModel,
        metadata={
              "datasetId": bqml_dataset_id,
              "projectId": project_id,
              "modelId": bqml_model_id,
            }
      )
    importer.set_display_name("import-bqml-model")

    anomaly_detection = BigqueryDetectAnomaliesModelJobOp(
        project=project_id,
        location=bq_location,
        model=importer.output,
        query_statement=detect_anomalies_query,
        contamination=0.5,
        anomaly_prob_threshold=0.0,
        job_configuration_query=job_configuration_query
    ).after(delete_inf_table)

    op = publish_anomalies_to_pubsub(
        destination_table=anomaly_detection.outputs["destination_table"],
        params=publish_anomalies_to_pubsub_params,
    ).after(anomaly_detection)
