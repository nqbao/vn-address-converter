import json
import os
import re
import unicodedata

from .models import Address, AddressLevel, MappingMissingError

WARD_MAPPING_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ward_mapping.json')
MANUAL_ALIASES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'manual_aliases.json')
WARD_MAPPING = None
MANUAL_ALIASES = None

def _get_manual_aliases():
    global MANUAL_ALIASES
    if MANUAL_ALIASES is None:
        try:
            with open(MANUAL_ALIASES_PATH, encoding='utf-8') as f:
                MANUAL_ALIASES = json.load(f)
        except FileNotFoundError:
            MANUAL_ALIASES = {"provinces": {}, "districts": {}, "wards": {}}
    return MANUAL_ALIASES

def normalize_alias(name: str, level: 'AddressLevel') -> str:
    if level == AddressLevel.PROVINCE:
        remove_words = ['thành phố', 'tỉnh']
    elif level == AddressLevel.DISTRICT:
        remove_words = ['thành phố', 'quận', 'huyện']
    elif level == AddressLevel.WARD:
        remove_words = ['phường', 'xã']
    else:
        remove_words = []
    name = unicodedata.normalize("NFC", name)
    pattern = r"^(%s)\s*" % "|".join([re.escape(w) for w in remove_words])  # <-- FIXED: single backslash
    name = re.sub(pattern, '', name, flags=re.IGNORECASE).strip()
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

def _get_ward_mapping():
    global WARD_MAPPING
    if WARD_MAPPING is None:
        with open(WARD_MAPPING_PATH, encoding='utf-8') as f:
            mapping = json.load(f)
        
        manual_aliases = _get_manual_aliases()
        
        province_aliases = {}
        district_aliases = {}
        ward_aliases = {}
        
        for prov_name, prov_val in mapping.items():
            # Use get_aliases to get all aliases for this province
            for alias in get_aliases(prov_name, AddressLevel.PROVINCE):
                province_aliases[alias] = prov_name
            
            # Add manual province aliases
            if prov_name in manual_aliases['provinces']:
                for alias in manual_aliases['provinces'][prov_name]:
                    province_aliases[alias.lower()] = prov_name
            
            district_aliases[prov_name] = {}
            ward_aliases[prov_name] = {}
            
            for dist_name, dist_val in prov_val.items():
                # Use get_aliases to get all aliases for this district
                for alias in get_aliases(dist_name, AddressLevel.DISTRICT):
                    district_aliases[prov_name][alias] = dist_name
                
                # Add manual district aliases
                if (prov_name in manual_aliases['districts'] and 
                    dist_name in manual_aliases['districts'][prov_name]):
                    for alias in manual_aliases['districts'][prov_name][dist_name]:
                        district_aliases[prov_name][alias.lower()] = dist_name
                
                ward_aliases[prov_name][dist_name] = {}
                
                for ward_name in dist_val:
                    # Use get_aliases to get all aliases for this ward
                    for alias in get_aliases(ward_name, AddressLevel.WARD):
                        ward_aliases[prov_name][dist_name][alias] = ward_name
                    
                    # Add manual ward aliases
                    if (prov_name in manual_aliases['wards'] and 
                        dist_name in manual_aliases['wards'][prov_name] and
                        ward_name in manual_aliases['wards'][prov_name][dist_name]):
                        for alias in manual_aliases['wards'][prov_name][dist_name][ward_name]:
                            ward_aliases[prov_name][dist_name][alias.lower()] = ward_name
        
        WARD_MAPPING = {
            'mapping': mapping,
            'province_aliases': province_aliases,
            'district_aliases': district_aliases,
            'ward_aliases': ward_aliases
        }
    return WARD_MAPPING


def convert_to_new_address(address: Address) -> Address:
    province = address.province
    district = address.district
    ward = address.ward
    street_address = address.street_address

    if not province or not district or not ward:
        raise ValueError('Missing province, district, or ward in address')

    mapping_obj = _get_ward_mapping()
    mapping = mapping_obj['mapping']
    province_aliases = mapping_obj['province_aliases']
    district_aliases = mapping_obj['district_aliases']
    ward_aliases = mapping_obj['ward_aliases']

    province_norm = normalize_alias(province, AddressLevel.PROVINCE)
    province_key = province if province in mapping else province_aliases.get(province_norm)
    if not province_key or province_key not in mapping:
        raise MappingMissingError(AddressLevel.PROVINCE, province)
    province_map = mapping[province_key]

    district_norm = normalize_alias(district, AddressLevel.DISTRICT)
    district_key = district if district in province_map else district_aliases[province_key].get(district_norm)
    if not district_key or district_key not in province_map:
        raise MappingMissingError(AddressLevel.DISTRICT, district)
    district_map = province_map[district_key]

    ward_norm = normalize_alias(ward, AddressLevel.WARD)
    ward_key = ward if ward in district_map else ward_aliases[province_key][district_key].get(ward_norm)
    if not ward_key or ward_key not in district_map:
        raise MappingMissingError(AddressLevel.WARD, ward)
    ward_map = district_map[ward_key]

    new_province = ward_map['new_provine_name']
    new_ward = ward_map['new_ward_name']

    return Address(
        street_address=street_address,
        ward=new_ward,
        district=None,
        province=new_province
    )
