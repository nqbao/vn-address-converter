"""Address alias normalization functionality for Vietnamese addresses."""

import re
import unicodedata
from .models import AddressLevel


def normalize_alias(name: str, level: 'AddressLevel') -> str:
    """Normalize address component name by removing administrative prefixes.
    
    Args:
        name: The address component name to normalize
        level: The administrative level (province, district, ward)
        
    Returns:
        Normalized lowercase name with prefixes removed
    """
    if level == AddressLevel.PROVINCE:
        remove_words = ['thành phố', 'tỉnh']
    elif level == AddressLevel.DISTRICT:
        remove_words = ['thành phố', 'quận', 'huyện']
    elif level == AddressLevel.WARD:
        remove_words = ['phường', 'xã']
    else:
        remove_words = []
    
    name = unicodedata.normalize("NFC", name)
    pattern = r"^(%s)\s*" % "|".join([re.escape(w) for w in remove_words])
    name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
    
    # Handle leading zeros for numeric wards (e.g., "01" -> "1")
    if level == AddressLevel.WARD and name.isdigit() and len(name) > 1 and name.startswith('0'):
        name = str(int(name))
    
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
    
    # Add normalized alias (if not empty)
    normalized = normalize_alias(name, level)
    if normalized:
        aliases.append(normalized)
    
    # Add lowercased original name
    aliases.append(name.lower())
    
    # Add accent folded version (after NFC normalization)
    nfc_normalized = unicodedata.normalize("NFC", name.lower())
    accent_folded = unicodedata.normalize("NFD", nfc_normalized)
    accent_folded = ''.join(c for c in accent_folded if unicodedata.category(c) != 'Mn')
    accent_folded = accent_folded.lower()
    if accent_folded and accent_folded not in aliases:
        aliases.append(accent_folded)
    
    return aliases