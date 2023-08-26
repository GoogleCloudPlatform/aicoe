
# Clean up

All the resources set up need to be deprovisioned to avoid incurring Billing charges.

## Tables of Contents

- [Terraform](#terraform)
- [Other Resources](#other-resources)

All sprints

- [Bootstrap](../00_bootstrap/README.md)
- [Sprint 1 - Realtime Ingestion](../01_realtime_ingestion/README.md)
- [Sprint 2 - Enrichment](../02_enrichment_dataflow/README.md)
- [Sprint 3 - Feature Store](../03_feature_store/README.md)
- [Sprint 4 - Anomaly Detection](../04_anomaly_detection/README.md)
- [Sprint 5 - BQML](../05_bqml/README.md)
- [Sprint 6 - Visualization](../06_visualization/README.md)
- [Clean up](../07_cleanup/README.md) (current)

## Terraform

```Time required: 10 mins```

> :warning: All resources provisioned in past sprints will be destroyed.

1. Destroy resources from each of the Sprints in reverse order [6 through 1]

    For instance

    ```console
    cd ../06_visualization
    terraform destroy -auto-approve
    ```

2. Repeat previous step across other Sprints:

    - [x] `05_bqml`
    - [x] `04_anomaly_detection`
    - [x] `03_feature_store`
    - [x] `02_enrichment_dataflow`
    - [x] `01_realtime_ingestion`
    - [x] `00_bootstrap`

## Other Resources

> :warning: All resources created from past scripts will be deleted.

1. The [utils](../utils/) folder contains shell scripts to delete resources such as DataFlow jobs, Vertex AI models, pipelines, feature store and other assets.

    ```console
    . ./load_environment_sh.sh
    ```

2. Delete resources by executing the shell scripts in sequence.

    ```console
    . ./cancel_dataflow_jobs.sh
    ```

    Try above with other shell scripts `delete_bq_tables_models.sh`, `delete_data_catalog_entries.sh` etc

---
[Previous sprint](../06_visualization/README.md)
