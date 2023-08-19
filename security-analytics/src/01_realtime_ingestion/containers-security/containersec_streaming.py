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

import os
import sys

from envbash import load_envbash

load_envbash("../generated/environment.sh")

current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(current_path, "..", "..", "utils"))
from gcp_utils import publish_pubsub_messages


def get_project_id():
    """Get GCP project ID from generated environment sh

    Returns:
        string: project_id
    """
    project_id = os.getenv("PROJECT_ID")
    if project_id is None:
        print(
            "Unable to find environment variable: PROJECT_ID. \
        Please run the environment.sh file again"
        )
    print(f"PROJECT_ID={project_id}")
    return project_id


def get_topic_id():
    """Get PubSub topics ID from generated environment sh

    Returns:
        string: topic_id
    """
    topic_id = os.getenv("PUBSUB_TOPIC_CONTAINERSEC_NAME")
    if topic_id is None:
        print(
            "Unable to find environment variable: PUBSUB_TOPIC_CONTAINERSEC_NAME. \
          Please run the environment.sh file again"
        )
    print(f"TOPIC_ID={topic_id}")
    return topic_id


def get_file_loc(current_path):
    """Get File location

    Args:
        current_path (_type_): current originating path of exec code

    Returns:
        _type_: _description_
    """
    file_loc = os.path.abspath(
        os.path.join(current_path, "..", "generated", "containersec_sample.json")
    )

    return file_loc


def publish_messages(current_path):
    """Publish message to PubSub

    Args:
        current_path (_type_): current originating path of exec code
    """
    project_id = get_project_id()
    topic_id = get_topic_id()
    file_loc = get_file_loc(current_path)

    publish_pubsub_messages(project_id, topic_id, file_loc)


publish_messages(current_path)
