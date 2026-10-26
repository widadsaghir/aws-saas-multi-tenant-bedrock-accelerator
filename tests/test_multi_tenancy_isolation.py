"""
Tests Unitaires TDD : Isolation Multi-Tenant Silo vs Pool
Vérification mathématique de l'absence de fuite cross-tenant
"""
from src.adapters.repository.in_memory_repository import InMemoryDocumentRepository
from src.domain.models import DocumentEntity, TenantContext, TenantTier


def test_silo_tenant_isolation():
    repo = InMemoryDocumentRepository()
    
    tenant_a = TenantContext(tenant_id="tenant-clinic-a", tier=TenantTier.SILO)
    tenant_b = TenantContext(tenant_id="tenant-clinic-b", tier=TenantTier.SILO)

    doc_a = DocumentEntity(
        document_id="doc-a-101",
        tenant_context=tenant_a,
        filename="dossier_medical_a.pdf",
        raw_content="Contenu confidentiel de la clinique A."
    )
    repo.save_document(doc_a)

    # 1. Le tenant A peut récupérer son propre document
    retrieved_a = repo.get_document("doc-a-101", tenant_id="tenant-clinic-a")
    assert retrieved_a is not None
    assert retrieved_a.filename == "dossier_medical_a.pdf"

    # 2. Le tenant B NE PEUT PAS accéder au document du tenant A (isolation Silo)
    leakage_attempt = repo.get_document("doc-a-101", tenant_id=tenant_b.tenant_id)
    assert leakage_attempt is None


def test_pool_tenant_isolation_with_rls():
    repo = InMemoryDocumentRepository()

    tenant_pme_1 = TenantContext(tenant_id="tenant-pme-1", tier=TenantTier.POOL)
    tenant_pme_2 = TenantContext(tenant_id="tenant-pme-2", tier=TenantTier.POOL)

    doc_pme_1 = DocumentEntity(
        document_id="doc-pme-202",
        tenant_context=tenant_pme_1,
        filename="facture_pme_1.pdf",
        raw_content="Contenu de la PME 1."
    )
    repo.save_document(doc_pme_1)

    # 1. Le tenant 1 accède à son document
    assert repo.get_document("doc-pme-202", tenant_id=tenant_pme_1.tenant_id) is not None

    # 2. Le tenant 2 est bloqué même dans le pool partagé
    assert repo.get_document("doc-pme-202", tenant_id=tenant_pme_2.tenant_id) is None
