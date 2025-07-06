import json
import sys
from collections import defaultdict

def nested_dict():
    return defaultdict(nested_dict)

def convert(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    result = nested_dict()
    for item in data:
        old_province = item['old_province_name']
        old_district = item['old_district_name']
        old_ward = item['old_ward_name']
        new_province = item['new_province_name']
        new_ward = item['new_ward_name']
        result[old_province][old_district][old_ward] = {
            'new_provine_name': new_province,
            'new_ward_name': new_ward
        }

    # Convert defaultdicts to dicts
    def to_dict(d):
        if isinstance(d, defaultdict):
            d = {k: to_dict(v) for k, v in d.items()}
        return d

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(to_dict(result), f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_json> <output_json>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
