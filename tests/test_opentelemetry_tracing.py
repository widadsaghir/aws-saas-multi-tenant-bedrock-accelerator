"""
Tests Unitaires TDD : Observabilité OpenTelemetry & FinOps par Tenant
"""
import pytest
from src.adapters.telemetry.opentelemetry_adapter import OpenTelemetryAdapter


def test_opentelemetry_records_reasoning_spans():
    otel = OpenTelemetryAdapter()

    otel.record_reasoning_step(
        tenant_id="tenant-hosp-marseille",
        step_name="pii_redaction_step",
        duration_ms=12.5,
        tokens_used=0,
        attributes={"stage": "local_sanitization"}
    )

    otel.record_reasoning_step(
        tenant_id="tenant-hosp-marseille",
        step_name="bedrock_claude_inference",
        duration_ms=480.0,
        tokens_used=820,
        attributes={"model": "claude-3-5-sonnet", "guardrails_passed": True}
    )

    spans = otel.get_spans_for_tenant("tenant-hosp-marseille")
    assert len(spans) == 2
    assert spans[0]["step_name"] == "pii_redaction_step"
    assert spans[1]["tokens_used"] == 820
    assert otel.get_total_tokens_for_tenant("tenant-hosp-marseille") == 820


def test_opentelemetry_isolates_metrics_across_tenants():
    otel = OpenTelemetryAdapter()

    otel.record_reasoning_step(tenant_id="tenant-1", step_name="step_a", duration_ms=50.0, tokens_used=300, attributes={})
    otel.record_reasoning_step(tenant_id="tenant-2", step_name="step_b", duration_ms=75.0, tokens_used=500, attributes={})

    assert otel.get_total_tokens_for_tenant("tenant-1") == 300
    assert otel.get_total_tokens_for_tenant("tenant-2") == 500
