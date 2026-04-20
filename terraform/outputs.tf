output "artifact_registry_repository" {
  description = "Artifact Registry repo name"
  value       = google_artifact_registry_repository.digital_twin.name
}

output "docker_image_prefix" {
  description = "Prefix for docker push (region-docker.pkg.dev/project/repo)"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.digital_twin.repository_id}"
}

output "openai_secret_id" {
  description = "Secret Manager id for OpenAI key (mount as OPENAI_API_KEY in Cloud Run)"
  value       = google_secret_manager_secret.openai_api_key.secret_id
}
