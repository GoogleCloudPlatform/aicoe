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

import json
import os
import sys
import logging
import pandas as pd

from envbash import load_envbash

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_path, "..", "..", "utils"))

from gcp_utils import publish_pubsub_messages


def get_logger():
    """Gets a custom logger & set the logging level."""
    logger = logging.getLogger(__name__)
    return logger


def process_data(row):
    """Takes a row as input and returns a JSON equivalent

    Args:
        row (_type_): _description_

    Returns:
        _type_: Returns the data dictionary as a JSON string.
    """
    row = json.loads(row)
    data = {key: str(value) for key, value in row.items()}

    return json.dumps(data)


def main():
    """Publish to PubSub"""
    logger = get_logger()

    env_undef = []
    for env in ["PROJECT_ID", "DDOS_TOPIC_NAME"]:
        if env not in os.environ:
            env_undef.append(env)

    if len(env_undef) > 0:
        logger.error(
            f"The following environment variables are required and not defined: {env_undef}"
        )
        sys.exit()

    project = os.environ.get("PROJECT_ID")
    pubsub_topic = os.environ.get("DDOS_TOPIC_NAME")

    file_loc = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "ddos_sample.csv")
    )

    df = pd.read_csv(file_loc)
    print(df.head(5))
    df["entity_type_flows"] = df["Flow_ID"]
    df["json"] = df.apply(lambda x: x.to_json(), axis=1)

    publish_pubsub_messages(
        project, pubsub_topic, df["json"], process_data, use_pandas=True
    )

main()
