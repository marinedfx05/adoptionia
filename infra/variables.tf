variable "region" {
  default = "eu-north-1"
}

variable "bucket_name" {
  default = "adoptionia-prod-md" # unique au monde
}

variable "my_ip" {
  description = "Votre adresse IP publique, seule autorisée en SSH"
}

