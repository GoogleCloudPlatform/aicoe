# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import json 
import logging

from concurrent import futures
# from collections.abc import Callable
from typing import Callable
import pandas 

from google.cloud import pubsub_v1


# get a custom logger & set the logging level
py_logger = logging.getLogger(__name__)
py_logger.setLevel(logging.INFO)

# configure the handler and formatter as needed
current_path = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(current_path, "..", "..", "logs")
if os.path.exists(log_dir) == False:
    os.makedirs(log_dir)

logpath = os.path.abspath(os.path.join(log_dir, f"{os.path.basename(__file__)}.log"))
py_handler = logging.FileHandler(logpath)
py_formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")

# add formatter to the handler
py_handler.setFormatter(py_formatter)
# add handler to the logger
py_logger.addHandler(py_handler)

def deduce_project_id():
    """
    We will try to deduce the project_id from the following env variables
    - PROJECT_ID
    - GCP_PROJECT
    - GOOGLE_APPLICATION_CREDENTIALS
    - DEVSHELL_PROJECT_ID (if we are running the script through cloud shell)
    """
    for env_val in ('PROJECT_ID',  'GCP_PROJECT', 'DEVSHELL_PROJECT_ID'):
        if env_val in os.environ:
            return os.getenv(env_val, None)

    if 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
        with open(os.environ['GOOGLE_APPLICATION_CREDENTIALS'], 'r') as fp:
            credentials = json.load(fp)
            print(f"{credentials = }")
        return credentials.get('project_id', None)
    else:
        py_logger.error('Failed to determine project_id')
        return None
    


def publish_pubsub_messages(project_id: str, topic_id: str, data_file: str, key=None, use_pandas=False):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    publish_futures = []

    def get_callback(
        publish_future: pubsub_v1.publisher.futures.Future, data: str
    ) -> Callable[[pubsub_v1.publisher.futures.Future], None]:
        def callback(publish_future: pubsub_v1.publisher.futures.Future) -> None:
            try:
                # Wait 60 seconds for the publish call to succeed.
                py_logger.info(publish_future.result(timeout=60))
            except futures.TimeoutError:
                py_logger.exception(f"Publishing {data} timed out.")

        return callback

    if use_pandas:
        for row in data_file:  # .tolist()
            row = key(row)
            py_logger.info(row)
            publish_future = publisher.publish(topic_path, row.encode("utf-8"))
            # Non-blocking. Publish failures are handled in the callback function.
            publish_future.add_done_callback(get_callback(publish_future, row))
            publish_futures.append(publish_future)
    else:
        with open(data_file) as fp:
            for data in fp:
                # print(data)
                if key:
                    data = key(data)
                publish_future = publisher.publish(topic_path, data.encode("utf-8"))
                # Non-blocking. Publish failures are handled in the callback function.
                publish_future.add_done_callback(get_callback(publish_future, data))
                publish_futures.append(publish_future)

    # Wait for all the publish futures to resolve before exiting.
    futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)

def get_terraform_output(folder, location=None):
    import subprocess
    import json 
    command = ['terraform', "output", '--json']
    proc = subprocess.Popen(command, cwd=folder,
                            stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    if not err:
        data = json.loads(str(out.decode('ascii')))
        return data
    return None

    # print(out, err)
    # from subprocess import Popen, PIPE
    # process = Popen(['terraform', "output", '--json'],  cwd=folder)
    # stdout, stderr = process.communicate()
    # print(f"{stdout = },{stderr = }")
    # import os

    # home_dir = os.system(f"cd {folder} && terraform output --json")
    # print(f"{home_dir = }")