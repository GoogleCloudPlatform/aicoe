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
from google.api_core.exceptions import NotFound

@component(
    packages_to_install=["google-cloud-bigquery"],
    base_image="python:3.9",
)
def delete_inference_table(table_id: str):
    from google.cloud import bigquery
    from google.api_core.exceptions import NotFound

    client = bigquery.client.Client()
    try:
        client.delete_table(table_id)
    except NotFound:
        print(f"Table does not exist: {table_id}")
    except Exception as ex:
        print(f"Failed to delete table: {table_id}")
        raise ex


@component(
    packages_to_install=[
        "google-cloud-pubsub==2.13.11",
        "google-cloud-bigquery==2.34.4",
        "google-cloud-bigquery-storage==2.7.0",
        "google-cloud-bigquery-storage[fastavro]",
    ],
    base_image="python:3.9",
)
def publish_anomalies_to_pubsub(destination_table: Input[Artifact], params: dict):
    import json
    from google.cloud import bigquery
    from google import pubsub_v1
    from google.cloud.bigquery_storage import BigQueryReadClient
    from google.cloud.bigquery_storage import types

    SOURCE_DATASET = destination_table.metadata["datasetId"]
    SOURCE_TABLE = destination_table.metadata["tableId"]
    PROJECT_NAME = params['PROJECT_NAME']
    TOPIC_ID = params['TOPIC_ID']

    BQ_STORAGE_CLIENT = BigQueryReadClient()
    BQ_CLIENT = bigquery.client.Client()
    PS_CLIENT = pubsub_v1.PublisherClient()

    requested_session = types.ReadSession()
    requested_session.table = (
        f"projects/{PROJECT_NAME}/datasets/{SOURCE_DATASET}/tables/{SOURCE_TABLE}"
    )
    requested_session.data_format = types.DataFormat.AVRO

    table_obj = BQ_CLIENT.get_table(f"{PROJECT_NAME}.{SOURCE_DATASET}.{SOURCE_TABLE}")
    session = BQ_STORAGE_CLIENT.create_read_session(
        parent=f"projects/{PROJECT_NAME}",
        read_session=requested_session,
        max_stream_count=1,
    )

    counter = 0
    while True:
        try:
            rows = BQ_STORAGE_CLIENT.read_rows(
                session.streams[0].name, offset=counter
            ).rows(session)
            for row in rows:
                # print(json.dumps(row, default=str))
                if row["is_anomaly"]:
                    resp = PS_CLIENT.publish(
                        topic=TOPIC_ID,
                        messages=[
                            pubsub_v1.PubsubMessage(
                                data=json.dumps(row, default=str).encode("utf-8")
                            )
                        ],
                    )
                    print(resp.message_ids)
                counter += 1

            if counter == table_obj.num_rows:
                break
        except Exception as ex:
            if "session expired" in str(ex):
                print(str(ex))
                counter -= 400
            else:
                print(str(ex))
                raise ex
