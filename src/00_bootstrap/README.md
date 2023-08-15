
# Solution Accelerator for Security Analytics

This is the first step that creates the foundational infrastructure needs for the remaining sprints.

## Tables of Contents

- [Solution Accelerator for Security Analytics](#solution-accelerator-for-security-analytics)
  - [Tables of Contents](#tables-of-contents)
  - [Prerequisites](#prerequisites)
  - [Bootstrap](#bootstrap)
    - [Overview](#overview)
    - [Steps](#steps)
    - [Exit criteria / e2e validation](#exit-criteria--e2e-validation)
    - [Resources created](#resources-created)

All sprints

- [Bootstrap](../00_bootstrap/README.md) (current)
- [Sprint 1 - Realtime Ingestion](../01_realtime_ingestion/README.md)
- [Sprint 2 - Enrichment](../02_enrichment_dataflow/README.md)
- [Sprint 3 - Feature Store](../03_feature_store/README.md)
- [Sprint 4 - Anomaly Detection](../04_anomaly_detection/README.md)
- [Sprint 5 - BQML](../05_bqml/README.md)
- [Sprint 6 - Visualization](../06_visualization/README.md)

## Prerequisites

```Time required: 10 mins```

- [x] [Empty Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- [x] [Python 3](https://cloud.google.com/python/docs/setup)
- [x] [Virtual Environment](https://cloud.google.com/python/docs/setup#installing_and_using_virtualenv)
- [x] [gcloud CLI](https://cloud.google.com/sdk/docs/install-sdk) (not required if using Cloud shell)
- [x] [Terraform](https://developer.hashicorp.com/terraform/tutorials/gcp-get-started/install-cli)

## Bootstrap

```Time required: 5 mins```

```Cost: $0 (part of free-tier)```

### Overview

The bootstrap phase initializes the Google Cloud project, terraform state bucket, and configures the terraform backends for each sprint.

- [x] Create a terraform state bucket `gs://tf-state-<DEST_PROJECT>`
- [x] Enable the services required for the solution accelerator
- [x] Populates `generated/environment.sh` with the basic environment variables
- [x] Populates `<SPRINT FOLDER>/backend.auto.tf` in every sprint folder

### Steps

1. Checkout the code (External)

    ```console
    git clone https://github.com/GoogleCloudPlatform/security-analytics-accelerators.git
    cd security-analytics-accelerators/src
    ```

2. Authenticate Google Cloud CLI to Google Cloud (gcloud)

    ```console
    gcloud auth login
    gcloud auth application-default login
    gcloud config set project [project name]
    ```

3. Create a virtual environment for Python

    ```console
    python3 -m venv ~/venv-solacc
    source ~/venv-solacc/bin/activate
    ```

4. Initialize the environment

    ```console
    cd 00_bootstrap
    sh setup.sh
    ```

5. Provision the infrastructure using Terraform

    ```console
    terraform init 
    terraform plan -var-file=terraform.tfvars
    terraform apply -var-file=terraform.tfvars --auto-approve
    ```

    **Validate**: Terraform finishes successfully.

    ```console
    $ terraform apply -var-file=terraform.tfvars --auto-approve
    Apply complete! Resources: X added, Y changed, 0 destroyed.
    ```

### Exit criteria / e2e validation

1. Terraform finishes successfully, no resources changed after the second run

    ```console
    $ terraform apply -var-file=terraform.tfvars --auto-approve
    Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
    ```

### Resources created

The following resources are created in your Google Cloud Project.

| # | Resource | Purpose |
|---|---|---|
| 1 | Cloud Storage Bucket | A Bucket where Terraform stores its state data files |
| 2 | Cloud APIs | APIs used for different services |

---
[Next sprint](../01_realtime_ingestion/README.md)
