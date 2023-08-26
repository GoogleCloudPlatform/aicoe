{
    "PROJECT_ID": "${project_id}",
    "REGION": "${region}",
    "BUCKET_NAME": "${containersec_bucket}",
    "BUCKET_URI": "gs://${containersec_bucket}",
    "SERVICE_ACCOUNT": "${service_account_email}",
    "RUN_FEATURE_STORE_TASK": {
        "PROJECT_ID": "${project_id}",
        "REGION": "${region}",
        "TEMP_DATASET": "batching_${random_suffix}",
        "ONLINE_STORE_FIXED_NODE_COUNT": 1,
        "DESTINATION_DATA_SET": "stg_modeling_${random_suffix}",
        "DESTINATION_TABLE_NAME": "containersec_served_fs",
        "TEMP_SRC_TABLE": "containersec_before_fs",
        "SOURCE_DATASET": "batching_${random_suffix}",
        "SOURCE_TABLE": "containersec",
        "TEMP_FILE_BUCKET": "${containersec_bucket}",
        "TEMP_FILE_PATH": "temp/bqml_feature_store_output.csv",
        "OLD_FEATURE_STORE_NAME": "",
        "NEW_FEATURE_STORE_NAME": "containersec_fs_${random_suffix}"
    },
    "PUBLISH_ANOMALIES_TO_PUBSUB_PARAMS": {
        "PROJECT_NAME": "${project_id}",
        "SOURCE_DATASET": "inferenced_${random_suffix}",
        "SOURCE_TABLE": "containersec_bqml_anomaly_detection",
        "TOPIC_NAME": "${containersec_incidents_topic_name}",
        "TOPIC_ID": "${containersec_incidents_topic_id}"
    },
    "PIPELINE_LAUNCH_PARAMS": {
        "PROJECT_ID": "${project_id}",
        "LOCATION": "US",
        "ANOMALY_DATASET": "inferenced_${random_suffix}",
        "ANOMALY_TABLE": "containersec_bqml_anomaly_detection",
        "SRC_STREAMING_DATASET": "streaming_${random_suffix}",
        "SRC_STREAMING_TABLE": "containersec_streaming_${random_suffix}",
        "MODEL_SOURCE_DATASET": "stg_modeling_${random_suffix}",
        "MODEL_SOURCE_TABLE": "containersec_served_fs",
        "MODEL_TARGET_DATASET": "batching_${random_suffix}",
        "MODEL_TARGET_NAME": "containersec_model_${random_suffix}",
        "CREATE_MODEL_QUERY": "CREATE OR REPLACE MODEL {}.{} OPTIONS(MODEL_TYPE = 'KMEANS', NUM_CLUSTERS = 32, KMEANS_INIT_METHOD = 'KMEANS++', DISTANCE_TYPE = 'COSINE', STANDARDIZE_FEATURES = TRUE, MAX_ITERATIONS = 50, EARLY_STOP = FALSE, WARM_START = FALSE ) AS select parse_timestamp('%Y-%m-%e %T%z', timestamp_s) as timestamp, endpoint, podcount, container_count, tls_enabled, errorcode, latency, is_timeout from `{}.{}.{}` ",
        "GET_DETECT_ANOMALY_DATA": "SELECT * except(timestamp), PARSE_TIMESTAMP('%Y-%m-%d %T', timestamp) as timestamp FROM `{}.{}`"
    }
}
