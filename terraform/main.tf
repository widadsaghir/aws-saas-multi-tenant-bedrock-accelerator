# ==============================================================================
# OmniDoc AWS SaaS Accelerator - Infrastructure as Code (Terraform)
# Architecture Multi-Tenant Hybride & Enclave Souveraine Amazon Bedrock
# Région : eu-west-3 (Paris)
# ==============================================================================

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "OmniDoc-SaaS-Accelerator"
      ManagedBy   = "Terraform"
      Environment = var.environment
    }
  }
}

# 1. AWS KMS : Clé Maîtresse Client (CMK) par Tenant Régulé (Silo Tier)
resource "aws_kms_key" "silo_tenant_cmk" {
  description             = "KMS CMK dédiée pour le chiffrement des données du tenant régulé"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  tags = {
    TenantId   = var.sample_tenant_id
    Tier       = "SILO"
    Compliance = "HDS_RGPD"
  }
}

resource "aws_kms_alias" "silo_tenant_alias" {
  name          = "alias/omnidoc-silo-${var.sample_tenant_id}"
  target_key_id = aws_kms_key.silo_tenant_cmk.key_id
}

# 2. VPC & Sous-Réseaux Isolés (eu-west-3)
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "omnidoc-saas-vpc"
  }
}

# 3. AWS PrivateLink : VPC Endpoint Privé vers Amazon Bedrock (Zéro Internet)
resource "aws_security_group" "bedrock_endpoint_sg" {
  name        = "omnidoc-bedrock-endpoint-sg"
  description = "Autorise le trafic HTTPS depuis le cluster EKS vers Amazon Bedrock"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc_endpoint" "bedrock_runtime" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_region}.bedrock-runtime"
  vpc_endpoint_type   = "Interface"
  security_group_ids  = [aws_security_group.bedrock_endpoint_sg.id]
  private_dns_enabled = true

  tags = {
    Name = "omnidoc-bedrock-runtime-endpoint"
  }
}

# 4. Amazon Bedrock Guardrail : Garde-Fou de Sécurité et Détection PII
resource "aws_bedrock_guardrail" "contract_guardrail" {
  name        = "omnidoc-contract-guardrail"
  description = "Intercepte le prompt injection, le jailbreak et bloque les fuites de données"

  blocked_input_messaging  = "Requête bloquée par les politiques de conformité contractuelle OmniDoc."
  blocked_outputs_messaging = "Réponse masquée par les gardes-fous de protection juridique."

  content_policy_config {
    filters_config {
      type            = "PROMPT_ATTACK"
      input_strength  = "HIGH"
      output_strength = "NONE"
    }
  }

  sensitive_information_policy_config {
    pii_entities_config {
      type   = "EMAIL"
      action = "ANONYMIZE"
    }
    pii_entities_config {
      type   = "PHONE"
      action = "ANONYMIZE"
    }
  }
}
