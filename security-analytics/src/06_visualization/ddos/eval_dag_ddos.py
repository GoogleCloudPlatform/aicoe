#!/usr/bin/env python

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
from airflow.providers.google.cloud.operators.dataflow import DataflowConfiguration, CheckJobRunning, DataflowCreatePythonJobOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow import models
from airflow.providers.apache.beam.operators.beam import BeamRunPythonPipelineOperator
import argparse
from airflow import configuration
from airflow.decorators import task

        
START_DATE = datetime(2022, 11, 25)

# Airflow default arguments
default_args = {
    'depends_on_past': False,
    'start_date': datetime(2022, 10, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'catchup': False,
    'retries': 0,
    'donot_pickle': True,
    'retry_delay': timedelta(minutes=3)
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


bucket_name = os.environ.get("ddos_bucket_name", "")
conf_file = os.environ.get("ddos_conf_file", "eval_ddos_settings.json")

options = get_options(bucket_name, conf_file)
beam_options = options['beam_options']

dags_folder = configuration.get('core', 'dags_folder')
beam_options['setup_file'] = os.path.join(dags_folder, beam_options['setup_file'])
GCS_PYTHON = options.get("dag", {}).get("py_file", '')
with models.DAG(
    dag_id=beam_options['job_name'],
    schedule_interval=options.get("dag", {}).get("schedule_interval", '@once'),
    default_args = default_args,
    start_date = START_DATE
) as dag:
    parser = argparse.ArgumentParser()
    
    start_python_job = DataflowCreatePythonJobOperator(
        py_file=GCS_PYTHON,
        job_name="{{task.task_id}}",
        options = beam_options,
        py_interpreter = "python3",
        py_requirements = ['google-cloud-aiplatform', 'apache-beam', 'apache-airflow-providers-apache-beam', 'apache-airflow-providers-google', 'pandas', 'google-apitools'],
        py_system_site_packages = False,
        project_id = beam_options['project'],
        location = beam_options['region'],
        gcp_conn_id = "google_cloud_default",
        wait_until_finished = False,
        task_id = beam_options['job_name']
    )
    
    start=DummyOperator(task_id="start", dag=dag)
    end=DummyOperator(task_id="end", dag=dag)
    start >> start_python_job >> end
