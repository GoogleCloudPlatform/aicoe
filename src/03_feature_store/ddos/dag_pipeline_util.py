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

import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions

# from sys import argv
import logging
import json


def parse_method(keys, timestamp_keys, string_input=None):
    import datetime

    # logging.getLogger().setLevel(logging.INFO)
    # logging.info(f"{keys = }")
    # logging.info(f"{timestamp_keys = }")

    row = dict(zip(keys, string_input))
    # As we are taking datetime as string, thus its not needed.
    # logging.info(f"input row: {row}")
    if timestamp_keys:
        for key in timestamp_keys:
            current_val = row[key]
            ending = ""
            if "/" in current_val:
                date_div = "/"
            else:
                date_div = "-"

            if "." in current_val:
                current_val = current_val.split(".", 1)[0]

            if current_val.lower().endswith("m"):
                ending = " %p"

            if len(current_val.split(date_div, 1)[0]) == 4:
                format_str = f"%Y{date_div}%m{date_div}%d %H:%M:%S{ending}".strip()
            else:
                format_str = f"%d{date_div}%m{date_div}%Y %H:%M:%S{ending}".strip()

            logging.info(f"format_str: {current_val} - {format_str}")
            updated_date = (
                datetime.datetime.strptime(current_val, format_str)
                .replace(tzinfo=None)
                .isoformat()
            )
            logging.info(f"{updated_date = }")
            row[key] = updated_date
    return row


def run(argv=None):
    def get_timestamp_keys(data):
        keys = []
        vals = []
        for d in data.split(","):
            key, val = d.split(":")
            if val.lower() == "timestamp":
                vals.append(key)
            keys.append(key)
        return keys, vals

    from functools import partial

    logging.getLogger().setLevel(logging.INFO)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--op_kwargs", dest="op_kwargs", default="", help="Input file to process."
    )
    known_args, pipelineargs = parser.parse_known_args(argv)
    print(f"{ known_args = }")
    print(f"{ pipelineargs = }")
    print(f"{ dir(known_args) }")
    print(f"{ known_args.op_kwargs = }")
    app_args = json.loads(known_args.op_kwargs.replace("'", '"'))

    BQ_PROJECT = app_args["BQ_PROJECT"]
    BQ_DS = app_args["BQ_DS"]
    GCS_BUCKET = app_args["GCS_BUCKET"]
    GCS_OBJECT_PATH = app_args["GCS_OBJECT_PATH"]
    SOURCE_DATASET = app_args["SOURCE_DATASET"]
    TARGET_TABLE = app_args["TARGET_TABLE"]
    SCHEMA = app_args["SCHEMA"]

    keys, vals = get_timestamp_keys(SCHEMA)
    # logging.info(f"{keys = }")
    # logging.info(f"{vals = }")

    update_parse_method = partial(parse_method, keys, vals)
    with beam.Pipeline(options=PipelineOptions()) as p:
        result = (
            p
            | "ReadData"
            >> beam.io.ReadFromText(
                f"gs://{GCS_BUCKET}/{GCS_OBJECT_PATH}/{SOURCE_DATASET}.csv",
                skip_header_lines=1,
            )
            | "SplitData" >> beam.Map(lambda x: x.split(","))
            | "RemoveNull" >> beam.Map(lambda x: 0 if None else x)
            | "ChangeDataType" >> beam.Map(update_parse_method)
            | "WriteToBigQuery"
            >> beam.io.WriteToBigQuery(
                f"{BQ_PROJECT}:{BQ_DS}.{TARGET_TABLE}",
                schema=SCHEMA,
                create_disposition="CREATE_IF_NEEDED",
                insert_retry_strategy="RETRY_ON_TRANSIENT_ERROR",
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
            )
        )
        logging.info(f"Result: {result}")
    return result
    # result.wait_until_finish()


# if __name__ == '__main__':
logging.getLogger().setLevel(logging.INFO)
run()
