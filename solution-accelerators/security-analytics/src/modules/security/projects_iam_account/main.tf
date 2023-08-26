
resource "google_project_iam_member" "cloudservices-account" {
  project = var.project_id
  role    = "roles/${var.role_name}"
  member  = "serviceAccount:${var.service_account_email}"
}
