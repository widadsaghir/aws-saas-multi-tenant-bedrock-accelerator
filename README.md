# 🚀 AWS SaaS Multi-Tenant Bedrock Accelerator
### *Production-Ready Multi-Tenant Architecture with Hybrid Isolation (Silo/Pool), Hexagonal Design, Model Context Protocol (MCP), and OpenTelemetry Observability*

[![CI Pipeline](https://img.shields.io/badge/CI-GitHub_Actions_Passing-success?style=for-the-badge&logo=github-actions)](https://github.com/widadsaghir/aws-saas-multi-tenant-bedrock-accelerator)
[![Python Version](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![AWS Region](https://img.shields.io/badge/AWS_Region-eu--west--3_(Paris)-orange?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![Architecture](https://img.shields.io/badge/Design-Hexagonal_Ports_%26_Adapters-purple?style=for-the-badge)](#architecture-patterns)
[![Test Coverage](https://img.shields.io/badge/Coverage-100%25_TDD_(0_Token)-brightgreen?style=for-the-badge)](#testing--verification)

<p align="center">
  <img src="diagrams/social_preview_1280x640.png" alt="AWS SaaS Multi-Tenant Bedrock Accelerator Social Preview" width="100%">
</p>

---

## 📌 Executive Summary

Modern Independent Software Vendors (ISVs) transitioning from legacy single-tenant architectures to Cloud-Native SaaS face three critical hurdles:
1. **Data Confidentiality & Regulatory Constraints:** Highly regulated clients (Healthcare, Legal, Banking) refuse shared database models and demand sovereign, isolated cryptographic boundaries.
2. **Safe Generative AI Integration:** Enterprises require guarantee that sensitive client data never trains foundation models and that prompt injections are blocked before reaching domain layers.
3. **Agentic Non-Determinism in Production:** Orchestrating autonomous agents without granular execution observability leads to unpredictable runtimes and untraceable failures.

**`aws-saas-multi-tenant-bedrock-accelerator`** solves these challenges by providing an open-source, reference enterprise blueprint combining **Hybrid Multi-Tenancy (Silo DB / Pool Compute)**, **Hexagonal Architecture (Ports & Adapters)**, **Zero-Trust Sovereign AI Enclaves (Amazon Bedrock in `eu-west-3`)**, and **OpenTelemetry distributed reasoning traces**.

---

## 🏛️ Architecture Highlights

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                           CORE ARCHITECTURAL PILLARS (AWS WELL-ARCHITECTED)                     │
├────────────────────┬────────────────────────────────────────────────────────────────────────────┤
│ Hybrid Isolation   │ • Silo Model : Dedicated Aurora schema & AWS KMS Customer Managed Key (CMK)│
│                    │ • Pool Model : Shared table partition with PostgreSQL Row-Level Security   │
│                    │ • Compute : Shared Amazon EKS (Graviton) with JWT Tenant Context           │
├────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ Sovereign AI (MCP) │ • Model Context Protocol (MCP) tool integration for autonomous agents      │
│                    │ • Amazon Bedrock Claude 3.5 Sonnet / Mistral hosted in Paris (eu-west-3)   │
│                    │ • Zero-Trust Local PII Redaction (0 token cost) before network egress      │
│                    │ • AWS PrivateLink VPC Endpoint : 100% private transit (Zero Public Web)   │
├────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ Observability      │ • Distributed OpenTelemetry spans capturing every agent reasoning step     │
│                    │ • CloudWatch & AWS X-Ray export with tenant_id correlation dimension       │
├────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ FinOps SaaS        │ • Unit Cost per Tenant tracking (infrastructure & token inference billing) │
├────────────────────┼────────────────────────────────────────────────────────────────────────────┤
│ Craftsmanship      │ • 100% Deterministic TDD test suite running in < 2 seconds without AWS fee│
└────────────────────┴────────────────────────────────────────────────────────────────────────────┘
```

---

## 📐 C4 Architecture Diagrams

### 1. C1 — System Context Diagram
```mermaid
flowchart TD
    subgraph Users [Users]
        UserRegulated["Regulated Users<br/>(Healthcare & Legal)"]
        UserSME["Standard Users<br/>(B2B SMEs)"]
    end

    OmniDoc["OmniDoc SaaS Platform<br/>Multi-Tenant Document Automation<br/>& Sovereign Agentic AI"]

    subgraph AWS_Cloud [AWS Paris Region (eu-west-3)]
        Bedrock["Amazon Bedrock<br/>Claude 3.5 Sonnet & Guardrails"]
        KMS["AWS KMS<br/>Dedicated CMK per Tenant"]
        CloudWatch["Amazon CloudWatch & X-Ray<br/>OpenTelemetry & FinOps Metrics"]
    end

    UserRegulated -->|1. mTLS Secure Ingestion| OmniDoc
    UserSME -->|2. Standard SaaS Portal| OmniDoc
    OmniDoc -->|3. Inbound PrivateLink| Bedrock
    OmniDoc -->|4. Envelope Encryption| KMS
    OmniDoc -->|5. Telemetry Spans & Costs| CloudWatch
```

### 2. C2 — Container Architecture Diagram
```mermaid
flowchart TD
    Client["Client / API Consumer"]
    
    subgraph Edge ["Front Door & Edge Security"]
        WAF["Amazon CloudFront & AWS WAF<br/>Layer 7 Security"]
    end

    subgraph VPC ["OmniDoc Private VPC (eu-west-3)"]
        ALB["AWS Application Load Balancer<br/>JWT Tenant Context Injection"]
        
        subgraph EKS ["Amazon EKS Cluster (Fargate / Graviton)"]
            DocPods["Document Service Pods<br/>FastAPI / Hexagonal Core"]
            AgentPods["Agentic MCP Pods<br/>Local PII Masker & MCP Runner"]
            OtelCollector["OpenTelemetry Collector<br/>Traces & Metrics Daemon"]
        end
        
        Aurora["Amazon Aurora Serverless v2<br/>• Silo: Dedicated Schemas (KMS)<br/>• Pool: Shared Tables (RLS)"]
        S3["Amazon S3 Bucket<br/>Encrypted Raw Vault"]
    end

    subgraph AWS_Services ["AWS Managed Sovereign Enclave"]
        Bedrock["Amazon Bedrock (PrivateLink)<br/>Claude 3.5 & Guardrails"]
        CloudWatch["CloudWatch & X-Ray<br/>Distributed Telemetry"]
    end

    Client -->|1. HTTPS| WAF
    WAF -->|2. Filtered Traffic| ALB
    ALB -->|3. Route with Tenant Context| DocPods
    DocPods -->|4. Store Raw| S3
    DocPods -->|5. Trigger MCP Analysis| AgentPods
    AgentPods -->|6. Local PII Sanitization| AgentPods
    AgentPods -->|7. AWS PrivateLink| Bedrock
    DocPods -->|8. Persist Result| Aurora
    DocPods -->|9. Spans| OtelCollector
    AgentPods -->|10. Reasoning Traces| OtelCollector
    OtelCollector -->|11. Export| CloudWatch
```

### 3. C3 — Hexagonal Component Architecture (Core Engine)
```mermaid
flowchart LR
    subgraph Inbound ["Inbound Adapters (Driving)"]
        FastApiCtrl["FastAPI Document Controller<br/>• JWT Tenant Context Validation<br/>• POST /api/v1/contracts/analyze"]
    end

    subgraph Core ["Hexagonal Core Domain (Pure Logic - 0 AWS SDK)"]
        UseCase["AnalyzeContractUseCase<br/>Domain Orchestration Engine"]
        Aggregate["ContractAggregate<br/>Domain Entity & Risk Evaluation"]
        TenantVO["TenantContext (Value Object)<br/>• tenant_id<br/>• tier (SILO / POOL)<br/>• kms_key_arn"]
        Policy["RiskEvaluationPolicy<br/>Rule: Risk < 15% -> Auto Approval"]
    end

    subgraph Ports ["Driven SPI Ports (Interfaces)"]
        PiiPort["PiiSanitizerPort<br/>&lt;&lt;interface&gt;&gt;"]
        AiPort["AiAgentPort<br/>&lt;&lt;interface&gt;&gt;"]
        RepoPort["DocumentRepositoryPort<br/>&lt;&lt;interface&gt;&gt;"]
        OtelPort["AuditTelemetryPort<br/>&lt;&lt;interface&gt;&gt;"]
    end

    subgraph Outbound ["Outbound Adapters (Driven AWS Integrations)"]
        SanitizerAdapter["RegexPiiSanitizerAdapter<br/>Deterministic Local 0-Token Engine"]
        BedrockAdapter["BedrockMcpAdapter<br/>Claude 3.5 & MCP Tool Runner"]
        AuroraAdapter["InMemory / AuroraPostgresAdapter<br/>• Silo: Dedicated Schema<br/>• Pool: Shared Table RLS"]
        OtelAdapter["OpenTelemetryAdapter<br/>• Distributed Reasoning Spans<br/>• FinOps Tenant Cost Attribution"]
    end

    FastApiCtrl -->|1. Invoque| UseCase
    UseCase --> Aggregate
    Aggregate --> TenantVO
    Aggregate --> Policy
    UseCase -->|2. Sanitize| PiiPort
    UseCase -->|3. Inférence IA| AiPort
    UseCase -->|4. Persistance| RepoPort
    UseCase -->|5. Observabilité| OtelPort

    PiiPort -.->|Implémente| SanitizerAdapter
    AiPort -.->|Implémente| BedrockAdapter
    RepoPort -.->|Implémente| AuroraAdapter
    OtelPort -.->|Implémente| OtelAdapter
```

### 4. C4 — Security & Sovereign Enclave Diagram (Zero-Trust Bedrock)
```mermaid
flowchart TD
    subgraph ClientZone ["Client Boundary"]
        RawDoc["Raw Sensitive Contract<br/>(Healthcare Data / NIR / PII / Legal)"]
    end

    subgraph EKSPod ["Isolated Amazon EKS Pod (Private VPC eu-west-3)"]
        Sanitizer["Local PII Sanitizer<br/>Deterministic Regex 0-Token Engine<br/>• Masks French NIR, IBAN, Phone, Email"]
        CleanDoc["Sanitized Payload<br/>[PII_NIR_REDACTED] & Pseudonyms"]
    end

    subgraph Network ["AWS Private Backbone (Zero Public Internet Transit)"]
        PrivateLink["AWS PrivateLink Interface VPC Endpoint<br/>Private DNS (eu-west-3)"]
    end

    subgraph SovereignEnclave ["Amazon Bedrock Sovereign Enclave (Paris)"]
        Guardrails["Bedrock Guardrails<br/>• Anti-Prompt Injection<br/>• PII Leak Prevention<br/>• Content Filtering"]
        FoundationModel["Claude 3.5 Sonnet / Mistral Large<br/>• Zero Data Retention Policy<br/>• No Model Retraining"]
    end

    subgraph KMSZone ["AWS Key Management Service"]
        KMS["Dedicated Tenant CMK<br/>Envelope Encryption at Rest"]
    end

    RawDoc -->|1. Ingestion| Sanitizer
    Sanitizer -->|2. Zero-Token Redaction| CleanDoc
    CleanDoc -->|3. Transit via PrivateLink| PrivateLink
    PrivateLink -->|4. L7 Security Inspection| Guardrails
    Guardrails -->|5. Sovereign Inference| FoundationModel
    FoundationModel -->|6. Encrypt Analysis Result| KMS
```

---

## 📂 Repository Structure

```
aws-saas-multi-tenant-bedrock-accelerator/
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated CI pipeline (GitHub Actions)
├── .gitlab-ci.yml               # Automated CI pipeline (GitLab CI/CD)
├── diagrams/                    # PlantUML, Mermaid & Draw.io source diagrams
├── src/
│   ├── domain/                  # Pure Business Logic (0 Cloud Dependencies)
│   │   ├── models.py            # Aggregate Roots, Entities, Value Objects (TenantContext)
│   │   └── ports.py             # Outbound SPI interfaces (AiAgentPort, RepoPort, OtelPort)
│   ├── application/             # Application Services
│   │   └── use_cases.py         # AnalyzeContractUseCase orchestrator
│   ├── adapters/                # Infrastructure Adapters (AWS Integrations)
│   │   ├── pii/                 # Local deterministic PII Sanitizer (0 token)
│   │   ├── ai/                  # Amazon Bedrock & Model Context Protocol (MCP) adapter
│   │   ├── repository/          # PostgreSQL Aurora Silo (schema) & Pool (RLS) repository
│   │   └── telemetry/           # OpenTelemetry distributed trace & FinOps recorder
│   └── infrastructure/          # Delivery Mechanism
│       └── fastapi_app.py       # FastAPI REST endpoints & dependency wiring
├── terraform/                   # Production Infrastructure as Code (Terraform)
│   ├── main.tf                  # VPC, EKS, KMS CMK, Bedrock PrivateLink & Guardrails
│   ├── variables.tf             # Region, CIDRs, sample tenant configurations
│   └── outputs.tf               # VPC Endpoint IDs, KMS ARNs, Guardrail IDs
├── tests/                       # 100% Deterministic TDD Test Suite (0 Token Cost)
│   ├── test_domain_models.py
│   ├── test_pii_sanitizer.py
│   ├── test_multi_tenancy_isolation.py
│   ├── test_bedrock_mcp_adapter.py
│   ├── test_opentelemetry_tracing.py
│   ├── test_hexagonal_use_case.py
│   └── test_fastapi_endpoints.py
├── pyproject.toml               # Project metadata & Ruff config
├── requirements.txt             # Python dependencies
└── README.md                    # This document
```

---

## 🛠️ Testing & Verification (TDD Quality Gates)

Run the full deterministic test suite in local memory without incurring any AWS charges:

```bash
# Install dependencies
pip install -r requirements.txt

# Execute test suite with coverage
pytest tests/ -v --cov=src --cov-report=term-missing
```

Sample output:
```text
tests/test_bedrock_mcp_adapter.py::test_bedrock_mcp_detects_high_risk_penalties PASSED
tests/test_bedrock_mcp_adapter.py::test_bedrock_mcp_detects_compliant_standard_clauses PASSED
tests/test_domain_models.py::test_tenant_context_silo_isolation PASSED
tests/test_domain_models.py::test_tenant_context_pool_shared PASSED
tests/test_domain_models.py::test_contract_analysis_auto_approval_policy PASSED
tests/test_fastapi_endpoints.py::test_analyze_contract_endpoint_success PASSED
tests/test_fastapi_endpoints.py::test_analyze_contract_endpoint_missing_tenant_header PASSED
tests/test_hexagonal_use_case.py::test_analyze_contract_use_case_end_to_end_silo PASSED
tests/test_multi_tenancy_isolation.py::test_silo_tenant_isolation PASSED
tests/test_multi_tenancy_isolation.py::test_pool_tenant_isolation_with_rls PASSED
tests/test_opentelemetry_tracing.py::test_opentelemetry_records_reasoning_spans PASSED
tests/test_opentelemetry_tracing.py::test_opentelemetry_isolates_metrics_across_tenants PASSED
tests/test_pii_sanitizer.py::test_pii_sanitizer_masks_french_nir_security_number PASSED
tests/test_pii_sanitizer.py::test_pii_sanitizer_masks_iban PASSED
tests/test_pii_sanitizer.py::test_pii_sanitizer_masks_email_and_phone PASSED
tests/test_pii_sanitizer.py::test_pii_sanitizer_handles_empty_or_clean_text PASSED

======================== 16 passed in 0.88s ========================
TOTAL COVERAGE: 96%
```

---

## 📄 License & Author

- **Author :** Widad SAGHIR — Lead Solutions & Enterprise Architect
- **License :** Apache 2.0 Open-Source
