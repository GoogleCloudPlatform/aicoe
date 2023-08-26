locals {
  templates = {
    "environment.sh"             = "environment.sh.tpl",
    "ddos_settings.json"         = "ddos_settings.json.tpl",
    "containersec_settings.json" = "containersec_settings.json.tpl"
  }
}

data "template_file" "generated" {
  for_each = local.templates

  template = file("${path.module}/templates/${each.value}")
  vars = {
    project_id                    = data.google_project.project.project_id
    project_number                = data.google_project.project.number
    region                        = local.region
    random_suffix                 = local.random_suffix
    network_id                    = data.google_compute_network.composer-vpc.id
    subnetwork_id                 = data.google_compute_subnetwork.composer-subnet.id
    subnetwork_id_without_project = "regions/${local.region}/subnetworks/${data.google_compute_subnetwork.composer-subnet.name}"
    service_account_email         = data.google_service_account.dataflow_sa.email
    ddos_bucket                   = module.cloud-storage.names.ddos
    containersec_bucket           = module.cloud-storage.names.containersec
    composer_dag_path             = google_composer_environment.composer-env.config.0.dag_gcs_prefix
    ddos_incident_topic           = "projects/${data.google_project.project.project_id}/topic/ddos-${local.random_suffix}"
  }
}

resource "local_file" "generated" {
  for_each = local.templates

  content         = data.template_file.generated[each.key].rendered
  filename        = "${path.module}/generated/${each.key}"
  file_permission = 0644
}
