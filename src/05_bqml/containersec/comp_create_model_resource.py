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
from kfp.v2.dsl import Input, component, Artifact, Output

with open("../generated/containersec_settings.json") as config:
    containersec_settings = json.load(config)
    
    
def create_model_resource_bqml(bqml_model_id: str, model: Output[Artifact]):
    from google.cloud import bigquery

    # Construct a BigQuery client object.
    client = bigquery.Client()
    model = client.get_model(bqml_model_id)  # Make an API request.

    full_model_id = "{}.{}.{}".format(model.project, model.dataset_id, model.model_id)
    friendly_name = model.friendly_name
    print(model)
    print(
        "Got model '{}' with friendly_name '{}'.".format(full_model_id, friendly_name)
    )
    model.metadata['resourceName'] = model.uri

create_model_resource_bqml("{0}.{1}.{2}".format(containersec_settings['PROJECT_ID'],
                                                containersec_settings['SOURCE_DATASET'],
                                                containersec_settings['MODEL_TARGET_NAME']), None)
