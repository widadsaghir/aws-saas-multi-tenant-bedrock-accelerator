"""
Tests Unitaires TDD : Adaptateur Amazon Bedrock & Protocole MCP
"""
import pytest
from src.domain.models import TenantContext, TenantTier
from src.adapters.ai.bedrock_mcp_adapter import BedrockMcpAdapter


def test_bedrock_mcp_detects_high_risk_penalties():
    adapter = BedrockMcpAdapter()
    tenant = TenantContext(tenant_id="t-law-firm", tier=TenantTier.SILO)
    
    content = "En cas de retard, une pénalité de 10% par jour calendaire sera exigée sans mise en demeure préalable."
    result = adapter.analyze_document(content, tenant, tools=["clause_risk_analyzer"])

    assert result.requires_human_review is True
    assert result.overall_risk_score >= 0.40
    assert any(c.title == "Pénalités de Retard" and c.risk_level == "HIGH" for c in result.detected_clauses)


def test_bedrock_mcp_detects_compliant_standard_clauses():
    adapter = BedrockMcpAdapter()
    tenant = TenantContext(tenant_id="t-startup", tier=TenantTier.POOL)

    content = "Limitation de responsabilité plafonnée aux montants payés au titre des 12 derniers mois. Traitement des données conforme au RGPD."
    result = adapter.analyze_document(content, tenant, tools=["clause_risk_analyzer", "regulatory_compliance_checker"])

    assert result.requires_human_review is False
    assert result.overall_risk_score < 0.15
    assert len(result.detected_clauses) >= 2
