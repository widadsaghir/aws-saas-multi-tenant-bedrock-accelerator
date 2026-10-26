"""
OpenTelemetry Adapter - Observabilité Distribuée des Agents IA en Production
Conforme aux recommandations de Damián Arregui (AWS Summit / AgentCore)
"""
from typing import Any

from src.domain.ports import AuditTelemetryPort


class OpenTelemetryAdapter(AuditTelemetryPort):
    """
    Traceur de raisonnement pour agents IA.
    Émet des Spans structurés contenant le tenant_id, les métriques d'inférence et les étapes MCP.
    """

    def __init__(self):
        # Buffer de traces en mémoire pour validation locale et inspection
        self.recorded_spans: list[dict[str, Any]] = []

    def record_reasoning_step(
        self,
        tenant_id: str,
        step_name: str,
        duration_ms: float,
        tokens_used: int,
        attributes: dict
    ) -> None:
        span = {
            "tenant_id": tenant_id,
            "step_name": step_name,
            "duration_ms": duration_ms,
            "tokens_used": tokens_used,
            "attributes": attributes,
            "otel_instrumentation": "aws-bedrock-agentcore",
        }
        self.recorded_spans.append(span)

    def get_spans_for_tenant(self, tenant_id: str) -> list[dict[str, Any]]:
        return [span for span in self.recorded_spans if span["tenant_id"] == tenant_id]

    def get_total_tokens_for_tenant(self, tenant_id: str) -> int:
        return sum(span["tokens_used"] for span in self.get_spans_for_tenant(tenant_id))
