#!/bin/bash

export PROJECT_ID=${project_id}
export PROJECT_NUMBER=${project_number}
export REGION=${region}
export RANDOM_SUFFIX=${random_suffix}
export NETWORK_SELF_LINK=${network_self_link}
export SUBNET_SELF_LINK=${subnet_self_link}
export SERVICE_ACCOUNT_EMAIL=${service_account_email}
export DDOS_INCIDENTS_TOPIC_NAME=${ddos_incidents_topic_name}
export DDOS_INCIDENTS_TOPIC_ID=${ddos_incidents_topic_id}
export DDOS_TOPIC_NAME=${ddos_topic_name}
export DDOS_TOPIC_ID=${ddos_topic_id}
export COMPOSER_DAG_PATH=${composer_dag_path}
export COMPOSER_BUCKET=${composer_bucket}
export DDOS_BUCKET=${ddos_bucket}
export ENDPOINT_NAME=${endpoint_name}
export ENDPOINT_ID=${endpoint_id}
export MODEL_NAME_PREFIX=${model_name_prefix}
export INFERENCE_TARGET_DATASET="inferenced_${random_suffix}"
export INFERENCE_TARGET_TABLE="ddos_automl_online_predictions_s06"
