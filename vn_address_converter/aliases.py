"""Address alias normalization functionality for Vietnamese addresses."""

import re
import unicodedata
from .models import AddressLevel


def normalize(name: str, level: 'AddressLevel') -> str:
    """Normalize address component name by removing administrative prefixes.
    
    Args:
        name: The address component name to normalize
        level: The administrative level (province, district, ward)
        
    Returns:
        Normalized lowercase name with prefixes removed
    """
    name = name.strip()
    name = unicodedata.normalize("NFC", name)

    if level == AddressLevel.DISTRICT:
        # Normalize district numbers (e.g., "quận 01" -> "quận 1")
        name = re.sub(r'\b0+(\d+)\b', r'\1', name)
    elif level == AddressLevel.WARD:
        # Normalize ward numbers (e.g., "phường 01" -> "phường 1")
        name = re.sub(r'\b0+(\d+)\b', r'\1', name)
        
    
    return name.lower()


def get_aliases(name: str, level: 'AddressLevel') -> list[str]:
    """Return list of aliases for given input name and level.
    
    Args:
        name: The name to generate aliases for
        level: The administrative level (province, district, ward)
        
    Returns:
        List of aliases including normalized alias, lowercased original name, and accent folded version
    """
    aliases = []

    name = name.strip()
    
    # Add lowercased original name
    aliases.append(name.lower())

    normalized = unicodedata.normalize("NFC", name).lower()
    if level == AddressLevel.PROVINCE:
        # Special case for provinces: remove "tỉnh" or "thành phố" prefix if present
        normalized = re.sub(r'^(tỉnh|thành phố)\s*', '', normalized, flags=re.IGNORECASE).strip()
    elif level == AddressLevel.DISTRICT:
        # Special case for districts: remove "thành phố" prefix if present
        normalized = re.sub(r'^(thành phố|quận|huyện)\s*', '', normalized, flags=re.IGNORECASE).strip()
    elif level == AddressLevel.WARD:
        # Special case for wards: remove "phường" or "xã" prefix if present
        normalized = re.sub(r'^(phường|xã)\s*', '', normalized, flags=re.IGNORECASE).strip()

    aliases.append(normalized)
    
    # Add accent folded version (after NFC normalization)
    nfc_normalized = unicodedata.normalize("NFC", name.lower())
    accent_folded = unicodedata.normalize("NFD", nfc_normalized)
    accent_folded = ''.join(c for c in accent_folded if unicodedata.category(c) != 'Mn')
    accent_folded = accent_folded.lower()
    if accent_folded and accent_folded not in aliases:
        aliases.append(accent_folded)
    
    return aliases
