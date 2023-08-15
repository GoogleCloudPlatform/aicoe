module "project-services" {
  source  = "terraform-google-modules/project-factory/google//modules/project_services"
  version = "~> 14.1"

  project_id                  = var.project_id
  disable_services_on_destroy = false
  activate_apis               = var.apis_list
}
