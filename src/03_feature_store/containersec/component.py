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
    packages_to_install=["pandas", "google-cloud-bigquery", "scikit-learn", "numpy", "google-cloud-aiplatform", "pyarrow", "google-cloud-storage"],
    base_image="python:3.9",
)
def run_feature_store_task(
    params: dict
):
    import random
    import string
    import sys
    import traceback
    import datetime

    from google.api_core.client_options import ClientOptions
    from google.cloud import bigquery
    from google.cloud.aiplatform import Featurestore
    from google.cloud.bigquery.table import TableReference


    PROJECT_ID=params['PROJECT_ID']
    REGION=params['REGION']
    ONLINE_STORE_FIXED_NODE_COUNT=params['ONLINE_STORE_FIXED_NODE_COUNT']
    TEMP_DATASET=params['TEMP_DATASET']
    TEMP_SRC_TABLE=params['TEMP_SRC_TABLE']
    SOURCE_DATASET=params['SOURCE_DATASET']
    SOURCE_TABLE=params['SOURCE_TABLE']
    NEW_FEATURE_STORE_NAME=params['NEW_FEATURE_STORE_NAME']
    OLD_FEATURE_STORE_NAME=params['OLD_FEATURE_STORE_NAME']

    BQ_CLIENT_INFO = ClientOptions(quota_project_id = PROJECT_ID)
    BQ_CLIENT = bigquery.client.Client(project = PROJECT_ID, 
                                       client_options=BQ_CLIENT_INFO)
    # FS_ALREADY_EXISTS = False

    def delete_feature_store(name):
        if name is not None and len(name) > 0:
            try:
                fs = Featurestore(
                    featurestore_name=name,
                    project=PROJECT_ID,
                    location=REGION,
                )
                fs.delete(force=True)
            except:
                print('Failed to delete feature store: ' + name)
                raise

    def map_dtype_to_featurestore(feature_type):
        if feature_type == "STRING":
            return "STRING"
        elif feature_type in ["INTEGER", "INT", "SMALLINT", "INTEGER", "BIGINT", "TINYINT", "BYTEINT", "INT64"]:
            return "INT64"
        elif feature_type.startswith("ARRAY") or feature_type.startswith("STRUCT"):
            raise "Cannot process source table having columns with datatype " + feature_type
            return None
        elif feature_type in ["BIGNUMERIC", "NUMERIC", "DECIMAL", "BIGDECIMAL", "FLOAT64", "FLOAT"]:
            return "DOUBLE"
        elif feature_type.startswith("BIGNUMERIC") or feature_type.startswith("NUMERIC") or feature_type.startswith("DECIMAL") or feature_type.startswith("BIGDECIMAL"):
            return "DOUBLE"
        elif feature_type == "BOOL":
            return "BOOL"
        elif feature_type == "BYTES":
            return "BYTES"
        elif feature_type in ["DATE", "DATETIME", "INTERVAL", "TIME", "TIMESTAMP"]:
            return "STRING"
        elif feature_type == "JSON":
            return "STRING"
        else:
            return "STRING"


    def populate_feature_store(name):
        fs_already_exists = False

        # Check if already exists
        try:
            fs = Featurestore(
                featurestore_name=name,
                project=PROJECT_ID,
                location=REGION,
            )
            print('Feature Store already exists')
            readings_entity_type = fs.get_entity_type(
                entity_type_id="readings"
            )
            fs_already_exists = True
            return fs, readings_entity_type, fs_already_exists
        except Exception as e:
            print('Feature Store does not exists. Creating Feature Store')
            fs = Featurestore.create(
                featurestore_id=name,
                online_store_fixed_node_count=ONLINE_STORE_FIXED_NODE_COUNT,
                project=PROJECT_ID,
                location=REGION,
                sync=True,
            )

        fs = Featurestore(
            featurestore_name=name,
            project=PROJECT_ID,
            location=REGION,
        )
        print(f"{fs.gca_resource=}")

        readings_entity_type = fs.create_entity_type(
            entity_type_id="readings",
            description="Reading of metadata from app",
        )
        table_obj = BQ_CLIENT.get_table('{}.{}.{}'.format(PROJECT_ID, TEMP_DATASET, TEMP_SRC_TABLE))
        for s in table_obj.schema:
            readings_entity_type.create_feature(
                feature_id=s.name.lower(),
                value_type=map_dtype_to_featurestore(s.field_type),
                # description="Unnamed integer column",
            )

        return fs, readings_entity_type, fs_already_exists

    def get_feature_source_fields(readings_entity_type):
        lof = readings_entity_type.list_features(order_by='create_time')
        lofn = [f.name for f in lof]
        # LOGGER.info(lofn)

        src_table = BQ_CLIENT.get_table(TableReference.from_string('{}.{}.{}'.format(PROJECT_ID, TEMP_DATASET, TEMP_SRC_TABLE), default_project=PROJECT_ID))
        columns = [s.name for s in src_table.schema]

        print('Obtained mapping from feature store to bigquery')
        return lofn, dict(zip(lofn, columns))

    def create_temporary_source_table():
        try:
            query = '''CREATE OR REPLACE TABLE `{project}`.{tempds}.{temptab} AS 
                SELECT * EXCEPT(`timestamp`), CAST(`timestamp` as STRING) as timestamp_s,
                concat(endpoint, '-', CAST(`timestamp` as STRING)) as reading_id
                FROM `{project}`.{srcds}.{srctab}'''.format(project=PROJECT_ID,
                                                          tempds=TEMP_DATASET, srcds=SOURCE_DATASET, 
                                                          temptab=TEMP_SRC_TABLE, srctab=SOURCE_TABLE)
            print(f'query = {query}')
            BQ_CLIENT.query(query, project=PROJECT_ID).result()
            print('Created temporary source table')
        except:
            print('Error creating temporary source table')
            raise

    def populate_features_extract_features(fs, readings_entity_type, fs_already_exists):
        try:
            lofn, feature_source_fields = get_feature_source_fields(readings_entity_type)
            if fs_already_exists is False:
                readings_entity_type.ingest_from_bq(
                    feature_ids=lofn,
                    feature_time=datetime.datetime.now(),
                    bq_source_uri='bq://{}.{}.{}'.format(PROJECT_ID, TEMP_DATASET, TEMP_SRC_TABLE),
                    feature_source_fields=feature_source_fields,
                    entity_id_field='reading_id',
                    disable_online_serving=False,
                    sync=True
                )
                print('Ingested Bigquery Source table into Feature Store')
        except:
            print('Error populating features in bigquery')
            raise

    delete_feature_store(OLD_FEATURE_STORE_NAME)
    create_temporary_source_table()
    fs, readings_entity_type, fs_already_exists = populate_feature_store(NEW_FEATURE_STORE_NAME)
    populate_features_extract_features(fs, readings_entity_type, fs_already_exists)
