"""
Domain Models - Pure Domain Logic (0 AWS SDK Dependencies)
Architecture Hexagonale & Domain-Driven Design (DDD)
"""
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class TenantTier(str, Enum):
    SILO = "SILO"      # Régulé (Santé / Notariat) : Schéma DB dédié + Clé KMS CMK
    POOL = "POOL"      # Standard (PME) : Schéma mutualisé avec Row-Level Security


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    tier: TenantTier
    kms_key_arn: str | None = None
    cost_center: str = "DEFAULT"

    def is_isolated_storage(self) -> bool:
        return self.tier == TenantTier.SILO


@dataclass
class Clause:
    clause_id: str
    title: str
    content: str
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    compliance_flags: list[str] = field(default_factory=list)


@dataclass
class ContractAnalysisResult:
    analysis_id: str
    tenant_id: str
    document_id: str
    overall_risk_score: float  # Entre 0.0 (zéro risque) et 1.0 (risque critique)
    detected_clauses: list[Clause]
    requires_human_review: bool
    tokens_consumed: int
    inference_latency_ms: float
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def is_compliant_for_auto_approval(self) -> bool:
        # Règle d'or : score de risque inférieur à 0.15 et pas de flag critique
        return self.overall_risk_score < 0.15 and not self.requires_human_review


@dataclass
class DocumentEntity:
    document_id: str
    tenant_context: TenantContext
    filename: str
    raw_content: str
    sanitized_content: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
