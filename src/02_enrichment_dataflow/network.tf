/*
 Copyright 2023 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 */

resource "google_compute_network" "composer-vpc" {
  name                    = "bq-sec-composer-vpc-${local.random_suffix}"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "composer-subnet" {
  name                     = "bq-sec-composer-subnetwork-${local.random_suffix}"
  ip_cidr_range            = "10.2.0.0/16"
  region                   = data.terraform_remote_state.bootstrap.outputs.region
  network                  = google_compute_network.composer-vpc.id
  private_ip_google_access = true
}

resource "google_compute_firewall" "allow-internal" {
  name = "allow-internal-${local.random_suffix}"

  allow {
    protocol = "all"
  }
  direction   = "INGRESS"
  description = "Allow rfc1918 ranges"
  network     = google_compute_network.composer-vpc.id
  priority    = 1000
  source_ranges = [
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16"
  ]
}

resource "google_compute_router" "custom-router" {
  name    = "router-${local.random_suffix}"
  region  = data.terraform_remote_state.bootstrap.outputs.region
  network = google_compute_network.composer-vpc.id

  bgp {
    asn = 64514
  }
}

# static external IP addresses for NAT
resource "google_compute_address" "nat_cusotm_ips" {
  count  = 2
  name   = "ip-${count.index}-${local.random_suffix}"
  region = google_compute_router.custom-router.region
}

resource "google_compute_router_nat" "custom-nat" {
  name                               = "nat-${local.random_suffix}"
  router                             = google_compute_router.custom-router.name
  region                             = google_compute_router.custom-router.region
  nat_ip_allocate_option             = "MANUAL_ONLY"
  nat_ips                            = google_compute_address.nat_cusotm_ips.*.self_link
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}
