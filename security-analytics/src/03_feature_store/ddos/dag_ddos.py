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

from __future__ import annotations

import os
from datetime import datetime, timedelta
import argparse

# from airflow.providers.google.cloud.operators.dataflow import DataflowCreatePythonJobOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowConfiguration

# from airflow.contrib.operators.dataflow_operator import DataFlowPythonOperator
# from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow import models
from airflow.models import Variable
from airflow.providers.apache.beam.operators.beam import BeamRunPythonPipelineOperator
from airflow.operators.python import PythonVirtualenvOperator
import apache_beam as beam
import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions

# from sys import argv
from airflow.decorators import task
import logging
import json
import random
import string

START_DATE = datetime(2022, 11, 25)
# GCS_PYTHON = os.environ.get("GCP_DATAFLOW_PYTHON",
#         "gs://ml-sec-rh6-us-ddos/dag_pipeline_util.py")
# Airflow default arguments
default_args = {
    "depends_on_past": False,
    "start_date": datetime(2022, 10, 19),
    "email_on_failure": False,
    "email_on_retry": False,
    "catchup": False,
    "retries": 0,
    "donot_pickle": True,
    "retry_delay": timedelta(minutes=3),
}


def get_options(bucket_name, json_file):
    from google.cloud import storage
    import json

    # Instantiate a Google Cloud Storage client and specify required bucket and file
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(json_file)

    # Download the contents of the blob as a string and then parse it using json.loads() method
    return json.loads(blob.download_as_string(client=None))


@task.virtualenv(
    task_id="run-feature-store-vertexai-pipeline",
    requirements=[
        "google-cloud-storage==2.5.0",
        "google-cloud-aiplatform==1.18.2",
        "kfp==1.8.16",
        "google-cloud-pipeline-components==1.0.28",
    ],
    system_site_packages=False,
    python_version="3.8",
)
def callable_virtualenv(params: dict):
    import random
    import string
    from google.cloud import storage
    import google.cloud.aiplatform as aip
    import kfp
    import json
    from kfp.v2.dsl import Input, component, Output
    from kfp.v2 import compiler
    import uuid

    var_list = globals()
    for key, val in params.items():
        var_list.__setitem__(key, val)

    UUID = str(uuid.uuid4())
    BUCKET_URI = f"gs://{BUCKET_NAME}"
    PIPELINE_ROOT = "{}/pipeline_root/syn_dataset".format(BUCKET_URI)
    # WORKING_DIR = f"{PIPELINE_ROOT}/{UUID}"
    # MODEL_DISPLAY_NAME = f"train_deploy{UUID}"
    DISPLAY_NAME = "s03-ddos-run-feature-store-task-" + UUID

    # def generate_uuid(length: int = 8) -> str:
    #    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def create_bucket(name):
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(name)
            new_bucket = storage_client.create_bucket(bucket, location="us")
            print("Bucket created")
        except:
            print("Error creating bucket")

    @component(
        packages_to_install=[
            "pandas",
            "google-cloud-bigquery",
            "scikit-learn",
            "numpy",
            "google-cloud-aiplatform",
            "pyarrow",
            "google-cloud-storage",
        ],
        base_image="python:3.9",
    )
    def run_feature_store_task(params: dict):
        import sys
        from concurrent import futures
        from google.cloud.aiplatform import Featurestore
        import datetime
        import datetime
        from google.cloud import bigquery
        import traceback
        from google.api_core.client_options import ClientOptions
        from google.cloud.bigquery.table import TableReference

        var_list = globals()
        for key, val in params.items():
            var_list.__setitem__(key, val)

        BQ_CLIENT_INFO = ClientOptions(quota_project_id=PROJECT_ID)
        BQ_CLIENT = bigquery.client.Client(
            project=PROJECT_ID, client_options=BQ_CLIENT_INFO
        )

        def delete_feature_store(name) -> bool:
            try:
                if name is None or len(name) == 0:
                    return
                fs = Featurestore(
                    featurestore_name=name,
                    project=PROJECT_ID,
                    location=REGION,
                )
                fs.delete(force=True)
            except:
                print("Failed to delete feature store: " + name)
            return

        def populate_feature_store(name):
            fs_already_exists = False

            try:
                fs = Featurestore(
                    featurestore_name=name,
                    project=PROJECT_ID,
                    location=REGION,
                )
                print(fs.gca_resource)
                flows_entity_type = fs.get_entity_type(entity_type_id="flows")
                fs_already_exists = True
                print("Feature store {} already exists".format(name))
                return fs, flows_entity_type, fs_already_exists
            except Exception as e:
                print("Feature store {} does not exists. Creating new. ".format(name))
                fs = Featurestore.create(
                    featurestore_id=name,
                    online_store_fixed_node_count=ONLINE_STORE_FIXED_NODE_COUNT,
                    project=PROJECT_ID,
                    location=REGION,
                    sync=True,
                )
                flows_entity_type = fs.create_entity_type(
                    entity_type_id="flows",
                    description="TCP flows in the dataset",
                )

            fs = Featurestore(
                featurestore_name=name,
                project=PROJECT_ID,
                location=REGION,
            )
            flows_entity_type = fs.get_entity_type(entity_type_id="flows")

            flows_entity_type.batch_create_features(
                feature_configs=FEATURE_STORE_FEATURE_NAMES
            )
            return fs, flows_entity_type, fs_already_exists

        def get_feature_source_fields(flows_entity_type):
            lof = flows_entity_type.list_features(order_by="create_time")
            lofn = [f.name for f in lof]
            # LOGGER.info(lofn)

            src_table = BQ_CLIENT.get_table(
                TableReference.from_string(
                    "{}.{}.{}".format(PROJECT_ID, SOURCE_DATASET, SOURCE_TABLE),
                    default_project=PROJECT_ID,
                )
            )
            columns = [s.name for s in src_table.schema]

            lofn.remove("timestamp")
            columns.remove("Timestamp")
            print("Obtained mapping from feature store to bigquery")
            return lofn, dict(zip(lofn, columns))

        def populate_features_extract_features(fs, flows_entity_type, already_exists):
            try:
                lofn, feature_source_fields = get_feature_source_fields(
                    flows_entity_type
                )
                if already_exists == False:
                    ent_type = flows_entity_type.ingest_from_bq(
                        feature_ids=lofn,
                        feature_time=datetime.datetime.now(),
                        bq_source_uri="bq://{}.{}.{}".format(
                            PROJECT_ID, SOURCE_DATASET, SOURCE_TABLE
                        ),
                        feature_source_fields=feature_source_fields,
                        entity_id_field="FlowID",
                        disable_online_serving=False,
                        sync=False,
                        ingest_request_timeout=7200,
                        worker_count=10,
                    )
                    futures.wait(
                        [ent_type._latest_future],
                        timeout=50 * 60,
                        return_when=futures.FIRST_EXCEPTION,
                    )
                    print("Ingested Bigquery Source table into Feature Store")

            except:
                traceback.print_exc()
                print("Error populating features in bigquery")

        delete_feature_store(OLD_FEATURE_STORE)
        fs, flows_entity_type, already_exists = populate_feature_store(
            NEW_FEATURE_STORE
        )
        populate_features_extract_features(fs, flows_entity_type, already_exists)
        sys.exit(0)

    @kfp.dsl.pipeline(name="s03-ddos-run-feature-store-task-" + UUID)
    def pipeline(run_feature_store_task_params: dict = RUN_FEATURE_STORE_TASK_PARAMS):
        op = run_feature_store_task(run_feature_store_task_params)

    create_bucket(BUCKET_NAME)
    aip.init(project=PROJECT_ID, staging_bucket=BUCKET_URI)

    compiler.Compiler().compile(
        pipeline_func=pipeline,
        package_path="ddos-tabular_regression_pipeline.json",
    )

    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="ddos-tabular_regression_pipeline.json",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
        parameter_values={
            "run_feature_store_task_params": RUN_FEATURE_STORE_TASK_PARAMS
        },
    )

    job.run(service_account=SERVICE_ACCOUNT)


bucket_name = os.environ.get("ddos_bucket_name", "")
conf_file = os.environ.get("ddos_conf_file", "ddos_settings.json")

options = get_options(bucket_name, conf_file)
beam_options = options["beam_options"]
random_job_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=3))
version_suffix = "-v03"
dag_name = beam_options["job_name"] + version_suffix
job_name = beam_options["job_name"] + version_suffix
beam_options["job_name"] = job_name
vertexai_options = options["vertexai_options"]
GCS_PYTHON = options.get("dag", {}).get("py_file", "")
with models.DAG(
    dag_id=dag_name,
    schedule_interval=options.get("dag", {}).get("schedule_interval", "0 3 * * *"),
    default_args=default_args,
    start_date=START_DATE,
) as dag:
    parser = argparse.ArgumentParser()

    start_python_job = BeamRunPythonPipelineOperator(
        task_id="load-ddos-" + beam_options["random_suffix"] + version_suffix,
        py_file=GCS_PYTHON,
        pipeline_options=beam_options,
        py_interpreter="python3",
        py_system_site_packages=False,
        dataflow_config=DataflowConfiguration(
            job_name="{{task.task_id}}",
            location=beam_options["region"],
            wait_until_finished=True,
            gcp_conn_id="google_cloud_default",
        ),
    )

    start_featurestore_job = callable_virtualenv(vertexai_options)

    start = DummyOperator(task_id="start", dag=dag)
    end = DummyOperator(task_id="end", dag=dag)
    start >> start_python_job >> start_featurestore_job >> end
    # start >> start_featurestore_job >> end
