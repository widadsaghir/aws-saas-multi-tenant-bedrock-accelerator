"""
Domain Ports - Pure SPI Interfaces for Hexagonal Architecture
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models import DocumentEntity, ContractAnalysisResult, TenantContext


class PiiSanitizerPort(ABC):
    """Port pour l'anonymisation / caviardage déterministe local (0 Token)"""
    @abstractmethod
    def sanitize(self, text: str) -> str:
        pass


class AiAgentPort(ABC):
    """Port pour l'inférence d'IA agentique et l'orchestration MCP"""
    @abstractmethod
    def analyze_document(
        self,
        sanitized_content: str,
        tenant_context: TenantContext,
        tools: List[str]
    ) -> ContractAnalysisResult:
        pass


class DocumentRepositoryPort(ABC):
    """Port pour la persistance avec routage Silo (schéma) ou Pool (RLS)"""
    @abstractmethod
    def save_document(self, document: DocumentEntity) -> None:
        pass

    @abstractmethod
    def save_analysis(self, result: ContractAnalysisResult) -> None:
        pass

    @abstractmethod
    def get_document(self, document_id: str, tenant_id: str) -> Optional[DocumentEntity]:
        pass


class AuditTelemetryPort(ABC):
    """Port pour l'observabilité OpenTelemetry des étapes de raisonnement"""
    @abstractmethod
    def record_reasoning_step(
        self,
        tenant_id: str,
        step_name: str,
        duration_ms: float,
        tokens_used: int,
        attributes: dict
    ) -> None:
        pass
