{
    "model": {
        "displayName": "${model_name}-uploaded",
        "predictSchemata": {
            "instanceSchemaUri": "${model_upload_location}/instance.yaml",
            "predictionSchemaUri": "${model_upload_location}/prediction_schema.yaml"
        },
        "containerSpec": {
            "imageUri": "us-docker.pkg.dev/vertex-ai/automl-tabular/prediction-server:20221020_1325_RC00",
            "predictRoute": "/predict",
            "healthRoute": "/health"
        },
        "supportedDeploymentResourcesTypes": [
           "DEDICATED_RESOURCES"
        ],
        "artifactUri": "${model_upload_location}"
    }
}
