variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "apis_list" {
  description = "List of APIs to be managed"
  type        = list(string)
  default = [
    "aiplatform.googleapis.com",
    "bigquery.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "composer.googleapis.com",
    "compute.googleapis.com",
    "datacatalog.googleapis.com",
    "dataflow.googleapis.com",
    "datastream.googleapis.com",
    "iam.googleapis.com",
    "sourcerepo.googleapis.com",
  ]
}
