provider "google" {
  project     = "yugiohbot"
  region      = "us-east1"
  zone        = "us-east1-a"
}

terraform {
  backend "gcs" {
    bucket      = "yugiohbot-tf-state"
    prefix      = "submission"
    credentials = "~/account.json"
  }
}
