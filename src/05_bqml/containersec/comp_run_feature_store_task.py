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


from kfp.v2.dsl import component

@component(
    packages_to_install=[
        "pandas==1.5.2",
        "google-cloud-bigquery==2.34.4",
        "scikit-learn==1.2.0",
        "numpy==1.22.4",
        "google-cloud-aiplatform==1.20.0",
        "pyarrow==9.0.0",
        "google-cloud-storage==2.7.0",
        "db-dtypes==1.0.5",
    ],
    base_image="python:3.9",
)
def run_feature_store_task(
    run_feature_store_task_params: dict
    ):
    import datetime
    import logging
    import random
    import string
    import sys
    import traceback

    from google.api_core.client_options import ClientOptions
    from google.cloud import bigquery
    from google.cloud import storage
    from google.cloud.aiplatform import Featurestore
    from google.cloud.bigquery.table import TableReference

    # By extracting variables at an early stage we fail fast in case of a missing key
    PROJECT_ID=run_feature_store_task_params['PROJECT_ID']
    REGION=run_feature_store_task_params['REGION']
    TEMP_FILE_BUCKET=run_feature_store_task_params['TEMP_FILE_BUCKET']
    TEMP_FILE_PATH=run_feature_store_task_params['TEMP_FILE_PATH']
    DESTINATION_DATA_SET=run_feature_store_task_params['DESTINATION_DATA_SET']
    DESTINATION_TABLE_NAME=run_feature_store_task_params['DESTINATION_TABLE_NAME']
    DESTINATION_TABLE_URI = f"bq://{PROJECT_ID}.{DESTINATION_DATA_SET}.{DESTINATION_TABLE_NAME}"
    TEMP_DATASET=run_feature_store_task_params['TEMP_DATASET']
    TEMP_SRC_TABLE=run_feature_store_task_params['TEMP_SRC_TABLE']
    NEW_FEATURE_STORE_NAME=run_feature_store_task_params['NEW_FEATURE_STORE_NAME']

    ONLINE_STORE_FIXED_NODE_COUNT=run_feature_store_task_params['ONLINE_STORE_FIXED_NODE_COUNT']
    SOURCE_DATASET=run_feature_store_task_params['SOURCE_DATASET']
    SOURCE_TABLE=run_feature_store_task_params['SOURCE_TABLE']
 
    BQ_CLIENT_INFO = ClientOptions(quota_project_id=PROJECT_ID)
    BQ_CLIENT = bigquery.client.Client(
        project=PROJECT_ID, client_options=BQ_CLIENT_INFO
    )
    STORAGE_CLIENT = storage.client.Client(project=PROJECT_ID)

    def get_feature_source_fields(readings_entity_type):
        lof = readings_entity_type.list_features(order_by="create_time")
        lofn = [f.name for f in lof]

        src_table = BQ_CLIENT.get_table(
            TableReference.from_string(
                f"{PROJECT_ID}.{TEMP_DATASET}.{TEMP_SRC_TABLE}",
                default_project=PROJECT_ID,
            )
        )
        columns = [s.name for s in src_table.schema]

        print("Obtained mapping from feature store to bigquery")
        return lofn, dict(zip(lofn, columns))

    def delete_target_predict_table():
        try:
            BQ_CLIENT.delete_table(
                f"{PROJECT_ID}.{DESTINATION_DATA_SET}.{DESTINATION_TABLE_NAME}"
            )
            print("Deleted target predict table")
        except:
            print("Error deleting target predict table")

    def populate_file_to_get_feature_now():
        try:
            df = BQ_CLIENT.query(
                f"SELECT reading_id as readings FROM {PROJECT_ID}.{TEMP_DATASET}.{TEMP_SRC_TABLE}",
                project=PROJECT_ID,
            ).to_dataframe()
            print("Obtained IDs from Bigquery")
            df["timestamp"] = datetime.datetime.now()

            bucket = STORAGE_CLIENT.get_bucket(TEMP_FILE_BUCKET)
            bucket.blob(TEMP_FILE_PATH).upload_from_string(
                df.to_csv(index=False), "text/csv"
            )
            print("Created file in GCS for populating all feature values")
        except:
            traceback.print_exc()
            print("Error creating file in GCS for populating all feature values")

    def populate_features_extract_features(fs, readings_entity_type):
        try:
            lofn, feature_source_fields = get_feature_source_fields(
                readings_entity_type
            )
            populate_file_to_get_feature_now()
            delete_target_predict_table()
            fs.batch_serve_to_bq(
                bq_destination_output_uri=DESTINATION_TABLE_URI,
                serving_feature_ids={"readings": lofn},
                read_instances_uri=f"gs://{TEMP_FILE_BUCKET}/{TEMP_FILE_PATH}",
            )
            print("Batch served features to Bigquery target table.")
        except:
            traceback.print_exc()
            print("Error populating features in bigquery")

    fs = Featurestore(
        featurestore_name=NEW_FEATURE_STORE_NAME,
        project=PROJECT_ID,
        location=REGION,
    )
    readings_entity_type = fs.get_entity_type(entity_type_id="readings")
    populate_features_extract_features(fs, readings_entity_type)
