"""Address parsing functionality for Vietnamese addresses."""

import re
import unicodedata
from .models import Address, AddressLevel


def _extract_ward_from_street(street_address: str) -> tuple[str | None, str | None]:
    """Try to extract a ward name from the end of a street address string.

    In some Vietnamese address formats the ward abbreviation is embedded
    in the street component, e.g. 'Phạm Thế Hiển P.06' or 'Võ Văn Ngân
    P.Linh Chiểu'.  This helper recognises common abbreviation patterns
    at the end of the street part and returns the trimmed street plus
    the expanded ward name.

    Returns:
        (new_street_address, extracted_ward) or (street_address, None)
    """
    if not street_address:
        return street_address, None

    _VIETNAMESE_VOWELS = (
        'aeiouy'
        'àáảãạâầấẩẫậăằắẳẵặ'
        'èéẻẽẹêềếểễệ'
        'ìíỉĩị'
        'òóỏõọôồốổỗộơờớởỡợ'
        'ùúủũụưừứửữự'
        'ỳýỷỹỵ'
    )

    def _has_vietnamese(text: str) -> bool:
        return any(ch.lower() in _VIETNAMESE_VOWELS for ch in text)

    # Pattern 1: P.06, P.13, P.02  →  Phường {number} (strip leading zeros)
    m = re.search(r'\s+P\.(\d{1,3})\s*$', street_address)
    if m:
        ward_num = str(int(m.group(1)))
        new_street = street_address[: m.start()].strip()
        if new_street:
            return new_street, f'Phường {ward_num}'

    # Pattern 2: P.Linh Chiểu, P.Bình Trị Đông B, P.Tân Định  →  Phường {name}
    m = re.search(
        r'\s+P\.([A-ZÀ-Ỹa-zà-ỹ0-9\s\-]{1,40})\s*$',
        street_address,
    )
    if m:
        ward_name = m.group(1).strip()
        # Sanity check: must look like a Vietnamese place name
        if ward_name and _has_vietnamese(ward_name) and len(ward_name) >= 1:
            new_street = street_address[: m.start()].strip()
            if new_street:
                return new_street, f'Phường {ward_name}'

    # Pattern 3: Xã Vĩnh Lộc A  →  Xã {name}
    m = re.search(
        r'\s+(Xã)\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\-]{1,40})\s*$',
        street_address,
        re.IGNORECASE,
    )
    if m:
        ward_name = m.group(2).strip()
        if ward_name and _has_vietnamese(ward_name) and len(ward_name) >= 1:
            new_street = street_address[: m.start()].strip()
            if new_street:
                return new_street, m.group(1) + ' ' + ward_name

    # Pattern 4: Thị trấn something  →  Thị trấn {name}
    m = re.search(
        r'\s+(Thị trấn)\s+([A-ZÀ-Ỹa-zà-ỹ0-9\s\-]{1,40})\s*$',
        street_address,
        re.IGNORECASE,
    )
    if m:
        ward_name = m.group(2).strip()
        if ward_name and _has_vietnamese(ward_name) and len(ward_name) >= 1:
            new_street = street_address[: m.start()].strip()
            if new_street:
                return new_street, m.group(1) + ' ' + ward_name

    return street_address, None


def _detect_component_type(part: str) -> AddressLevel:
    """Detect the type of address component based on keywords.
    
    Args:
        part: Address component string
        
    Returns:
        AddressLevel: Component type - WARD, DISTRICT, PROVINCE, or STREET
    """
    part_lower = part.lower().strip()
    
    # Ward keywords
    ward_keywords = ['phường', 'phuong', 'xã', 'xa', 'thị trấn', 'thi tran']
    for keyword in ward_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.WARD
    
    # Province keywords (check first to prioritize over district keywords)
    province_keywords = ['tỉnh', 'tinh']
    for keyword in province_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.PROVINCE
    
    # For "thành phố" - need to distinguish between province-level cities and district-level
    # Province-level cities are typically major municipalities
    if part_lower.startswith('thành phố') or part_lower.startswith('thanh pho') \
        or part_lower.startswith('tp ') or part_lower.startswith('tp.'):
        # If it contains multiple words after "thành phố", likely a province
        # Simple heuristic: if there are 3+ words total, it's probably a province
        words = part_lower.split()
        if len(words) >= 3:
            return AddressLevel.PROVINCE
        else:
            return AddressLevel.DISTRICT
    
    # District keywords
    district_keywords = ['quận', 'quan', 'huyện', 'huyen', 'tp', 'thị xã', 'thi xa']
    for keyword in district_keywords:
        if part_lower.startswith(keyword):
            return AddressLevel.DISTRICT
    
    # If no keyword matches, assume it's a street address
    return AddressLevel.STREET


def parse_address(address_string: str) -> Address:
    """Parse an address string into components.
    
    Args:
        address_string: Address string separated by comma, semicolon, pipe, or hyphen in formats:
                       - "district, province" (e.g., "Quận 10, TP Hồ Chí Minh")
                       - "ward, district, province"
                       - "street_address, ward, district, province"
    
    Returns:
        Address: Parsed address with components
    
    Raises:
        ValueError: If address string format is invalid
    """
    if not address_string or not address_string.strip():
        raise ValueError("Address string cannot be empty")

    # Normalize Unicode to NFC so that keyword matching works consistently
    # regardless of whether input is composed (NFC) or decomposed (NFD)
    address_string = unicodedata.normalize("NFC", address_string)

    # Normalize newlines to commas so copy-pasted multi-line addresses parse correctly
    address_string = address_string.replace('\r\n', ', ').replace('\r', ', ').replace('\n', ', ')

    # Try different separators in order of preference
    separators = [',', ';', '|', '-']
    parts = None
    has_empty_slot = False
    
    for separator in separators:
        if separator in address_string:
            raw_parts = [part.strip() for part in address_string.split(separator)]
            has_empty_slot = any(p == '' for p in raw_parts)
            parts = [p for p in raw_parts if p]
            break
    
    if parts is None:
        # No separator found, treat as single component
        parts = [address_string.strip()]
        has_empty_slot = False

    if parts[-1] in ("Việt Nam", "Vienam"):
        # Remove "Việt Nam" if it's the last part
        parts = parts[:-1]
    
    if len(parts) < 2:
        raise ValueError("Address must have at least district and province")
    elif len(parts) == 2:
        # Format: "district, province" (e.g., "Quận 10, TP Hồ Chí Minh")
        district, province = parts
        ward = None
        street_address = None
    elif len(parts) == 3:
        # Use heuristics to determine which components are present
        types = [_detect_component_type(part) for part in parts]
        
        # Initialize all variables
        street_address = None
        ward = None
        district = None
        province = None
        
        # Apply heuristics based on detected types
        # Handle all possible combinations explicitly
        if AddressLevel.WARD in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # All three components detected: ward, district, province
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # street, district, province (missing ward)
            street_address = parts[types.index(AddressLevel.STREET)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # street, ward, province (missing district)
            street_address = parts[types.index(AddressLevel.STREET)]
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
        elif AddressLevel.STREET in types and AddressLevel.WARD in types and AddressLevel.DISTRICT in types:
            # street, ward, district (missing province)
            street_address = parts[types.index(AddressLevel.STREET)]
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
        elif AddressLevel.WARD in types and AddressLevel.DISTRICT in types:
            # ward, district, unknown (assume unknown is province)
            ward = parts[types.index(AddressLevel.WARD)]
            district = parts[types.index(AddressLevel.DISTRICT)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.DISTRICT]:
                    province = part
                    break
        elif AddressLevel.WARD in types and AddressLevel.PROVINCE in types:
            # ward, province, unknown (assume unknown is street)
            ward = parts[types.index(AddressLevel.WARD)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.WARD, AddressLevel.PROVINCE]:
                    street_address = part
                    break
        elif AddressLevel.DISTRICT in types and AddressLevel.PROVINCE in types:
            # district, province, unknown (assume unknown is street)
            district = parts[types.index(AddressLevel.DISTRICT)]
            province = parts[types.index(AddressLevel.PROVINCE)]
            # Find the remaining part
            for i, part in enumerate(parts):
                if types[i] not in [AddressLevel.DISTRICT, AddressLevel.PROVINCE]:
                    street_address = part
                    break
        else:
            # Default: assume ward, district, province format
            ward = parts[0]
            district = parts[1]
            province = parts[2]
    elif len(parts) == 4:
        # Format: "street_address, ward, district, province"
        street_address, ward, district, province = parts
    else:
        # Format: "street_address_part1, street_address_part2, ..., ward, district, province"
        # Take the last 3 parts as ward, district, province
        # Combine the rest as street_address
        ward, district, province = parts[-3:]
        street_address = ", ".join(parts[:-3])
    
    # If ward is missing and the original address had an empty structural slot
    # (e.g. "street, , district, province"), try to recover a ward abbreviation
    # that was embedded in the street component, such as P.06 or P.Linh Chiểu.
    if ward is None and street_address and has_empty_slot:
        extracted_street, extracted_ward = _extract_ward_from_street(street_address)
        if extracted_ward:
            street_address = extracted_street
            ward = extracted_ward

    return Address(
        street_address=street_address if street_address else None,
        ward=ward if ward else None,
        district=district if district else None,
        province=province if province else None
    )