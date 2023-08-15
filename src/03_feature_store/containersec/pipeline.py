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


import kfp

from uuid import uuid4

from component import run_feature_store_task


UUID = str(uuid4())


@kfp.dsl.pipeline(name=f"s03-containersec_run_feature_store-{UUID}")
def pipeline(
    run_feature_store_task_params: dict
):
    run_fs_task = run_feature_store_task(run_feature_store_task_params)
