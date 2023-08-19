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

import datetime
import json
import os
import random
import time
import pandas as pd

ENDPOINT = [
    "web_niagara",
    "web_angel",
    "web_iguazu",
    "web_victoria",
    "web_yosemite",
    "web_sutherland",
    "web_bangloc",
    "app_tugela",
    "app_jog",
    "app_rhine",
    "app_gocta",
    "app_palouse",
    "app_havasu",
    "app_browne",
    "app_yumbilla",
    "app_bridalveil",
    "app_dudhsagar",
    "data_proxysql",
]
PODCOUNT = [1, 2, 3, 4, 5, 6, 7, 8]
CONTAINERCOUNT = [1, 2]
TLS_ENABLED = [0, 1]

ERRORCODE = [
    200,
    201,
    202,
    205,
    300,
    301,
    302,
    400,
    401,
    403,
    500,
    502,
    504,
]

LATENCY_MS = [10, 3000]

ISTIMEOUT = [0, 1]

d = []
current = datetime.datetime(2022, 9, 20, 13, 00)
tmp_path = os.path.abspath(os.path.join("..", "generated"))
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)

file_name = os.path.join(tmp_path, "containersec_sample.json")

print(f"writing to {file_name}")
with open(file_name, "w") as outfile:
    for i in range(1, 50):
        errorcode = random.choice(ERRORCODE)
        if errorcode < 300:
            data = {
                "timestamp": str(
                    current + datetime.timedelta(minutes=random.randrange(i))
                ),
                "endpoint": random.choice(ENDPOINT),
                "podcount": random.choice(PODCOUNT),
                "container_count": 2,
                "tls_enabled": 1,
                "errorcode": errorcode,
                "latency": float(random.randrange(10, 150)),
                "is_timeout": 0,
            }
        else:
            data = {
                "timestamp": str(
                    current + datetime.timedelta(minutes=random.randrange(i))
                ),
                "endpoint": random.choice(ENDPOINT),
                "podcount": int(random.randrange(8, 9)),
                "container_count": 2,
                "tls_enabled": random.choice(TLS_ENABLED),
                "errorcode": errorcode,
                "latency": float(random.randrange(150, 3000)),
                "is_timeout": random.choice(ISTIMEOUT),
            }
        outfile.write(json.dumps(data))
        outfile.write("\n")
