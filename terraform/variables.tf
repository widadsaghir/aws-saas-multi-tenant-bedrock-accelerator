variable "aws_region" {
  description = "Région souveraine AWS"
  type        = string
  default     = "eu-west-3"
}

variable "environment" {
  description = "Environnement de déploiement"
  type        = string
  default     = "production"
}

variable "vpc_cidr" {
  description = "Plage IP CIDR du VPC OmniDoc"
  type        = string
  default     = "10.100.0.0/16"
}

variable "sample_tenant_id" {
  description = "Identifiant d'un locataire régulé pour la clé KMS CMK"
  type        = string
  default     = "tenant-clinique-pasteur"
}
