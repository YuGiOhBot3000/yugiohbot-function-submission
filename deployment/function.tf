resource "google_cloudfunctions_function" "function" {
  name        = var.function_title
  description = var.function_description
  runtime     = var.function_runtime

  available_memory_mb   = 256
  source_archive_bucket = google_storage_bucket.bucket.name
  source_archive_object = google_storage_bucket_object.function.name
  timeout               = 60

  entry_point   = var.entry_point
  trigger_http  = true
}
