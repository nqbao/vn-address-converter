"""Mapping data loading and caching functionality for Vietnamese address conversion."""

import json
import os
from .models import AddressLevel
from .aliases import get_aliases

# Path constants
WARD_MAPPING_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ward_mapping.json')
MANUAL_ALIASES_PATH = os.path.join(os.path.dirname(__file__), 'data', 'manual_aliases.json')

# Global caches
WARD_MAPPING = None
MANUAL_ALIASES = None


def get_manual_aliases():
    """Load manual aliases data from JSON file."""
    global MANUAL_ALIASES
    if MANUAL_ALIASES is None:
        try:
            with open(MANUAL_ALIASES_PATH, encoding='utf-8') as f:
                MANUAL_ALIASES = json.load(f)
        except FileNotFoundError:
            MANUAL_ALIASES = {"provinces": {}, "districts": {}, "wards": {}}
    return MANUAL_ALIASES


def get_ward_mapping():
    """Load and process ward mapping data with aliases."""
    global WARD_MAPPING
    if WARD_MAPPING is None:
        with open(WARD_MAPPING_PATH, encoding='utf-8') as f:
            mapping = json.load(f)
        
        manual_aliases = get_manual_aliases()
        
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