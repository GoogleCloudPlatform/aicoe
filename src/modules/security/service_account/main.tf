
resource "google_project_iam_member" "gserviceaccount" {
  project = var.project_id
  role    = "roles/${var.role_name}"
  member  = "serviceAccount:service-${var.service_account_email}"
}