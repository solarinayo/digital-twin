provider "google" {
  project = var.project_id
  region  = var.region
}

# APIs required for Cloud Run deploys and Artifact Registry (CI pushes images here).
locals {
  services = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "iam.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.services)

  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# Docker repository used by GitHub Actions to push images before Cloud Run deploy.
resource "google_artifact_registry_repository" "digital_twin" {
  location      = var.region
  repository_id = "digital-twin"
  description   = "Container images for the Digital Twin (FastAPI)"
  format        = "DOCKER"

  depends_on = [google_project_service.apis]
}
