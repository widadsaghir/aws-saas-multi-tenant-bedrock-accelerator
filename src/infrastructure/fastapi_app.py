"""
FastAPI Inbound Adapter - REST API & Dependency Injection
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

from src.adapters.ai.bedrock_mcp_adapter import BedrockMcpAdapter
from src.adapters.pii.regex_sanitizer import RegexPiiSanitizerAdapter
from src.adapters.repository.in_memory_repository import InMemoryDocumentRepository
from src.adapters.telemetry.opentelemetry_adapter import OpenTelemetryAdapter
from src.application.use_cases import AnalyzeContractUseCase
from src.domain.models import TenantContext, TenantTier

app = FastAPI(
    title="OmniDoc AWS SaaS Accelerator API",
    description="Multi-Tenant Contract Analysis with Amazon Bedrock, MCP, and OpenTelemetry",
    version="1.0.0"
)

# Composition Hexagonale / Wiring
sanitizer = RegexPiiSanitizerAdapter()
ai_agent = BedrockMcpAdapter()
repository = InMemoryDocumentRepository()
telemetry = OpenTelemetryAdapter()
use_case = AnalyzeContractUseCase(sanitizer, ai_agent, repository, telemetry)


class ContractAnalysisRequest(BaseModel):
    filename: str
    raw_content: str
    tier: str = "POOL"  # "SILO" ou "POOL"
    kms_key_arn: str | None = None


class ContractAnalysisResponse(BaseModel):
    analysis_id: str
    tenant_id: str
    document_id: str
    overall_risk_score: float
    requires_human_review: bool
    tokens_consumed: int
    inference_latency_ms: float
    clauses_detected_count: int


@app.post("/api/v1/contracts/analyze", response_model=ContractAnalysisResponse)
def analyze_contract_endpoint(
    request: ContractAnalysisRequest,
    x_tenant_id: str | None = Header(None, alias="X-Tenant-ID")
):
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="Header 'X-Tenant-ID' obligatoire.")

    tier = TenantTier.SILO if request.tier.upper() == "SILO" else TenantTier.POOL
    tenant_context = TenantContext(
        tenant_id=x_tenant_id,
        tier=tier,
        kms_key_arn=request.kms_key_arn
    )

    result = use_case.execute(
        filename=request.filename,
        raw_content=request.raw_content,
        tenant_context=tenant_context
    )

    return ContractAnalysisResponse(
        analysis_id=result.analysis_id,
        tenant_id=result.tenant_id,
        document_id=result.document_id,
        overall_risk_score=result.overall_risk_score,
        requires_human_review=result.requires_human_review,
        tokens_consumed=result.tokens_consumed,
        inference_latency_ms=result.inference_latency_ms,
        clauses_detected_count=len(result.detected_clauses)
    )
