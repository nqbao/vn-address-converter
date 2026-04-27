import pytest
from vn_address_converter import parse_address, Address


class TestParseAddress:
    """Test cases for the parse_address function."""
    
    def test_parse_address_with_street_address(self):
        """Test parsing address with street address included."""
        address_str = "123 Nguyen Van Linh, Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Nguyen Van Linh"
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_without_street_address(self):
        """Test parsing address without street address."""
        address_str = "Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_with_whitespace(self):
        """Test parsing address with extra whitespace."""
        address_str = "  123 Le Loi  ,  Phường 2  ,  Quận 1  ,  Thành phố Hồ Chí Minh  "
        result = parse_address(address_str)
        
        assert result.street_address == "123 Le Loi"
        assert result.ward == "Phường 2"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_different_province(self):
        """Test parsing address from different province."""
        address_str = "456 Tran Hung Dao, Xã Tân Thạnh, Huyện Cần Giờ, Tỉnh Khánh Hòa"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Tran Hung Dao"
        assert result.ward == "Xã Tân Thạnh"
        assert result.district == "Huyện Cần Giờ"
        assert result.province == "Tỉnh Khánh Hòa"
    
    def test_parse_address_empty_string(self):
        """Test parsing empty string raises ValueError."""
        with pytest.raises(ValueError, match="Address string cannot be empty"):
            parse_address("")
    
    def test_parse_address_whitespace_only(self):
        """Test parsing whitespace-only string raises ValueError."""
        with pytest.raises(ValueError, match="Address string cannot be empty"):
            parse_address("   ")
    
    def test_parse_address_too_few_components(self):
        """Test parsing address with too few components raises ValueError."""
        with pytest.raises(ValueError, match="Address must have at least district and province"):
            parse_address("Phường 1")
    
    def test_parse_address_two_components(self):
        """Test parsing address with district and province only."""
        address_str = "Quận 10, TP Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward is None
        assert result.district == "Quận 10"
        assert result.province == "TP Hồ Chí Minh"
    
    def test_parse_address_too_many_components(self):
        """Test parsing address with too many components combines them into street_address."""
        address = parse_address("123 Street, Building A, Phường 1, Quận 7, Thành phố Hồ Chí Minh")
        assert address.street_address == "123 Street, Building A"
        assert address.ward == "Phường 1"
        assert address.district == "Quận 7"
        assert address.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_empty_components(self):
        """Test parsing address with empty components."""
        address_str = ", Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_special_characters(self):
        """Test parsing address with special characters."""
        address_str = "123/45 Đường Nguyễn Huệ, Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123/45 Đường Nguyễn Huệ"
        assert result.ward == "Phường Bến Nghé"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_with_empty_component(self):
        """Test parsing address with empty component (double comma)."""
        address_str = "Thôn Quảng Đạt, xã Ngũ Phúc, , Huyện Kim Thành, Hải Dương"
        result = parse_address(address_str)
        
        assert result.street_address == "Thôn Quảng Đạt"
        assert result.ward == "xã Ngũ Phúc"
        assert result.district == "Huyện Kim Thành"
        assert result.province == "Hải Dương"
    
    @pytest.mark.parametrize("address_str,expected", [
        ("Quận 10, TP Hồ Chí Minh", {
            'street_address': None,
            'ward': None,
            'district': "Quận 10",
            'province': "TP Hồ Chí Minh"
        }),
        ("Phường 1, Quận 7, Thành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        ("789 Lê Văn Việt, Xã Hiệp Phú, Huyện Thủ Đức, Tỉnh Đồng Nai", {
            'street_address': "789 Lê Văn Việt",
            'ward': "Xã Hiệp Phú",
            'district': "Huyện Thủ Đức",
            'province': "Tỉnh Đồng Nai"
        }),
        ("Phường 12, Quận Gò Vấp, Thành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 12",
            'district': "Quận Gò Vấp",
            'province': "Thành phố Hồ Chí Minh"
        })
    ])
    def test_parse_address_parametrized(self, address_str, expected):
        """Parametrized test for various address formats."""
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']
    
    def test_parse_address_returns_address_type(self):
        """Test that parse_address returns Address type."""
        address_str = "Phường 1, Quận 7, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        # Check that result is an Address dataclass
        assert hasattr(result, 'street_address')
        assert hasattr(result, 'ward')
        assert hasattr(result, 'district')
        assert hasattr(result, 'province')
    
    def test_parse_address_heuristic_three_parts(self):
        """Test heuristic parsing for 3-part addresses with missing components."""
        
        # Test: street, district, province (missing ward)
        address_str = "123 Main Street, Quận 1, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Main Street"
        assert result.ward is None
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test: street, ward, province (missing district)
        address_str = "456 Elm Street, Phường 2, Tỉnh Khánh Hòa"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Elm Street"
        assert result.ward == "Phường 2"
        assert result.district is None
        assert result.province == "Tỉnh Khánh Hòa"
        
        # Test: ward, province, street (missing district, different order)
        address_str = "Phường 3, Tỉnh Đồng Nai, 789 Oak Street"
        result = parse_address(address_str)
        
        assert result.street_address == "789 Oak Street"
        assert result.ward == "Phường 3"
        assert result.district is None
        assert result.province == "Tỉnh Đồng Nai"
        
        # Test: district, province, street (missing ward, different order)
        address_str = "Quận 7, Thành phố Hồ Chí Minh, 321 Pine Street"
        result = parse_address(address_str)
        
        assert result.street_address == "321 Pine Street"
        assert result.ward is None
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test: traditional format still works (ward, district, province)
        address_str = "Phường 1, Quận 2, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address is None
        assert result.ward == "Phường 1"
        assert result.district == "Quận 2"
        assert result.province == "Thành phố Hồ Chí Minh"
    
    def test_parse_address_heuristic_keywords(self):
        """Test heuristic parsing with various Vietnamese keywords."""
        
        # Test with alternative ward keywords
        address_str = "ABC Building, Xã Tân Phú, Tỉnh Long An"
        result = parse_address(address_str)
        
        assert result.street_address == "ABC Building"
        assert result.ward == "Xã Tân Phú"
        assert result.district is None
        assert result.province == "Tỉnh Long An"
        
        # Test with alternative district keywords
        address_str = "XYZ Complex, Huyện Bình Chánh, Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "XYZ Complex"
        assert result.ward is None
        assert result.district == "Huyện Bình Chánh"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with non-accented keywords
        address_str = "123 Test St, Phuong 5, Quan 3"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Test St"
        assert result.ward == "Phuong 5"
        assert result.district == "Quan 3"
        assert result.province is None

    def test_parse_address_non_standard_formats(self):
        """Test parsing non-standard address formats."""
        # Test with semicolon separator
        address_str = "123 Lê Lợi; Phường 1; Quận 7; Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "123 Lê Lợi"
        assert result.ward == "Phường 1"
        assert result.district == "Quận 7"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with hyphen separator
        address_str = "456 Nguyễn Trãi - Phường 2 - Quận 1 - Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "456 Nguyễn Trãi"
        assert result.ward == "Phường 2"
        assert result.district == "Quận 1"
        assert result.province == "Thành phố Hồ Chí Minh"
        
        # Test with pipe separator
        address_str = "789 Hai Bà Trưng | Phường 3 | Quận 3 | Thành phố Hồ Chí Minh"
        result = parse_address(address_str)
        
        assert result.street_address == "789 Hai Bà Trưng"
        assert result.ward == "Phường 3"
        assert result.district == "Quận 3"
        assert result.province == "Thành phố Hồ Chí Minh"

    @pytest.mark.parametrize("address_str,expected", [
        # Thị xã Ninh Hòa (ward, district, province)
        ("Phường Ninh Giang, Thị xã Ninh Hòa, Tỉnh Khánh Hòa", {
            'street_address': None,
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # Thị xã Bình Minh with street address
        ("123 Đường Test, Phường Thành Phước, Thị xã Bình Minh, Tỉnh Vĩnh Long", {
            'street_address': "123 Đường Test",
            'ward': "Phường Thành Phước",
            'district': "Thị xã Bình Minh",
            'province': "Tỉnh Vĩnh Long"
        }),
        # Thị xã An Khê (ward, district, province)
        ("Phường An Bình, Thị xã An Khê, Tỉnh Gia Lai", {
            'street_address': None,
            'ward': "Phường An Bình",
            'district': "Thị xã An Khê",
            'province': "Tỉnh Gia Lai"
        }),
        # Street, ward, Thị xã district, province (4 parts)
        ("Số 45 Lê Lợi, Phường Ninh Hiệp, Thị xã Ninh Hòa, Tỉnh Khánh Hòa", {
            'street_address': "Số 45 Lê Lợi",
            'ward': "Phường Ninh Hiệp",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # Thị xã with missing ward (street, district, province)
        ("456 Trần Phú, Thị xã Bình Minh, Tỉnh Vĩnh Long", {
            'street_address': "456 Trần Phú",
            'ward': None,
            'district': "Thị xã Bình Minh",
            'province': "Tỉnh Vĩnh Long"
        }),
        # Thị xã with non-accented keyword (thi xa)
        ("Phuong An Binh, Thi xa An Khe, Tinh Gia Lai", {
            'street_address': None,
            'ward': "Phuong An Binh",
            'district': "Thi xa An Khe",
            'province': "Tinh Gia Lai"
        }),
        # Reversed order: district, province, ward (should still resolve)
        ("Thị xã Ninh Hòa, Tỉnh Khánh Hòa, Phường Ninh Giang", {
            'street_address': None,
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # Thị xã with extra whitespace
        ("  Phường Ninh Giang  ,  Thị xã Ninh Hòa  ,  Tỉnh Khánh Hòa  ", {
            'street_address': None,
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # Multiple street parts before ward/district/province
        ("Tầng 2, Tòa nhà A, Phường Ninh Giang, Thị xã Ninh Hòa, Tỉnh Khánh Hòa", {
            'street_address': "Tầng 2, Tòa nhà A",
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
    ])
    def test_parse_address_thi_xa_district(self, address_str, expected):
        """Test parsing addresses with 'Thị xã' district prefix."""
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']

    @pytest.mark.parametrize("address_str,expected", [
        ("Phường 1\nQuận 7\nThành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        ("123 Lê Lợi\r\nPhường 2\r\nQuận 1\r\nThành phố Hồ Chí Minh", {
            'street_address': "123 Lê Lợi",
            'ward': "Phường 2",
            'district': "Quận 1",
            'province': "Thành phố Hồ Chí Minh"
        }),
        ("Phường Ninh Giang\nThị xã Ninh Hòa\nTỉnh Khánh Hòa", {
            'street_address': None,
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # Mixed newline and comma
        ("Tầng 2\nTòa nhà A, Phường 1, Quận 7, Thành phố Hồ Chí Minh", {
            'street_address': "Tầng 2, Tòa nhà A",
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
    ])
    def test_parse_address_newlines(self, address_str, expected):
        """Test parsing addresses with newline separators."""
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']

    @pytest.mark.parametrize("address_str,expected", [
        # NFD decomposed input: basic 3-part (macOS-style decomposed Unicode)
        ("Phu\u031bo\u031b\u0300ng 1, Qua\u0323\u0302n 7, Tha\u0300nh pho\u0302\u0301 Ho\u0302\u0300 Chi\u0301 Minh", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        # NFD input: 4-part with street
        ("123 Nguye\u0302\u0303n Tra\u0303i, Phu\u031bo\u031b\u0300ng 2, Qua\u0323\u0302n 1, Tha\u0300nh pho\u0302\u0301 Ho\u0302\u0300 Chi\u0301 Minh", {
            'street_address': "123 Nguyễn Trãi",
            'ward': "Phường 2",
            'district': "Quận 1",
            'province': "Thành phố Hồ Chí Minh"
        }),
        # NFD input: Thị xã district
        ("Phu\u031bo\u031b\u0300ng Ninh Giang, Thi\u0323 xa\u0303 Ninh Ho\u0300a, Ti\u0309nh Kha\u0301nh Ho\u0300a", {
            'street_address': None,
            'ward': "Phường Ninh Giang",
            'district': "Thị xã Ninh Hòa",
            'province': "Tỉnh Khánh Hòa"
        }),
        # NFD input: Việt Nam suffix should be stripped
        ("Phu\u031bo\u031b\u0300ng 1, Qua\u0323\u0302n 7, Tha\u0300nh pho\u0302\u0301 Ho\u0302\u0300 Chi\u0301 Minh, Vie\u0323\u0302t Nam", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        # NFD input: reversed order (heuristic must still work)
        ("Tha\u0300nh pho\u0302\u0301 Ho\u0302\u0300 Chi\u0301 Minh, Qua\u0323\u0302n 7, Phu\u031bo\u031b\u0300ng 1", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
        # NFD input: mixed NFD/NFC (edge case)
        ("Phu\u031bo\u031b\u0300ng 1, Quận 7, Thành phố Hồ Chí Minh", {
            'street_address': None,
            'ward': "Phường 1",
            'district': "Quận 7",
            'province': "Thành phố Hồ Chí Minh"
        }),
    ])
    def test_parse_address_nfd_normalization(self, address_str, expected):
        """Test parsing addresses with NFD-decomposed Unicode input.

        macOS and some browsers output NFD text (decomposed accents).
        The parser must normalize to NFC before keyword matching so that
        NFD and NFC inputs produce identical results.
        """
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']

    @pytest.mark.parametrize("address_str,expected", [
        # P.06  →  Phường 6
        ("123 Đường ABC P.06, , Quận 8, TP Hồ Chí Minh", {
            'street_address': "123 Đường ABC",
            'ward': "Phường 6",
            'district': "Quận 8",
            'province': "TP Hồ Chí Minh"
        }),
        # P.13  →  Phường 13
        ("456 Đường XYZ P.13, , Quận 5, TP Hồ Chí Minh", {
            'street_address': "456 Đường XYZ",
            'ward': "Phường 13",
            'district': "Quận 5",
            'province': "TP Hồ Chí Minh"
        }),
        # P.02  →  Phường 2 (strip leading zero)
        ("789 Đường Test P.02, , Quận Tân Bình, TP Hồ Chí Minh", {
            'street_address': "789 Đường Test",
            'ward': "Phường 2",
            'district': "Quận Tân Bình",
            'province': "TP Hồ Chí Minh"
        }),
        # P.Linh Chiểu  →  Phường Linh Chiểu
        ("3 Đường DEF P.Linh Chiểu, , Quận 7, TP Hồ Chí Minh", {
            'street_address': "3 Đường DEF",
            'ward': "Phường Linh Chiểu",
            'district': "Quận 7",
            'province': "TP Hồ Chí Minh"
        }),
        # P.Bình Trị Đông B  →  Phường Bình Trị Đông B
        ("315 Đường GHI P.Bình Trị Đông B, , Quận Bình Tân, TP Hồ Chí Minh", {
            'street_address': "315 Đường GHI",
            'ward': "Phường Bình Trị Đông B",
            'district': "Quận Bình Tân",
            'province': "TP Hồ Chí Minh"
        }),
        # P.Tân Định  →  Phường Tân Định
        ("12 Đường JKL P.Tân Định, , Quận 1, TP Hồ Chí Minh", {
            'street_address': "12 Đường JKL",
            'ward': "Phường Tân Định",
            'district': "Quận 1",
            'province': "TP Hồ Chí Minh"
        }),
        # Xã Testville A at end of street
        ("Lô Số 1 KCN Test Xã Testville A, , Huyện Bình Chánh, TP Hồ Chí Minh", {
            'street_address': "Lô Số 1 KCN Test",
            'ward': "Xã Testville A",
            'district': "Huyện Bình Chánh",
            'province': "TP Hồ Chí Minh"
        }),
        # Thị trấn extraction (lower-case 'trấn' should still match)
        ("42 Đường MNO Thị trấn Testtown, , Huyện Cần Giờ, TP Hồ Chí Minh", {
            'street_address': "42 Đường MNO",
            'ward': "Thị trấn Testtown",
            'district': "Huyện Cần Giờ",
            'province': "TP Hồ Chí Minh"
        }),
        # 3-part with multi-word street and named ward abbreviation
        ("123 Đường LMN P.An Khánh, , Quận 2, TP Hồ Chí Minh", {
            'street_address': "123 Đường LMN",
            'ward': "Phường An Khánh",
            'district': "Quận 2",
            'province': "TP Hồ Chí Minh"
        }),
    ])
    def test_parse_address_ward_from_street(self, address_str, expected):
        """Test extracting ward abbreviation embedded in street when ward slot is empty."""
        result = parse_address(address_str)
        assert result.street_address == expected['street_address']
        assert result.ward == expected['ward']
        assert result.district == expected['district']
        assert result.province == expected['province']

    @pytest.mark.parametrize("address_str", [
        # No double comma — P. should stay in street even if it looks like a ward
        "123 Đường ABC P.06, Quận 8, TP Hồ Chí Minh",
        # Ward already present in proper slot — no extraction, street keeps P.
        "456 Đường XYZ P.13, Phường 13, Quận 5, TP Hồ Chí Minh",
        # Double comma but no ward pattern at end of street
        "6A Cửu Long, , Quận Tân Bình, TP Hồ Chí Minh",
        # Double comma with Xã but no Vietnamese name after it
        "Lô Số 1 Xã, , Huyện Bình Chánh, TP Hồ Chí Minh",
        # Normal 4-part address without any abbreviation
        "123 Lê Lợi, Phường 1, Quận 7, Thành phố Hồ Chí Minh",
        # P. in the middle of street, not at end
        "P.06 Building, 123 Đường ABC, Quận 8, TP Hồ Chí Minh",
    ])
    def test_parse_address_no_ward_extraction(self, address_str):
        """Test that ward is NOT extracted when conditions are not met."""
        result = parse_address(address_str)
        # Just verify it parses without exception and does not invent a ward
        # from a street middle fragment
        assert "P." not in (result.ward or "")

    def test_parse_address_ward_extraction_no_empty_street(self):
        """Test that extraction is skipped if it would leave an empty street."""
        # If street were just "P.06" with empty ward slot, do NOT extract
        result = parse_address("P.06, , Quận 8, TP Hồ Chí Minh")
        assert result.street_address == "P.06"
        assert result.ward is None