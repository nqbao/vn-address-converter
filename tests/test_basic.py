"""
Basic functionality tests for vn-address-converter.
"""
import pytest
from vn_address_converter import convert_address, Address


def test_convert_address():
    """Test converting a simple address."""
    address = Address(
        street="123 Main St",
        ward="Ward 1",
        district="District 1",
        city="Ho Chi Minh City"
    )
    
    result = convert_address(address)
    
    assert result["street"] == "123 Main St"
    assert result["ward"] == "Ward 1"
    assert result["district"] == "District 1"
    assert result["city"] == "Ho Chi Minh City"
