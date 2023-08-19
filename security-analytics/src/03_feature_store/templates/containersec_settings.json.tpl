{
  "PROJECT_ID": "${project_id}",
  "REGION": "${region}",
  "BUCKET_NAME": "${containersec_bucket}",
  "BUCKET_URI": "gs://${containersec_bucket}",
  "SERVICE_ACCOUNT": "${service_account_email}",
  "RUN_FEATURE_STORE_TASK": {
      "RANDOM_SUFFIX": "${random_suffix}",
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
      "TEMP_FILE_PATH": "temp/feature_store_output_bqml.csv",
      "OLD_FEATURE_STORE_NAME": "",
      "NEW_FEATURE_STORE_NAME": "containersec_fs_${random_suffix}"
  }
}
