"""
Tests Unitaires TDD : Modèles du Domaine (DDD)
"""
import pytest
from src.domain.models import TenantContext, TenantTier, ContractAnalysisResult, Clause


def test_tenant_context_silo_isolation():
    context = TenantContext(
        tenant_id="tenant-clinic-paris",
        tier=TenantTier.SILO,
        kms_key_arn="arn:aws:kms:eu-west-3:123456789012:key/cmk-tenant-clinic"
    )
    assert context.is_isolated_storage() is True
    assert context.tier == TenantTier.SILO


def test_tenant_context_pool_shared():
    context = TenantContext(
        tenant_id="tenant-sme-lyon",
        tier=TenantTier.POOL
    )
    assert context.is_isolated_storage() is False
    assert context.tier == TenantTier.POOL


def test_contract_analysis_auto_approval_policy():
    # Cas 1 : Faible risque, pas de révision humaine requise -> Approbation automatique
    compliant_result = ContractAnalysisResult(
        analysis_id="a1",
        tenant_id="t1",
        document_id="d1",
        overall_risk_score=0.08,
        detected_clauses=[],
        requires_human_review=False,
        tokens_consumed=420,
        inference_latency_ms=150.0
    )
    assert compliant_result.is_compliant_for_auto_approval() is True

    # Cas 2 : Risque élevé (> 0.15) ou révision humaine requise -> Pas d'approbation auto
    risky_result = ContractAnalysisResult(
        analysis_id="a2",
        tenant_id="t2",
        document_id="d2",
        overall_risk_score=0.45,
        detected_clauses=[Clause(clause_id="c1", title="Pénalités", content="10% par jour", risk_level="HIGH")],
        requires_human_review=True,
        tokens_consumed=650,
        inference_latency_ms=210.0
    )
    assert risky_result.is_compliant_for_auto_approval() is False
