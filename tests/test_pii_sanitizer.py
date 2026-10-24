"""
Tests Unitaires TDD : Caviardage PII Déterministe Local (0 Token)
"""
import pytest
from src.adapters.pii.regex_sanitizer import RegexPiiSanitizerAdapter


def test_pii_sanitizer_masks_french_nir_security_number():
    sanitizer = RegexPiiSanitizerAdapter()
    text = "Le patient Jean Dupont possède le numéro de sécurité sociale 1 85 12 75 108 234 45 pour son admission."
    sanitized = sanitizer.sanitize(text)
    assert "1 85 12 75 108 234 45" not in sanitized
    assert "[PII_NIR_REDACTED]" in sanitized


def test_pii_sanitizer_masks_iban():
    sanitizer = RegexPiiSanitizerAdapter()
    text = "Veuillez effectuer le virement sur le compte FR7630006000011234567890189 dès signature."
    sanitized = sanitizer.sanitize(text)
    assert "FR7630006000011234567890189" not in sanitized
    assert "[PII_IBAN_REDACTED]" in sanitized


def test_pii_sanitizer_masks_email_and_phone():
    sanitizer = RegexPiiSanitizerAdapter()
    text = "Contact : docteur.martin@clinique-paris.fr ou par téléphone au 06 12 34 56 78."
    sanitized = sanitizer.sanitize(text)
    assert "docteur.martin@clinique-paris.fr" not in sanitized
    assert "06 12 34 56 78" not in sanitized
    assert "[PII_EMAIL_REDACTED]" in sanitized
    assert "[PII_PHONE_REDACTED]" in sanitized


def test_pii_sanitizer_handles_empty_or_clean_text():
    sanitizer = RegexPiiSanitizerAdapter()
    assert sanitizer.sanitize("") == ""
    clean_text = "Le présent contrat de sous-traitance est conclu pour une durée de 3 ans."
    assert sanitizer.sanitize(clean_text) == clean_text
