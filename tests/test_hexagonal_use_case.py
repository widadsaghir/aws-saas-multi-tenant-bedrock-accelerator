"""
Tests Unitaires TDD : Cas d'Usage Hexagonal de Bout en Bout
"""
import pytest
from src.domain.models import TenantContext, TenantTier
from src.application.use_cases import AnalyzeContractUseCase
from src.adapters.pii.regex_sanitizer import RegexPiiSanitizerAdapter
from src.adapters.ai.bedrock_mcp_adapter import BedrockMcpAdapter
from src.adapters.repository.in_memory_repository import InMemoryDocumentRepository
from src.adapters.telemetry.opentelemetry_adapter import OpenTelemetryAdapter


def test_analyze_contract_use_case_end_to_end_silo():
    # 1. Composition / Wiring des adaptateurs
    sanitizer = RegexPiiSanitizerAdapter()
    ai_agent = BedrockMcpAdapter()
    repo = InMemoryDocumentRepository()
    telemetry = OpenTelemetryAdapter()

    use_case = AnalyzeContractUseCase(sanitizer, ai_agent, repo, telemetry)

    # 2. Contexte d'un client Santé (Silo)
    tenant = TenantContext(
        tenant_id="tenant-clinique-pasteur",
        tier=TenantTier.SILO,
        kms_key_arn="arn:aws:kms:eu-west-3:111222333444:key/pasteur-cmk"
    )

    raw_contract = (
        "CONTRAT DE PRESTATION. Responsable : Dr. Martin (NIR : 1 82 04 75 042 123 99, email : martin@pasteur.fr). "
        "En cas de retard supérieur à 48 heures, une pénalité de 10% par jour sera prélevée."
    )

    # 3. Exécution du cas d'usage
    result = use_case.execute(
        filename="contrat_maintenance_radiologie.pdf",
        raw_content=raw_contract,
        tenant_context=tenant
    )

    # 4. Vérifications de conformité et d'architecture
    # Vérification A : Résultat d'analyse
    assert result.tenant_id == "tenant-clinique-pasteur"
    assert result.requires_human_review is True  # En raison de la pénalité de 10%
    assert result.overall_risk_score >= 0.40

    # Vérification B : Persistance dans le silo étanche
    persisted_doc = repo.get_document(result.document_id, tenant_id="tenant-clinique-pasteur")
    assert persisted_doc is not None
    assert "[PII_NIR_REDACTED]" in persisted_doc.sanitized_content
    assert "1 82 04 75 042 123 99" not in persisted_doc.sanitized_content

    # Vérification C : Observabilité OpenTelemetry
    spans = telemetry.get_spans_for_tenant("tenant-clinique-pasteur")
    assert len(spans) == 1
    assert spans[0]["step_name"] == "contract_agentic_pipeline"
    assert spans[0]["attributes"]["tier"] == "SILO"
    assert spans[0]["attributes"]["is_isolated_storage"] is True
