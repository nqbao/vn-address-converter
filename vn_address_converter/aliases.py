"""Address alias normalization functionality for Vietnamese addresses."""

import re
import unicodedata
from .models import AddressLevel
from .utils import accent_fold


def normalize(name: str, level: 'AddressLevel') -> str:
    """Normalize the given address name based on its level.
    
    Args:
        name: The name to normalize
        level: The administrative level (province, district, ward)
        
    Returns:
        Normalized name as a lowercase string
    """
    name = name.strip()
    name = unicodedata.normalize("NFC", name)
    
    # Remove parenthetical text like "(Hết hiệu lực)", "(No longer valid)", etc.
    # Only for districts, wards, and cities (not provinces)
    if level in (AddressLevel.DISTRICT, AddressLevel.WARD):
        name = re.sub(r'\([^)]*\)', '', name).strip()

    if level == AddressLevel.PROVINCE:
        name = re.sub(r'\s*province\s*$', '', name, flags=re.IGNORECASE).strip()
    if level == AddressLevel.DISTRICT:
        # Normalize district numbers (e.g., "quận 01" -> "quận 1")
        name = re.sub(r'\b0+(\d+)\b', r'\1', name)
        name = re.sub(r'\bdistrict\s*', '', name, flags=re.IGNORECASE)
    elif level == AddressLevel.WARD:
        # Normalize ward numbers (e.g., "phường 01" -> "phường 1")
        name = re.sub(r'\b0+(\d+)\b', r'\1', name)
        name = re.sub(r'\bward\s*', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\bcommunes?\s*', '', name, flags=re.IGNORECASE)

    
    return name.strip().lower()


def _normalize_vietnamese_phonetics(text: str) -> list[str]:
    """Generate Vietnamese phonetic variants for common ambiguous spellings.
    
    Args:
        text: The text to generate phonetic variants for
        
    Returns:
        List of phonetic variants including the original text
    """
    variants = [text]
    
    # Common Vietnamese phonetic variations
    replacements = [
        # oa/oà variations
        ('oà', 'òa'),  # Hoà -> Hòa
        ('òa', 'oà'),  # Hòa -> Hoà
        # Add more patterns as needed
        ('hoà', 'hòa'),
        ('hòa', 'hoà'),
        ('toà', 'tòa'),
        ('tòa', 'toà'),
        ('soà', 'sòa'),
        ('sòa', 'soà'),
    ]
    
    for old, new in replacements:
        if old in text.lower():
            variant = text.lower().replace(old, new)
            if variant not in variants:
                variants.append(variant)
                
    return variants


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

    # Generate Vietnamese phonetic variants
    phonetic_variants = _normalize_vietnamese_phonetics(name)
    for variant in phonetic_variants:
        if variant.lower() not in aliases:
            aliases.append(variant.lower())

    normalized = unicodedata.normalize("NFC", name).lower()
    if level == AddressLevel.PROVINCE:
        # Special case for provinces: remove "tỉnh" or "thành phố" prefix if present
        normalized = re.sub(r'^(tỉnh|thành phố)\s*', '', normalized, flags=re.IGNORECASE).strip()
    elif level == AddressLevel.DISTRICT:
        # Special case for districts: remove "thành phố" or "TP" prefix if present
        normalized = re.sub(r'^(thành phố|tp\.?|quận|huyện|thị xã|tx\.?|h\.?|x\.?)\s*', '', normalized, flags=re.IGNORECASE).strip()
    elif level == AddressLevel.WARD:
        # Special case for wards: remove "phường" or "xã" prefix if present
        normalized = re.sub(r'^(phường|xã|x\.?)\s*', '', normalized, flags=re.IGNORECASE).strip()

    if normalized not in aliases:
        aliases.append(normalized)
        # add accent folded version
        accent_folded = accent_fold(normalized)
        if accent_folded and accent_folded not in aliases:
            aliases.append(accent_folded)
    
    # Generate phonetic variants for normalized form too
    normalized_variants = _normalize_vietnamese_phonetics(normalized)
    for variant in normalized_variants:
        if variant.lower() not in aliases:
            aliases.append(variant.lower())
    
    # Add numbered ward/district abbreviation aliases (P1, P.1, P01, P.01, etc.)
    if level in (AddressLevel.WARD, AddressLevel.DISTRICT):
        # Check if this is a numbered ward/district
        number_match = re.search(r'\b(\d+)\b', normalized)
        if number_match:
            number = number_match.group(1)
            number_int = int(number)
            
            # Generate common abbreviation patterns
            abbreviations = []
            if level == AddressLevel.WARD:
                abbreviations.extend([
                    f"p{number}",           # p1
                    f"p.{number}",          # p.1  
                    f"p{number_int:02d}",   # p01
                    f"p.{number_int:02d}",  # p.01
                ])
            elif level == AddressLevel.DISTRICT:
                abbreviations.extend([
                    f"q{number}",           # q1
                    f"q.{number}",          # q.1
                    f"q{number_int:02d}",   # q01
                    f"q.{number_int:02d}",  # q.01
                ])
            
            # Add variants with different cases
            for abbr in abbreviations:
                if abbr not in aliases:
                    aliases.append(abbr)
                # Add uppercase version
                abbr_upper = abbr.upper()
                if abbr_upper not in aliases:
                    aliases.append(abbr_upper)
    
    # Add accent folded version (after NFC normalization)
    accent_folded_final = accent_fold(name.lower())
    if accent_folded_final and accent_folded_final not in aliases:
        aliases.append(accent_folded_final)
    
    return aliases
