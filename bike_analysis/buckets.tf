####
# Cloud Storage Bucket for storing files and relevant information for the execution of cloud functions within GCP
#
####
resource "google_storage_bucket" "cloud_function_data_analysis" {
    name     = "cloud-function-data-analysis-${var.project_id}"
    location = var.region
    project  = var.project_id
}