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


@component(
    packages_to_install=["pandas"],
    base_image="python:3.8",
)
def create_model_object(model_name: str, model: Output[Artifact]):
    model.metadata['resourceName'] = model_name


@component(
    packages_to_install=["pandas","google-cloud-aiplatform==1.20.0"],
    base_image="python:3.8",
)
def find_latest_model_with_prefix_and_create_model_object(ai_api_endpoint: str, project_id: str, region: str, model_name_prefix: str, model: Output[Artifact]):
    from google.cloud import aiplatform_v1

    def get_latest_model_with_prefix(project_id, region, prefix) -> list:
        # Create a client
        client_options = {"api_endpoint": ai_api_endpoint}
        client = aiplatform_v1.ModelServiceClient(client_options=client_options)

        # Initialize request argument(s)
        request = aiplatform_v1.ListModelsRequest(
            parent=f"projects/{project_id}/locations/{region}",
        )

        # Make the request
        page_result = client.list_models(request=request)

        # Handle the response: filter for name prefix, sort, return the latest item
        responses = [{"name": response.name, "display_name": response.display_name, "create_time": response.create_time} for response in page_result]
        responses_filtered = list(filter(lambda x: x['display_name'].startswith(prefix), responses))
        responses_filtered_sorted = sorted(responses_filtered, key=lambda x: x['create_time'], reverse=True)
        if len(responses_filtered_sorted) > 0:
            return responses_filtered_sorted[0]
        else:
            raise Exception(f"Models starting with prefix {prefix} not found")

    model.metadata['resourceName'] = get_latest_model_with_prefix(project_id, region, model_name_prefix)['name']


@component(
    packages_to_install=["pandas"],
    base_image="python:3.8",
)
def create_endpoint_object(endpoint_id: str, endpoint: Output[Artifact]):
    endpoint.metadata['resourceName'] = endpoint_id


@component(
    packages_to_install=["google-cloud-aiplatform==1.20.0", "google-cloud-bigquery==2.34.4", "pandas==1.5.2", "numpy==1.22.4",
        "scikit-learn==1.2.0", "pyarrow==9.0.0", "google-cloud-bigquery-storage==2.13.2", "google-cloud-bigquery-storage[fastavro]",
        "google-cloud-pubsub==2.13.11"],
    base_image="python:3.8",
)
def do_online_prediction(
    region: str,
    project_id: str,
    prediction_dataset: str,
    prediction_table: str,
    source_dataset: str,
    source_table: str,
    incident_topic_name: str,
    endpoint: Input[Artifact]
):
    from google.cloud import bigquery
    import pandas as pd
    import os
    import numpy as np
    from sklearn.preprocessing import LabelEncoder, normalize
    from google.cloud.aiplatform_v1.types import Endpoint
    import argparse
    import json
    import copy
    from decimal import Decimal
    from google.cloud import aiplatform
    import sys
    import logging
    from google.cloud.bigquery.schema import SchemaField
    from google.cloud.bigquery.dataset import DatasetReference
    from google.cloud.bigquery.table import TableReference, Table
    from google.cloud.bigquery_storage import BigQueryReadClient
    from google.cloud.bigquery_storage import types
    from google.api_core.retry import Retry
    import time
    from google import pubsub_v1

    LOGGER = logging.getLogger()

    def check_if_already_exists(client, table):
        try:
            client.get_table('{}.{}.{}'.format(project_id, prediction_dataset, prediction_table))
            return True
        except:
            return False


    #     class Object():
    #         def __init__(self):
    #             self.metadata = {
    #                 'resourceName': 'projects/757095049861/locations/us-central1/endpoints/43245991343685632'
    #             }

    #     endpoint = Object()
    BQ_CLIENT = bigquery.Client(project=project_id)
    BQ_CLIENT2 = bigquery.Client(project=project_id)
    BQ_STORAGE_CLIENT = BigQueryReadClient()
    PS_CLIENT = pubsub_v1.PublisherClient()
    aiplatform.init(project=project_id, location=region)

    SOURCE_TABLE_OBJ = BQ_CLIENT.get_table('{}.{}.{}'.format(project_id, source_dataset, source_table))
    TARGET_TABLE_SCHEMA = copy.deepcopy(SOURCE_TABLE_OBJ.schema)
    TARGET_TABLE_SCHEMA.extend([SchemaField(name='predict', field_type='STRING'),
                              SchemaField(name='json', field_type='STRING')])
    del TARGET_TABLE_SCHEMA[2]
    TARGET_TABLE_SCHEMA.insert(2, SchemaField(name='c0', field_type='INTEGER'))
    prediction_table_OBJ = None
    TOPIC_NAME = incident_topic_name

    if check_if_already_exists(BQ_CLIENT, '{}.{}.{}'.format(project_id, prediction_dataset, prediction_table)):
        BQ_CLIENT.delete_table('{}.{}.{}'.format(project_id, prediction_dataset, prediction_table))
        time.sleep(1)

    ds_ref = DatasetReference(project_id, prediction_dataset)
    table_ref = TableReference(ds_ref, prediction_table)
    table_obj = Table(table_ref, schema=TARGET_TABLE_SCHEMA)
    prediction_table_OBJ = BQ_CLIENT.create_table(table_obj)

    requested_session = types.ReadSession()
    requested_session.table = "projects/{}/datasets/{}/tables/{}".format(project_id, source_dataset, source_table)
    requested_session.data_format = types.DataFormat.AVRO

    session = BQ_STORAGE_CLIENT.create_read_session(parent="projects/{}".format(project_id), read_session=requested_session, max_stream_count=1)

    print(endpoint.metadata['resourceName'])
    endpoint_name = endpoint.metadata['resourceName']
    endpoint = aiplatform.Endpoint(endpoint_name)
    pre_prediction_input = '{ "instances": [ '
    post_prediction_input = ' ] } '

    prev_counter = 0
    counter = 0

    while True:
        try:
            rows = BQ_STORAGE_CLIENT.read_rows(session.streams[0].name, offset=counter).rows(session)
            for page in rows.pages:
                df_orig = page.to_dataframe()
                df_orig['entity_type_flows'] = df_orig['flow_id']
                df = df_orig

                X_test = df.drop(['label'], axis=1)
                Y_test = df['label']
                n_classes = 2
                BATCH_SIZE = df_orig.shape[0]

                # counter = 0
                prev_counter = counter
                predictions_0_l = []
                predictions_1_l = []
                y_predicted = []
                predictions_argmax = []
                obj_prediction_input = ''
                temp_counter = 0

                for i in range(0,min(BATCH_SIZE, len(X_test.index)),):
                    pre = '{ '
                    post = ' }, \n'
                    temp = ''
                    for c in X_test.columns:
                        # print(i, end=' ')
                        if c in ['active_mean', 'active_std', 'active_max', 'active_min', 'bwd_iat_mean', 'bwd_iat_std',
                                'bwd_iat_tot', 'bwd_iat_max', 'bwd_iat_min', 'bwd_pkt_len_mean',
                                'bwd_pkt_len_std', 'bwd_pkt_len_max', 'bwd_pkt_len_min', 'bwd_pkts_s',
                                'bwd_seg_size_avg', 'down_up_ratio', 'flow_byts_s', 'flow_iat_mean', 'flow_iat_std',
                                'flow_iat_max',
                                'flow_pkts_s', 'fwd_iat_mean', 'fwd_iat_max', 'flow_iat_min', 'fwd_iat_std',
                                'fwd_iat_tot', 'fwd_iat_min', 'fwd_pkt_len_mean', 'fwd_pkt_len_std',
                                'fwd_pkt_len_max', 'fwd_pkt_len_min', 'fwd_pkts_s', 'fwd_seg_size_avg', 'idle_mean',
                                'idle_std', 'idle_max', 'idle_min',
                                'pkt_len_mean', 'pkt_len_std', 'pkt_len_var', 'pkt_size_avg', 'pkt_len_min',
                                'pkt_len_max', 'totlen_fwd_pkts', 'totlen_bwd_pkts']:
                            if np.isnan(X_test.iloc[i][c]):
                                temp = temp + '"{}": {}, '.format(c, 0)
                            elif np.isinf(X_test.iloc[i][c]):
                                temp = temp + '"{}": {}, '.format(c, 9223372036854775807)
                            else:
                                temp = temp + '"{}": {}, '.format(c, X_test.iloc[i][c])
                        else:
                            temp = temp + '"{}": "{}", '.format(c, X_test.iloc[i][c])

                    temp = pre + temp[:-2] + post
                    obj_prediction_input += temp
                    temp_counter += 1

                prev_counter = counter
                counter += temp_counter

                prediction_input = pre_prediction_input + obj_prediction_input[:-3] + post_prediction_input
                response = endpoint.raw_predict(body=bytes(prediction_input, encoding='utf8'), headers={'Content-Type':'application/json'})
                predictions = json.loads(response.text)
                if 'predictions' in predictions:
                    # print(prediction_input)
                    # print(predictions)
                    y_predicted = [np.argmax(p['scores'], axis=0) for p in predictions['predictions']]
                    # print(predictions['predictions'])
                    # predictions_argmax.extend(y_predicted)
                    for p in predictions['predictions']:
                        # print(p)
                        predictions_0_l.append(p['scores'][0])
                        predictions_1_l.append(p['scores'][1])
                else:
                    print(prediction_input)
                    print(predictions)

                mapping = dict()
                map_count = 0
                for val in predictions.get('predictions')[0].get('classes'):
                    mapping[val] = map_count
                    map_count += 1
                y_test_p = list(Y_test.map(mapping))
                correct = sum(np.array(y_predicted) == np.array(y_test_p))
                total = len(y_predicted)
                print( f"Correct predictions = {correct}, Total predictions = {total}, Accuracy = {correct/total}, Grand Total = {counter}" )

                # df_orig['predict_prob_0'] = pd.Series(predictions_0_l, dtype=np.float64)
                # df_orig['predict_prob_1'] = pd.Series(predictions_1_l, dtype=np.float64)
                df_orig['predict'] = pd.Series(y_predicted, dtype=np.str)
                df_orig['json'] = df_orig.apply(lambda x: x.to_json(), axis=1)
                table_obj = BQ_CLIENT.get_table('{}.{}.{}'.format(project_id, prediction_dataset, prediction_table))

                while True:
                    try:
                        BQ_CLIENT2.insert_rows_from_dataframe(table_obj, df_orig)
                        break
                    except:
                        time.sleep(1)
                        print("Retrying writing to table {}".format('{}.{}.{}'.format(project_id, prediction_dataset, prediction_table)))
                print('Written {} rows to Bigquery'.format(BATCH_SIZE))

                # Post to Pubsub, ddos rows
                try:
                    pred_array = np.array(y_predicted) == np.array(y_test_p)
                    rows = list(page)
                    pcounter = 0
                    while pcounter < len(pred_array):
                        if pred_array[pcounter] == False:
                            resp = PS_CLIENT.publish(topic=TOPIC_NAME, messages=[
                                            pubsub_v1.PubsubMessage(data=json.dumps(rows[pcounter], default=str).encode('utf-8'))])
                            print(resp.message_ids)
                        pcounter += 1
                except Exception as e:
                    print('Error {} posting to Pubsub'.format(str(e)))

            if SOURCE_TABLE_OBJ.num_rows <= counter:
                break
        except Exception as e:
            if 'session expired' in str(e):
                counter -= 400
            else:
                raise e

    print('Predictions written to Bigquery')
