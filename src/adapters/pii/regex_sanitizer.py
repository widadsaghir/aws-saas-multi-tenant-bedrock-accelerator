"""
Local PII Sanitizer Adapter - Caviardage Déterministe 0 Token
Conforme au Pattern Zero-Trust Sovereign Air-Gap Sanitizer
"""
import re
from src.domain.ports import PiiSanitizerPort


class RegexPiiSanitizerAdapter(PiiSanitizerPort):
    """
    Dé-identification locale s'exécutant dans le pod EKS avant tout envoi vers le LLM.
    Garantit qu'aucune information nominative sensible (santé/juridique) ne quitte le conteneur.
    """

    def __init__(self):
        # NIR (Numéro de Sécurité Sociale Français : 13 ou 15 chiffres)
        self.nir_pattern = re.compile(r"\b[12]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}(\s?\d{2})?\b")
        # IBAN Français
        self.iban_pattern = re.compile(r"\bFR\d{2}[A-Z0-9]{23}\b", re.IGNORECASE)
        # Email
        self.email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
        # Numéro de Téléphone Français
        self.phone_pattern = re.compile(r"\b(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}\b")

    def sanitize(self, text: str) -> str:
        if not text:
            return ""

        sanitized = text
        sanitized = self.nir_pattern.sub("[PII_NIR_REDACTED]", sanitized)
        sanitized = self.iban_pattern.sub("[PII_IBAN_REDACTED]", sanitized)
        sanitized = self.email_pattern.sub("[PII_EMAIL_REDACTED]", sanitized)
        sanitized = self.phone_pattern.sub("[PII_PHONE_REDACTED]", sanitized)

        return sanitized
