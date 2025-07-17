import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(__file__))

from vn_address_converter.converter import convert_to_new_address, parse_address, Address

def main():
    st.title("🏛️ Vietnam Address Converter")
    st.write("Convert old Vietnamese addresses to the new administrative format (2024-2025 reform)")
    
    # Input methods
    input_method = st.radio("Choose input method:", ["Parse from string", "Manual input"])
    
    if input_method == "Manual input":
        st.subheader("Manual Address Input")
        
        col1, col2 = st.columns(2)
        
        with col1:
            street = st.text_input("Street Address (optional)", placeholder="e.g., 123 Nguyen Trai")
            ward = st.text_input("Ward/Commune *", placeholder="e.g., Phường Bến Thành")
            
        with col2:
            district = st.text_input("District *", placeholder="e.g., Quận 1")
            province = st.text_input("Province/City *", placeholder="e.g., Thành phố Hồ Chí Minh")
        
        if st.button("Convert Address", type="primary"):
            if not all([ward, district, province]):
                st.error("Please fill in all required fields (Ward, District, Province)")
            else:
                try:
                    address = Address(
                        street_address=street if street else None,
                        ward=ward,
                        district=district,
                        province=province
                    )
                    converted = convert_to_new_address(address)
                    
                    st.success("✅ Address converted successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Address")
                        st.write(f"**Street:** {address.get('street_address') or 'N/A'}")
                        st.write(f"**Ward:** {address.get('ward')}")
                        st.write(f"**District:** {address.get('district')}")
                        st.write(f"**Province:** {address.get('province')}")
                    
                    with col2:
                        st.subheader("New Address")
                        st.write(f"**Street:** {converted.get('street_address') or 'N/A'}")
                        st.write(f"**Ward:** {converted.get('ward')}")
                        st.write(f"**District:** {converted.get('district') or 'N/A (eliminated)'}")
                        st.write(f"**Province:** {converted.get('province')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    else:
        st.subheader("Parse Address from String")
        
        st.info("Enter address in format: `street, ward, district, province` or `ward, district, province`")
        st.write("Supported separators: comma (,), semicolon (;), pipe (|), hyphen (-)")
        
        # Initialize session state for selected example
        if 'selected_example' not in st.session_state:
            st.session_state.selected_example = ""
        
        address_string = st.text_area(
            "Address String",
            value=st.session_state.selected_example,
            placeholder="e.g., 123 Nguyen Trai, Phường Bến Thành, Quận 1, Thành phố Hồ Chí Minh",
            height=100
        )
        
        # Example addresses
        examples = [
            "Phường Bến Thành, Quận 1, Thành phố Hồ Chí Minh",
            "123 Nguyen Trai; Phường Bến Thành; Quận 1; Thành phố Hồ Chí Minh",
            "Xã Tân Phú | Huyện Châu Thành | Tỉnh Long An",
            "456 Le Loi - Phường 1 - Quận 3 - TP.HCM"
        ]
        
        selected_example = st.selectbox(
            "Or choose an example:",
            [""] + examples,
            format_func=lambda x: "Select an example..." if x == "" else x,
            key="example_dropdown"
        )
        
        # Update the session state if a new example is selected
        if selected_example and selected_example != st.session_state.selected_example:
            st.session_state.selected_example = selected_example
            st.rerun()
        
        if st.button("Parse and Convert", type="primary"):
            if not address_string.strip():
                st.error("Please enter an address string")
            else:
                try:
                    # First parse the address
                    parsed = parse_address(address_string)
                    
                    st.success("✅ Address parsed successfully!")
                    
                    # Show parsed components
                    with st.expander("Parsed Components"):
                        st.write(f"**Street:** {parsed.street_address or 'N/A'}")
                        st.write(f"**Ward:** {parsed.ward or 'N/A'}")
                        st.write(f"**District:** {parsed.district or 'N/A'}")
                        st.write(f"**Province:** {parsed.province or 'N/A'}")

                    # Convert to new format
                    converted = convert_to_new_address(parsed)
                    
                    st.success("✅ Address converted successfully!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.subheader("Original Address")
                        st.write(f"**Street:** {parsed.street_address or 'N/A'}")
                        st.write(f"**Ward:** {parsed.ward or 'N/A'}")
                        st.write(f"**District:** {parsed.district or 'N/A'}")
                        st.write(f"**Province:** {parsed.province or 'N/A'}")

                    with col2:
                        st.subheader("New Address")
                        st.write(f"**Street:** {converted.street_address or 'N/A'}")
                        st.write(f"**Ward:** {converted.ward or 'N/A'}")
                        st.write(f"**Province:** {converted.province or 'N/A'}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()