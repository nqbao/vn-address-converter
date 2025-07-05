from typing import TypedDict

class Address(TypedDict):
    street: str | None
    ward: str | None
    district: str | None
    city: str | None


def convert_address(address: Address) -> Address:
    new_address = Address(
        street=address.get('street'),
        ward=address.get('ward'),
        district=address.get('district'),
        city=address.get('city')
    )

    return new_address
