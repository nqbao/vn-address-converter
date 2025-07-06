#!/usr/bin/env python3
"""
Simple script to extract all tables and their headings from wiki.html
Returns raw HTML without parsing table contents
"""

from bs4 import BeautifulSoup
import json

def extract_tables_and_headings_html(html_file):
    """
    Extract all tables with class 'wikitable' and their associated headings from HTML file.
    Returns raw HTML without parsing table contents.
    
    Args:
        html_file (str): Path to the HTML file
        
    Returns:
        list: List of dictionaries containing table HTML and heading information
    """
    
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all tables with class "wikitable"
    tables = soup.find_all('table', class_='wikitable')
    
    extracted_data = []
    
    for i, table in enumerate(tables):
        table_info = {
            'table_index': i + 1,
            'heading_html': None,
            'heading_text': None,
            'table_html': str(table),
            'table_classes': table.get('class', [])
        }
        
        # Find the preceding heading for this table
        # Look for div elements with class "mw-heading" that appear before the table
        current_element = table
        
        # Search backwards for the nearest mw-heading div
        while current_element:
            current_element = current_element.find_previous_sibling()
            if current_element:
                # Check if it's a mw-heading div
                if (current_element.name == 'div' and 
                    current_element.get('class') and 
                    'mw-heading' in current_element.get('class', [])):
                    
                    # Extract the heading HTML and text
                    table_info['heading_html'] = str(current_element)
                    heading_element = current_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if heading_element:
                        table_info['heading_text'] = heading_element.get_text(strip=True)
                    break
        
        extracted_data.append(table_info)
    
    return extracted_data

def save_to_json(data, output_file):
    """Save extracted data to JSON file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def print_summary(data):
    """Print a summary of extracted tables"""
    print(f"Total tables found: {len(data)}")
    print("="*60)
    
    for table in data:
        print(f"\nTable {table['table_index']}:")
        print(f"Heading: {table['heading_text']}")
        print(f"Table classes: {', '.join(table['table_classes'])}")
        print(f"Table HTML length: {len(table['table_html'])} characters")
        print(f"Heading HTML length: {len(table['heading_html']) if table['heading_html'] else 0} characters")
        print("-" * 40)

def main():
    html_file = 'wiki.html'
    output_file = 'extracted_tables_html.json'
    
    print("Extracting tables and headings HTML from wiki.html...")
    
    # Extract tables and headings
    extracted_data = extract_tables_and_headings_html(html_file)
    
    # Save to JSON
    save_to_json(extracted_data, output_file)
    print(f"Data saved to {output_file}")
    
    # Print summary
    print_summary(extracted_data)
    
    # Create a simple text report
    report_file = 'tables_html_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("TABLES AND HEADINGS HTML EXTRACTION REPORT\n")
        f.write("="*60 + "\n")
        f.write(f"Total tables found: {len(extracted_data)}\n\n")
        
        for table in extracted_data:
            f.write(f"TABLE {table['table_index']}\n")
            f.write(f"Heading: {table['heading_text']}\n")
            f.write(f"Classes: {', '.join(table['table_classes'])}\n")
            f.write(f"Table HTML length: {len(table['table_html'])} characters\n")
            f.write(f"Heading HTML length: {len(table['heading_html']) if table['heading_html'] else 0} characters\n")
            f.write("-" * 40 + "\n\n")
    
    print(f"Text report saved to {report_file}")

if __name__ == "__main__":
    main()
