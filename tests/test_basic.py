"""
Basic functionality tests for vn-address-converter.
"""
from vn_address_converter import convert_address, Address
import pytest

@pytest.mark.parametrize("address,expected", [
    (
        Address(
            street="720A Điện Biên Phủ",
            ward="Phường 22",
            district="Quận Bình Thạnh",
            province="Thành phố Hồ Chí Minh"
        ),
        Address(
            street="720A Điện Biên Phủ",
            ward="Phường Thạnh Mỹ Tây",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        Address(
            street="1 P. Nhà Thờ",
            ward="Phường Hàng Trống",
            district="Quận Hoàn Kiếm",
            province="Thành phố Hà Nội"
        ),
        Address(
            street="1 P. Nhà Thờ",
            ward="Phường Hoàn Kiếm",
            district=None,
            province="Thành phố Hà Nội"
        )
    ),
    (
        # case insensitive ward and district
        Address(
            street="07 Công trường Lam Sơn",
            ward="phường bến nghé",
            district="quận 1",
            province="thành phố hồ chí minh"
        ),
        Address(
            street="07 Công trường Lam Sơn",
            ward="Phường Sài Gòn",
            district=None,
            province="Thành phố Hồ Chí Minh"
        )
    ),
    (
        # test aliases
        Address(
            street="51 Lê Lợi",
            ward="Phú Hội",
            district="Thuận Hóa",
            province="Huế"
        ),
        Address(
            street="51 Lê Lợi",
            ward="Phường Thuận Hóa",
            district=None,
            province="Thành phố Huế"
        )
    ),
])
def test_convert_address_table(address, expected):
    result = convert_address(address)
    assert result == expected
