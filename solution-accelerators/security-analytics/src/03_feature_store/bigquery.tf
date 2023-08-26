resource "google_bigquery_dataset" "dataset" {
  for_each = toset(var.datasets)

  dataset_id    = "${each.value}_${local.random_suffix}"
  friendly_name = "${each.value}_${local.random_suffix}"
  description   = "${each.value}_${local.random_suffix}"
  location      = "US"
  project       = data.google_project.project.project_id
  labels        = local.labels_map
}

resource "google_bigquery_table" "containersec" {
  dataset_id          = google_bigquery_dataset.dataset["batching"].dataset_id
  table_id            = "containersec"
  deletion_protection = false
  project             = data.google_project.project.project_id
  labels              = local.labels_map
}

resource "google_bigquery_job" "containersec_load" {
  job_id  = "containersec_job_load_${local.random_suffix}"
  project = data.google_project.project.project_id

  labels = {
    "my_job" = "load"
  }

  load {
    source_uris = [
      "gs://${module.cloud-storage.names.containersec}/${google_storage_bucket_object.containersec_object.name}",
    ]

    destination_table {
      project_id = data.google_project.project.project_id
      dataset_id = google_bigquery_dataset.dataset["batching"].dataset_id
      table_id   = google_bigquery_table.containersec.table_id
    }

    autodetect    = true
    source_format = "NEWLINE_DELIMITED_JSON"
  }
}
