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
 
 
from kfp.v2.dsl import Input, component, Artifact, Output

@component(
    packages_to_install=["pandas==1.5.2", "google-cloud-bigquery==2.34.4", "scikit-learn==1.2.0", "numpy==1.22.4", 
        "google-cloud-aiplatform==1.20.0", "pyarrow==9.0.0", "google-cloud-storage==2.7.0"],
    base_image="python:3.9",
)
def run_feature_store_task(
    run_feature_store_task_params: dict,
):
    import os
    import random
    import string
    import time
    import sys
    from concurrent import futures
    from google.cloud.aiplatform import Feature, Featurestore
    import datetime
    import datetime
    from google.cloud import bigquery
    from google.cloud import storage
    import traceback
    import logging
    import argparse
    from google.cloud.bigquery.job import QueryJobConfig
    from google.api_core.client_options import ClientOptions
    from google.cloud.bigquery.table import TableReference

    # By extracting variables at an early stage we fail fast in case of a missing key
    PROJECT_ID=run_feature_store_task_params['PROJECT_ID']
    REGION=run_feature_store_task_params['REGION']
    OLD_FEATURE_STORE=run_feature_store_task_params['OLD_FEATURE_STORE']
    NEW_FEATURE_STORE=run_feature_store_task_params['NEW_FEATURE_STORE']
    ONLINE_STORE_FIXED_NODE_COUNT=run_feature_store_task_params['ONLINE_STORE_FIXED_NODE_COUNT']
    SOURCE_DATASET=run_feature_store_task_params['SOURCE_DATASET']
    SOURCE_TABLE=run_feature_store_task_params['SOURCE_TABLE']
    TEMP_FILE_BUCKET=run_feature_store_task_params['TEMP_FILE_BUCKET']
    TEMP_FILE_PATH=run_feature_store_task_params['TEMP_FILE_PATH']
    DESTINATION_DATA_SET=run_feature_store_task_params['DESTINATION_DATA_SET']
    DESTINATION_TABLE_NAME=run_feature_store_task_params['DESTINATION_TABLE_NAME']
    DESTINATION_TABLE_URI=run_feature_store_task_params['DESTINATION_TABLE_URI']

    LOGGER = logging.getLogger()
    BQ_CLIENT_INFO = ClientOptions(quota_project_id=PROJECT_ID)
    BQ_CLIENT = bigquery.client.Client(project=PROJECT_ID, client_options=BQ_CLIENT_INFO)
    STORAGE_CLIENT = storage.client.Client(project=PROJECT_ID)

    def delete_feature_store(project_id, region, name) -> bool:
        try:
            if name is None or len(name) == 0:
                return
            fs = Featurestore(
                featurestore_name=name,
                project=project_id,
                location=region,
            )
            fs.delete(force=True)
        except:
            print('Failed to delete feature store: ' + name)
        return


    def populate_feature_store(project_id, region, name, online_store_fixed_node_count):
        fs_already_exists = False
        
        try:
            fs = Featurestore(
                featurestore_name=name,
                project=project_id,
                location=region,
            )
            print(fs.gca_resource)
            flows_entity_type = fs.get_entity_type(
                entity_type_id="flows"
            )
            fs_already_exists = True
            print('Feature store {} already exists'.format(name))
            return fs, flows_entity_type, fs_already_exists
        except Exception as e:
            print('Feature store {} does not exists. Creating new. '.format(name))
            fs = Featurestore.create(
                featurestore_id=name,
                online_store_fixed_node_count=online_store_fixed_node_count,
                project=project_id,
                location=region,
                sync=True,
            )
            flows_entity_type = fs.create_entity_type(
                entity_type_id="flows",
                description="TCP flows in the dataset",
            )

        fs = Featurestore(
            featurestore_name=name,
            project=project_id,
            location=region,
        )
        flows_entity_type = fs.get_entity_type(
            entity_type_id="flows"
        )

        flows_entity_type.batch_create_features(
            feature_configs={
                "c0": {
                        "value_type": "INT64",
                    },
                "flow_id": {
                        "value_type": "STRING",
                    },
                "src_ip": {
                        "value_type": "STRING",
                    },
                "src_port": {
                        "value_type": "INT64",
                    },
                "dst_ip": {
                        "value_type": "STRING",
                    },
                "dst_port": {
                        "value_type": "INT64",
                    },
                "protocol": {
                        "value_type": "INT64",
                    },
                "timestamp": {
                        "value_type": "STRING",
                    },
                "flow_duration": {
                        "value_type": "INT64",
                    },
                "tot_fwd_pkts": {
                        "value_type": "INT64",
                    },
                "tot_bwd_pkts": {
                        "value_type": "INT64",
                    },
                "totlen_fwd_pkts": {
                        "value_type": "DOUBLE",
                    },
                "totlen_bwd_pkts": {
                        "value_type": "DOUBLE",
                    },
                "fwd_pkt_len_max": {
                        "value_type": "DOUBLE",
                    },
                "fwd_pkt_len_min": {
                        "value_type": "DOUBLE",
                    },
                "fwd_pkt_len_mean": {
                        "value_type": "DOUBLE",
                    },
                "fwd_pkt_len_std": {
                        "value_type": "DOUBLE",
                    },
                "bwd_pkt_len_max": {
                        "value_type": "DOUBLE",
                    },
                "bwd_pkt_len_min": {
                        "value_type": "DOUBLE",
                    },
                "bwd_pkt_len_mean": {
                        "value_type": "DOUBLE",
                    },
                "bwd_pkt_len_std": {
                        "value_type": "DOUBLE",
                    },
                "flow_byts_s": {
                        "value_type": "DOUBLE",
                    },
                "flow_pkts_s": {
                        "value_type": "DOUBLE",
                    },
                "flow_iat_mean": {
                        "value_type": "DOUBLE",
                    },
                "flow_iat_std": {
                        "value_type": "DOUBLE",
                    },
                "flow_iat_max": {
                        "value_type": "DOUBLE",
                    },
                "flow_iat_min": {
                        "value_type": "DOUBLE",
                    },
                "fwd_iat_tot": {
                        "value_type": "DOUBLE",
                    },
                "fwd_iat_mean": {
                        "value_type": "DOUBLE",
                    },
                "fwd_iat_std": {
                        "value_type": "DOUBLE",
                    },
                "fwd_iat_max": {
                        "value_type": "DOUBLE",
                    },
                "fwd_iat_min": {
                        "value_type": "DOUBLE",
                    },
                "bwd_iat_tot": {
                        "value_type": "DOUBLE",
                    },
                "bwd_iat_mean": {
                        "value_type": "DOUBLE",
                    },
                "bwd_iat_std": {
                        "value_type": "DOUBLE",
                    },
                "bwd_iat_max": {
                        "value_type": "DOUBLE",
                    },
                "bwd_iat_min": {
                        "value_type": "DOUBLE",
                    },
                "fwd_psh_flags": {
                        "value_type": "INT64",
                    },
                "bwd_psh_flags": {
                        "value_type": "INT64",
                    },
                "fwd_urg_flags": {
                        "value_type": "INT64",
                    },
                "bwd_urg_flags": {
                        "value_type": "INT64",
                    },
                "fwd_header_len": {
                        "value_type": "INT64",
                    },
                "bwd_header_len": {
                        "value_type": "INT64",
                    },
                "fwd_pkts_s": {
                        "value_type": "DOUBLE",
                    },
                "bwd_pkts_s": {
                        "value_type": "DOUBLE",
                    },
                "pkt_len_min": {
                        "value_type": "DOUBLE",
                    },
                "pkt_len_max": {
                        "value_type": "DOUBLE",
                    },
                "pkt_len_mean": {
                        "value_type": "DOUBLE",
                    },
                "pkt_len_std": {
                        "value_type": "DOUBLE",
                    },
                "pkt_len_var": {
                        "value_type": "DOUBLE",
                    },
                "fin_flag_cnt": {
                        "value_type": "INT64",
                    },
                "syn_flag_cnt": {
                        "value_type": "INT64",
                    },
                "rst_flag_cnt": {
                        "value_type": "INT64",
                    },
                "psh_flag_cnt": {
                        "value_type": "INT64",
                    },
                "ack_flag_cnt": {
                        "value_type": "INT64",
                    },
                "urg_flag_cnt": {
                        "value_type": "INT64",
                    },
                "cwe_flag_cnt": {
                        "value_type": "INT64",
                    },
                "ece_flag_cnt": {
                        "value_type": "INT64",
                    },
                "down_up_ratio": {
                        "value_type": "DOUBLE",
                    },
                "pkt_size_avg": {
                        "value_type": "DOUBLE",
                    },
                "fwd_seg_size_avg": {
                        "value_type": "DOUBLE",
                    },
                "bwd_seg_size_avg": {
                        "value_type": "DOUBLE",
                    },
                "fwd_byts_b_avg": {
                        "value_type": "INT64",
                    },
                "fwd_pkts_b_avg": {
                        "value_type": "INT64",
                    },
                "fwd_blk_rate_avg": {
                        "value_type": "INT64",
                    },
                "bwd_byts_b_avg": {
                        "value_type": "INT64",
                    },
                "bwd_pkts_b_avg": {
                        "value_type": "INT64",
                    },
                "bwd_blk_rate_avg": {
                        "value_type": "INT64",
                    },
                "subflow_fwd_pkts": {
                        "value_type": "INT64",
                    },
                "subflow_fwd_byts": {
                        "value_type": "INT64",
                    },
                "subflow_bwd_pkts": {
                        "value_type": "INT64",
                    },
                "subflow_bwd_byts": {
                        "value_type": "INT64",
                    },
                "init_fwd_win_byts": {
                        "value_type": "INT64",
                    },
                "init_bwd_win_byts": {
                        "value_type": "INT64",
                    },
                "fwd_act_data_pkts": {
                        "value_type": "INT64",
                    },
                "fwd_seg_size_min": {
                        "value_type": "INT64",
                    },
                "active_mean": {
                        "value_type": "DOUBLE",
                    },
                "active_std": {
                        "value_type": "DOUBLE",
                    },
                "active_max": {
                        "value_type": "DOUBLE",
                    },
                "active_min": {
                        "value_type": "DOUBLE",
                    },
                "idle_mean": {
                        "value_type": "DOUBLE",
                    },
                "idle_std": {
                        "value_type": "DOUBLE",
                    },
                "idle_max": {
                        "value_type": "DOUBLE",
                    },
                "idle_min": {
                        "value_type": "DOUBLE",
                    },
                "label": {
                        "value_type": "STRING",
                    }
            }
        )
        return fs, flows_entity_type, fs_already_exists

    def get_feature_source_fields(project_id, flows_entity_type, source_dataset, source_table):
        lof = flows_entity_type.list_features(order_by='create_time')
        lofn = [f.name for f in lof]
        # LOGGER.info(lofn)

        src_table = BQ_CLIENT.get_table(TableReference.from_string('{}.{}.{}'.format(project_id, source_dataset, source_table), default_project=project_id))
        columns = [s.name for s in src_table.schema]

        lofn.remove('timestamp')
        columns.remove('Timestamp')
        print('Obtained mapping from feature store to bigquery')
        return lofn, dict(zip(lofn, columns))

    def delete_target_predict_table(project_id, destination_data_set, destination_table_name):
        try:
            BQ_CLIENT.delete_table('{}.{}.{}'.format(project_id, destination_data_set, destination_table_name))
            print('Deleted target predict table')
        except:
            print('Error deleting target predict table')

    def populate_file_to_get_feature_now(project_id, source_dataset, source_table, temp_file_bucket, temp_file_path):
        try:
            df = BQ_CLIENT.query(f"SELECT `FlowID` as flows FROM `{project_id}`.`{source_dataset}`.`{source_table}`", project=project_id).to_dataframe()
            print('Obtained Feature IDs from Bigquery')
            df['timestamp'] = datetime.datetime.now()

            bucket = STORAGE_CLIENT.get_bucket(temp_file_bucket)
            bucket.blob(temp_file_path).upload_from_string(df.to_csv(index=False), 'text/csv')
            print('Created file in GCS for populating all feature values')
        except:
            traceback.print_exc()
            print('Error creating file in GCS for populating all feature values')


    def populate_features_extract_features(project_id, source_dataset, source_table, destination_table_uri, temp_file_bucket, temp_file_path, fs, flows_entity_type, already_exists, destination_data_set, destination_table_name):
        try:
            lofn, feature_source_fields = get_feature_source_fields(project_id, flows_entity_type, source_dataset, source_table)
            if already_exists == False:
                ent_type = flows_entity_type.ingest_from_bq(
                    feature_ids=lofn,
                    feature_time=datetime.datetime.now(),
                    bq_source_uri='bq://{}.{}.{}'.format(project_id, source_dataset, source_table),
                    feature_source_fields=feature_source_fields,
                    entity_id_field='FlowID',
                    disable_online_serving=False,
                    sync=False,
                    ingest_request_timeout=7200,
                    worker_count=10
                )
                futures.wait([ent_type._latest_future], timeout=50*60, return_when=futures.FIRST_EXCEPTION)
                print('Ingested Bigquery Source table into Feature Store')

            populate_file_to_get_feature_now(project_id, source_dataset, source_table, temp_file_bucket, temp_file_path)
            delete_target_predict_table(project_id, destination_data_set, destination_table_name)
            fs.batch_serve_to_bq(
                bq_destination_output_uri=destination_table_uri,
                serving_feature_ids={ "flows": lofn },
                read_instances_uri='gs://{}/{}'.format(temp_file_bucket, temp_file_path)
            )
            print('Batch served features to Bigquery target table.')
        except:
            traceback.print_exc()
            print('Error populating features in bigquery')

    delete_feature_store(PROJECT_ID,
                         REGION,
                         OLD_FEATURE_STORE)
    
    fs, flows_entity_type, already_exists = populate_feature_store(
        PROJECT_ID, 
        REGION, 
        NEW_FEATURE_STORE, 
        ONLINE_STORE_FIXED_NODE_COUNT)
    
    populate_features_extract_features(
        PROJECT_ID, 
        SOURCE_DATASET,
        SOURCE_TABLE,
        DESTINATION_TABLE_URI,
        TEMP_FILE_BUCKET,
        TEMP_FILE_PATH,
        fs, 
        flows_entity_type, 
        already_exists,
        DESTINATION_DATA_SET,
        DESTINATION_TABLE_NAME,
        )
