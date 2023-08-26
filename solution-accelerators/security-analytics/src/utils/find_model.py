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

import sys

from google.cloud import aiplatform_v1

def find_latest_model_with_prefix(project_id: str, location: str, prefix: str) -> list:
    # Create a client
    client_options = {"api_endpoint": f"{location}-aiplatform.googleapis.com"}
    client = aiplatform_v1.ModelServiceClient(client_options=client_options)

    # Initialize request argument(s)
    request = aiplatform_v1.ListModelsRequest(
        parent=f"projects/{project_id}/locations/{location}",
    )

    # Make the request
    page_result = client.list_models(request=request)

    # Handle the response
    responses = [{"name": response.name, "display_name": response.display_name, "create_time": response.create_time} for response in page_result]
    responses_filtered = list(filter(lambda x: x['display_name'].startswith(prefix), responses))
    responses_filtered_sorted = sorted(responses_filtered, key=lambda x: x['create_time'], reverse=True)
    if len(responses_filtered_sorted) > 0:
        return responses_filtered_sorted[0]
    else:
        raise Exception(f"Models starting with prefix {prefix} not found")

if len(sys.argv) < 4:
  print("Usage: find_model.py [project_id] [location] [model_name_prefix]")
else:
  project_id = sys.argv[1]
  location = sys.argv[2]
  model_name_prefix = sys.argv[3]
  print(find_latest_model_with_prefix(project_id, location, model_name_prefix))
