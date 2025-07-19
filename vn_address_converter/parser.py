"""Address parsing functionality for Vietnamese addresses."""

from .models import Address


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
        # Format: "ward, district, province"
        ward, district, province = parts
        street_address = None
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