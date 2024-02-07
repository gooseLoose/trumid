terraform {
  backend "gcs" {
    bucket = "citibike-data-analysis-tf-backend"             
  }
}