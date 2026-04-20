variable "project_id" {
  description = "GCP project ID (e.g. jekacode-488803)"
  type        = string
}

variable "region" {
  description = "Default region for regional resources"
  type        = string
  default     = "us-central1"
}
