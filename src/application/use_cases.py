"""
Application Use Cases - Orchestration de la Logique Métier
"""
import uuid
import time
from src.domain.models import DocumentEntity, ContractAnalysisResult, TenantContext
from src.domain.ports import (
    PiiSanitizerPort,
    AiAgentPort,
    DocumentRepositoryPort,
    AuditTelemetryPort,
)


class AnalyzeContractUseCase:
    """
    Cas d'usage maître :
    1. Réception du document et du contexte tenant.
    2. Caviardage local PII (0 token) pour garantir le secret médical/juridique.
    3. Persistance du document (Silo/Pool).
    4. Inférence agentique souveraine via MCP (Bedrock).
    5. Enregistrement des traces OpenTelemetry pour observabilité en production.
    """

    def __init__(
        self,
        sanitizer: PiiSanitizerPort,
        ai_agent: AiAgentPort,
        repository: DocumentRepositoryPort,
        telemetry: AuditTelemetryPort,
    ):
        self.sanitizer = sanitizer
        self.ai_agent = ai_agent
        self.repository = repository
        self.telemetry = telemetry

    def execute(
        self,
        filename: str,
        raw_content: str,
        tenant_context: TenantContext,
    ) -> ContractAnalysisResult:
        start_time = time.time()
        doc_id = str(uuid.uuid4())

        # 1. Dé-identification PII locale stricte (0 Token)
        sanitized_content = self.sanitizer.sanitize(raw_content)

        document = DocumentEntity(
            document_id=doc_id,
            tenant_context=tenant_context,
            filename=filename,
            raw_content=raw_content,
            sanitized_content=sanitized_content,
        )

        # 2. Persistance dans le schéma ou la table du tenant
        self.repository.save_document(document)

        # 3. Inférence Agentique MCP (Outils : vérification juridique, calcul pénalités)
        mcp_tools = ["clause_risk_analyzer", "regulatory_compliance_checker"]
        analysis_result = self.ai_agent.analyze_document(
            sanitized_content=sanitized_content,
            tenant_context=tenant_context,
            tools=mcp_tools,
        )
        analysis_result.document_id = doc_id

        # 4. Persistance du résultat d'analyse
        self.repository.save_analysis(analysis_result)

        # 5. Émission de télémétrie OpenTelemetry
        duration_ms = (time.time() - start_time) * 1000
        self.telemetry.record_reasoning_step(
            tenant_id=tenant_context.tenant_id,
            step_name="contract_agentic_pipeline",
            duration_ms=duration_ms,
            tokens_used=analysis_result.tokens_consumed,
            attributes={
                "tier": tenant_context.tier.value,
                "requires_human_review": analysis_result.requires_human_review,
                "overall_risk_score": analysis_result.overall_risk_score,
                "is_isolated_storage": tenant_context.is_isolated_storage(),
            },
        )

        return analysis_result
