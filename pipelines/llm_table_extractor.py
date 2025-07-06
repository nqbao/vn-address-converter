#!/usr/bin/env python3
"""
Enhanced HTML Table Mapper with LLM

This script creates a mapping from (Cấp huyện cũ, Cấp xã cũ) -> Cấp xã mới
by parsing HTML table data with LLM assistance for better text extraction and mapping.
"""

import json
import re
import os
from typing import Dict, Tuple, List, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai


class LLMTableMapper:
    def __init__(self):
        """Initialize the LLM table mapper."""
        load_dotenv()
        
        # Setup OpenAI client
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
        
    def extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        if not html_content:
            return ""
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text = soup.get_text()
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        text = text.strip()
        
        return text

    def parse_table_with_llm(self, table_html: str) -> List[Dict]:
        """
        Use LLM to parse the table and extract structured data.
        """
        # Extract text from HTML for LLM processing
        soup = BeautifulSoup(table_html, 'html.parser')
        
        # Get table rows for analysis
        rows = soup.find('tbody').find_all('tr') if soup.find('tbody') else soup.find_all('tr')
        
        # Create a simplified text representation for LLM
        table_text = []
        for i, row in enumerate(rows):
            cells = row.find_all(['td', 'th'])
            cell_texts = []
            for cell in cells:
                text = self.extract_text_from_html(str(cell))
                rowspan = cell.get('rowspan', '1')
                colspan = cell.get('colspan', '1')
                cell_texts.append(f"{text} (rowspan:{rowspan}, colspan:{colspan})")
            table_text.append(f"Row {i}: {' | '.join(cell_texts)}")
        
        table_text_str = "\n".join(table_text)
        
        prompt = f"""
Analyze this Vietnamese administrative table and extract mappings. The table has 4 columns:
1. Cấp huyện cũ (Old district level)
2. Cấp xã cũ (Old commune/ward level) 
3. Cấp xã mới (New commune/ward level)
4. Nguồn (Source)

Table data:
{table_text_str}

Please extract mappings in the format (Cấp huyện cũ, Cấp xã cũ) -> Cấp xã mới.

Rules:
1. Handle rowspan properly - when a district cell has rowspan > 1, it applies to multiple rows
2. When Cấp xã cũ contains multiple entries separated by breaks, create separate mappings for each
3. When Cấp xã cũ is empty or missing, use empty string ""
4. Clean up text by removing HTML tags and extra whitespace
5. Extract just the administrative unit names, removing links and extra text

Return the result as a JSON object where keys are "district|old_commune" and values are "new_commune".
Do not return any code or explanations, just the JSON object.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": "You are an expert in Vietnamese administrative divisions and HTML table parsing. Extract mappings accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    print("Failed to parse JSON from LLM response")
                    return {}
            else:
                print("No JSON found in LLM response")
                return {}
                
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {}

    def build_mapping_from_table(self, table_html: str) -> Dict[Tuple[str, str], str]:
        """
        Build mapping from HTML table using LLM assistance.
        """
        # Parse table with LLM
        llm_result = self.parse_table_with_llm(table_html)
        
        mapping = {}
        
        if llm_result:
            # Convert LLM result to our format
            for key, value in llm_result.items():
                if '|' in key:
                    parts = key.split('|', 1)
                    if len(parts) == 2:
                        district, old_commune = parts
                        mapping[(district.strip(), old_commune.strip())] = value.strip()
        else:
            print("LLM parsing failed or returned empty")
        
        return mapping

    def process_table(self, table_index: int) -> Dict[Tuple[str, str], str]:
        """
        Process a specific table by index.
        """
        # Read the extracted tables JSON file
        try:
            with open('extracted_tables_html.json', 'r', encoding='utf-8') as f:
                tables_data = json.load(f)
        except FileNotFoundError:
            print("extracted_tables_html.json not found!")
            return {}
        
        # Find the target table
        target_table = None
        for table in tables_data:
            if table.get('table_index') == table_index:
                target_table = table
                break
        
        if not target_table:
            print(f"Table index {table_index} not found!")
            return {}
        
        print(f"Processing table: {target_table['heading_text']}")
        
        # Build mapping from the table
        table_html = target_table['table_html']
        mapping = self.build_mapping_from_table(table_html)
        
        return mapping

    def save_mapping(self, mapping: Dict[Tuple[str, str], str], filename: str):
        """
        Save mapping to JSON file.
        """
        # Convert tuple keys to string format for JSON serialization
        mapping_for_json = {f"{k[0]}|{k[1]}": v for k, v in mapping.items()}
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(mapping_for_json, f, ensure_ascii=False, indent=2)
        
        print(f"Mapping saved to {filename}")

    def load_mapping(self, filename: str) -> Dict[Tuple[str, str], str]:
        """
        Load mapping from JSON file.
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                mapping_json = json.load(f)
            
            # Convert string keys back to tuple format
            mapping = {}
            for key, value in mapping_json.items():
                if '|' in key:
                    parts = key.split('|', 1)
                    if len(parts) == 2:
                        mapping[(parts[0], parts[1])] = value
            
            return mapping
        except FileNotFoundError:
            print(f"File {filename} not found!")
            return {}


def main():
    """Main function to demonstrate the enhanced mapper."""
    import sys
    
    mapper = LLMTableMapper()
    
    # Get table index from command line argument or use default
    table_index = 2  # Default value
    if len(sys.argv) > 1:
        try:
            table_index = int(sys.argv[1])
        except ValueError:
            print("Error: Table index must be a number")
            print("Usage: python llm_table_extractor.py [table_index]")
            return
    
    # Check if output file already exists
    output_filename = f'table_{table_index}_mapping.json'
    if os.path.exists(output_filename):
        print(f"Output file '{output_filename}' already exists. Skipping processing.")
        return
    
    print(f"Processing table index: {table_index}")
    mapping = mapper.process_table(table_index)
    
    if mapping:
        print(f"\nCreated {len(mapping)} mapping entries:")
        print("\nSample mappings:")
        
        # Show first 10 mappings as examples
        count = 0
        for (huyen, xa_cu), xa_moi in mapping.items():
            if count >= 10:
                break
            print(f"  ('{huyen}', '{xa_cu}') -> '{xa_moi}'")
            count += 1
        
        # Show some specific examples with empty old commune
        print("\nExamples with empty old commune:")
        empty_count = 0
        for (huyen, xa_cu), xa_moi in mapping.items():
            if not xa_cu and empty_count < 5:  # Empty old commune
                print(f"  ('{huyen}', '') -> '{xa_moi}'")
                empty_count += 1
        
        # Save mapping to JSON file
        mapper.save_mapping(mapping, output_filename)
        
        print(f"\nTotal mappings: {len(mapping)}")
    else:
        print("No mappings created.")


if __name__ == "__main__":
    main()
