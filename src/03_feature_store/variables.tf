variable "datasets" {
  type = list(string)
}

variable "bucket_names" {
  type = list(string)
}

variable "bucket_names_force_destroy" {
  type = map(string)
}
