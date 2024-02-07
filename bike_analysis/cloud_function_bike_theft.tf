# Generates an archive of the source code compressed as a .zip file.
data "archive_file" "bike_theft_source" {
  type        = "zip"
  source_dir  = "source/cloud_functions/bike_theft"
  output_path = "${path.module}/bike_theft.zip"
}

# Add source code zip to the Cloud Function's bucket
resource "google_storage_bucket_object" "bike_theft_zip" {
  source       = data.archive_file.bike_theft_source.output_path
  content_type = "application/zip"
  name         = "src-${data.archive_file.bike_theft_source.output_md5}.zip"
  bucket       = google_storage_bucket.cloud_function_data_analysis.name
  depends_on = [
    google_storage_bucket.cloud_function_data_analysis,
    data.archive_file.bike_theft_source
  ]
}

# Create the Cloud function triggered by a `Finalize` event on the bucket
resource "google_cloudfunctions_function" "analysis_bike_theft_tracking" {
  name                  = "analysis-bike-theft-tracking"
  description           = "Function to determine if latest entries in bike trip table should be labeled as theft or stolen bikes."
  runtime               = "python39"
  project               = var.project_id
  region                = var.region
  source_archive_bucket = google_storage_bucketcloud_function_data_analysis.name
  source_archive_object = google_storage_bucket_object.bike_theft_zip.name
  entry_point           = "run_main"
  depends_on = [
    google_storage_bucket.cloud_function_data_analysis,
    google_storage_bucket_object.bike_theft_zip,
  ]
}