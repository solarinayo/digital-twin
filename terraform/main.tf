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

data "google_project" "project" {
  project_id = var.project_id
}

# OpenAI key: value is never stored in Terraform. Add versions with CI or `gcloud secrets versions add`.
resource "google_secret_manager_secret" "openai_api_key" {
  project   = var.project_id
  secret_id = "openai-api-key"

  replication {
    auto {}
  }

  depends_on = [google_project_service.apis]
}

# Cloud Run (default runtime SA) reads the secret at instance startup as env OPENAI_API_KEY.
resource "google_secret_manager_secret_iam_member" "openai_runtime_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
}
