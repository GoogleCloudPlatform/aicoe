variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "role_name" {
  description = "Role name roles/abc.xyz"
  type        = string
}

variable "role_names" {
  description = "Role name roles/abc.xyz"
  type        = list(string)
  default     = ["bigquery.metadataViewer", "bigquery.dataEditor"]
}

variable "service_account_email" {
  description = "IAM Service account email"
  type        = string
}
