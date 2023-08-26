output "bucket_names" {
  value = module.cloud-storage.names
}

output "composer_bucket" {
  value = replace(replace(google_composer_environment.composer-env.config.0.dag_gcs_prefix, "gs://", ""), "/dags", "")
}

output "composer_dag_path" {
  value = google_composer_environment.composer-env.config.0.dag_gcs_prefix
}

output "datasets" {
  value = [
    for ds in google_bigquery_dataset.dataset : ds.dataset_id
  ]
}
