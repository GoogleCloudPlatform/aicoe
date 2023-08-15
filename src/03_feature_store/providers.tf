terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.58.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "4.57.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.4.3"
    }
  }
}

provider "google-beta" {
  project = data.terraform_remote_state.bootstrap.outputs.project_id
  region  = data.terraform_remote_state.bootstrap.outputs.region
  zone    = data.terraform_remote_state.bootstrap.outputs.zone
}

provider "google" {
  project = data.terraform_remote_state.bootstrap.outputs.project_id
  region  = data.terraform_remote_state.bootstrap.outputs.region
  zone    = data.terraform_remote_state.bootstrap.outputs.zone
}
