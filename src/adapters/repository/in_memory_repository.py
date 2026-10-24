"""
In-Memory & Dynamic PostgreSQL Repository Adapter
Modélise l'isolation hybride Silo (schémas dédiés) et Pool (partagé RLS)
"""
from typing import Dict, Optional
from src.domain.models import DocumentEntity, ContractAnalysisResult, TenantTier
from src.domain.ports import DocumentRepositoryPort


class InMemoryDocumentRepository(DocumentRepositoryPort):
    """
    Simulateur de base de données relationnelle Aurora multi-tenant en mémoire.
    - Pour les tiers SILO : partitionnement dans un conteneur dédié étanche `silo_{tenant_id}`.
    - Pour les tiers POOL : partitionnement dans une table mutualisée `pool_shared_documents`.
    """

    def __init__(self):
        # Silos isolés : {tenant_id: {doc_id: DocumentEntity}}
        self.silo_schemas: Dict[str, Dict[str, DocumentEntity]] = {}
        # Pool partagé : {doc_id: DocumentEntity}
        self.pool_shared_documents: Dict[str, DocumentEntity] = {}
        # Stockage des analyses
        self.analyses: Dict[str, ContractAnalysisResult] = {}

    def save_document(self, document: DocumentEntity) -> None:
        tenant_context = document.tenant_context
        if tenant_context.tier == TenantTier.SILO:
            # Création du schéma isolé si inexistant
            if tenant_context.tenant_id not in self.silo_schemas:
                self.silo_schemas[tenant_context.tenant_id] = {}
            self.silo_schemas[tenant_context.tenant_id][document.document_id] = document
        else:
            # Stockage dans le pool partagé avec tenant_id
            self.pool_shared_documents[document.document_id] = document

    def save_analysis(self, result: ContractAnalysisResult) -> None:
        self.analyses[result.analysis_id] = result

    def get_document(self, document_id: str, tenant_id: str) -> Optional[DocumentEntity]:
        # 1. Vérification dans les silos isolés
        if tenant_id in self.silo_schemas and document_id in self.silo_schemas[tenant_id]:
            return self.silo_schemas[tenant_id][document_id]
        
        # 2. Vérification dans le pool partagé (avec validation stricte du tenant_id)
        if document_id in self.pool_shared_documents:
            doc = self.pool_shared_documents[document_id]
            if doc.tenant_context.tenant_id == tenant_id:
                return doc
        return None

    def get_analysis(self, analysis_id: str) -> Optional[ContractAnalysisResult]:
        return self.analyses.get(analysis_id)
