module "cloud-storage" {
  source  = "terraform-google-modules/cloud-storage/google"
  version = "3.4.1"
  # insert the 3 required variables here
  project_id       = data.google_project.project.project_id
  storage_class    = "REGIONAL"
  names            = var.bucket_names
  prefix           = "ml-sec-${local.random_suffix}"
  randomize_suffix = false
  location         = local.region
  force_destroy    = var.bucket_names_force_destroy
}

resource "google_composer_environment" "composer-env" {
  project = data.google_project.project.project_id
  name    = "airflow2-${local.random_suffix}"
  region  = local.region

  config {
    private_environment_config {
      enable_private_endpoint = false
    }

    software_config {
      image_version = "composer-2-airflow-2"
      pypi_packages = {
        apache-airflow-providers-google      = ""
        apache-airflow-providers-apache-beam = ""

      }
      env_variables = {
        PROJECT          = data.google_project.project.project_id
        ddos_bucket_name = module.cloud-storage.names.ddos
        syn_bucket_name  = module.cloud-storage.names.syn
      }
    }
    environment_size = "ENVIRONMENT_SIZE_SMALL"

    node_config {
      network         = data.google_compute_network.composer-vpc.id
      subnetwork      = data.google_compute_subnetwork.composer-subnet.id
      service_account = data.google_service_account.dataflow_sa.name
    }
  }
}

resource "google_storage_bucket_object" "containersec_object" {
  name   = "data/containersec.json"
  source = "data/containersec.json"
  bucket = module.cloud-storage.names.containersec
}

resource "google_storage_bucket_object" "ddos_dag_pipeline_util_object" {
  name   = "dag_pipeline_util.py"
  source = "ddos/dag_pipeline_util.py"
  bucket = module.cloud-storage.names.ddos
}

resource "google_storage_bucket_object" "ddos_settings_object" {
  depends_on = [local_file.generated["ddos_settings.json"]]

  name   = "ddos_settings.json"
  source = "generated/ddos_settings.json"
  bucket = module.cloud-storage.names.ddos
}

resource "google_storage_bucket_object" "ddos_object" {
  name   = "data/ddos.csv"
  source = "data/ddos.csv"
  bucket = module.cloud-storage.names.ddos
}

resource "google_storage_bucket_object" "dag_ddos" {
  name   = "dags/dag_ddos.py"
  source = "ddos/dag_ddos.py"
  bucket = replace(replace(google_composer_environment.composer-env.config.0.dag_gcs_prefix, "gs://", ""), "/dags", "")
}
