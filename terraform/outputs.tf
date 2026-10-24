output "vpc_id" {
  description = "ID du VPC OmniDoc"
  value       = aws_vpc.main.id
}

output "bedrock_private_endpoint_id" {
  description = "ID de l'interface VPC Endpoint PrivateLink vers Bedrock"
  value       = aws_vpc_endpoint.bedrock_runtime.id
}

output "sample_silo_tenant_kms_arn" {
  description = "ARN de la clé KMS CMK dédiée au tenant régulé"
  value       = aws_kms_key.silo_tenant_cmk.arn
}

output "bedrock_guardrail_id" {
  description = "ID du garde-fou Bedrock configuré"
  value       = aws_bedrock_guardrail.contract_guardrail.guardrail_id
}
