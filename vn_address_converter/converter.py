import copy

from typing import Union
from .models import Address, AddressLevel, MappingMissingError
from .parser import parse_address
from .aliases import normalize_alias
from .mapping import get_ward_mapping



def convert_to_new_address(address: Union[str, Address]) -> Address:
    # If string is provided, parse it to Address object first
    if isinstance(address, str):
        address = parse_address(address)
    
    province = address.province
    district = address.district
    ward = address.ward
    street_address = address.street_address

    # If district is missing, this could be a new address format then return as is
    if not district:
        return copy.copy(address)
    
    if not province or not ward:
        raise ValueError('Missing province or ward in address')

    mapping_obj = get_ward_mapping()
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

    # Handle legacy district mapping if available
    if province_map.get('legacy_district_mapping'):
        legacy_mapping = province_map['legacy_district_mapping']
        if district in legacy_mapping:
            district_key = legacy_mapping[district]
        elif district_norm in legacy_mapping:
            district_key = legacy_mapping[district_norm]

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
