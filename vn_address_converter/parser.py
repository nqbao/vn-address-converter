"""Address parsing functionality for Vietnamese addresses."""

import re
from .models import Address, AddressLevel


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
    district_keywords = ['quận', 'quan', 'huyện', 'huyen', 'tp']
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
    
    # Try different separators in order of preference
    separators = [',', ';', '|', '-']
    parts = None
    
    for separator in separators:
        if separator in address_string:
            parts = [part.strip() for part in address_string.split(separator) if part.strip()]
            break
    
    if parts is None:
        # No separator found, treat as single component
        parts = [address_string.strip()]

    if parts[-1].lower() in ("việt nam", "vietnam", "vn"):
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
    
    return Address(
        street_address=street_address if street_address else None,
        ward=ward if ward else None,
        district=district if district else None,
        province=province if province else None
    )