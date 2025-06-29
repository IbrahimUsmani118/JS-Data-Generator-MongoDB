#!/usr/bin/env python3
"""
Data Export Module - Optimized version
Provides functionality for exporting data to various formats with validation and error handling.
"""

import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import os
import sys


class DataExporter:
    """A class to handle data export to various formats with validation and error handling."""
    
    def __init__(self):
        self.supported_formats = ['csv', 'json', 'xml', 'excel', 'parquet']
        self.export_history = []
    
    def validate_data(self, data_list: List[Dict[str, Any]]) -> bool:
        """Validate input data structure."""
        if not isinstance(data_list, list):
            raise ValueError("Data must be a list of dictionaries")
        
        if not data_list:
            raise ValueError("Data list cannot be empty")
        
        for i, item in enumerate(data_list):
            if not isinstance(item, dict):
                raise ValueError(f"Item at index {i} must be a dictionary")
            
            if not item:
                raise ValueError(f"Item at index {i} cannot be empty")
        
        return True
    
    def export_to_csv(self, data_list: List[Dict[str, Any]], filename: str, 
                     encoding: str = 'utf-8') -> bool:
        """Export data to CSV format with improved error handling."""
        try:
            if not filename.endswith('.csv'):
                filename += '.csv'
            
            # Get all unique keys from all dictionaries
            all_keys = set()
            for item in data_list:
                all_keys.update(item.keys())
            
            # Sort keys for consistent output
            fieldnames = sorted(list(all_keys))
            
            with open(filename, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for item in data_list:
                    # Fill missing keys with empty strings
                    row = {key: item.get(key, '') for key in fieldnames}
                    writer.writerow(row)
            
            self._log_export('csv', filename, len(data_list))
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def export_to_json(self, data_list: List[Dict[str, Any]], filename: str, 
                      pretty_print: bool = True) -> bool:
        """Export data to JSON format with improved formatting."""
        try:
            if not filename.endswith('.json'):
                filename += '.json'
            
            export_data = {
                "metadata": {
                    "exported_at": datetime.now().isoformat(),
                    "total_records": len(data_list),
                    "format": "json"
                },
                "data": data_list
            }
            
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                if pretty_print:
                    json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
                else:
                    json.dump(export_data, jsonfile, ensure_ascii=False)
            
            self._log_export('json', filename, len(data_list))
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_xml(self, data_list: List[Dict[str, Any]], filename: str, 
                     root_name: str = "data", item_name: str = "item") -> bool:
        """Export data to XML format with improved structure."""
        try:
            if not filename.endswith('.xml'):
                filename += '.xml'
            
            root = ET.Element(root_name)
            
            # Add metadata
            metadata = ET.SubElement(root, "metadata")
            ET.SubElement(metadata, "exported_at").text = datetime.now().isoformat()
            ET.SubElement(metadata, "total_records").text = str(len(data_list))
            ET.SubElement(metadata, "format").text = "xml"
            
            # Add data
            data_element = ET.SubElement(root, "records")
            for i, row in enumerate(data_list):
                item_element = ET.SubElement(data_element, item_name, id=str(i))
                for key, value in row.items():
                    # Clean key name for XML
                    clean_key = key.replace(' ', '_').replace('-', '_')
                    column_element = ET.SubElement(item_element, clean_key)
                    column_element.text = str(value) if value is not None else ""
            
            # Create pretty XML
            rough_string = ET.tostring(root, encoding='unicode')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="  ")
            
            with open(filename, 'w', encoding='utf-8') as xmlfile:
                xmlfile.write(pretty_xml)
            
            self._log_export('xml', filename, len(data_list))
            return True
            
        except Exception as e:
            print(f"Error exporting to XML: {e}")
            return False
    
    def export_to_excel(self, data_list: List[Dict[str, Any]], filename: str) -> bool:
        """Export data to Excel format using pandas."""
        try:
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            df = pd.DataFrame(data_list)
            
            # Add metadata as a separate sheet
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
                
                # Create metadata sheet
                metadata_df = pd.DataFrame([{
                    'Exported At': datetime.now().isoformat(),
                    'Total Records': len(data_list),
                    'Format': 'excel',
                    'Columns': len(df.columns)
                }])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
            
            self._log_export('excel', filename, len(data_list))
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
    
    def export_to_parquet(self, data_list: List[Dict[str, Any]], filename: str) -> bool:
        """Export data to Parquet format for efficient storage."""
        try:
            if not filename.endswith('.parquet'):
                filename += '.parquet'
            
            df = pd.DataFrame(data_list)
            df.to_parquet(filename, index=False)
            
            self._log_export('parquet', filename, len(data_list))
            return True
            
        except Exception as e:
            print(f"Error exporting to Parquet: {e}")
            return False
    
    def _log_export(self, format_type: str, filename: str, record_count: int):
        """Log export operations."""
        self.export_history.append({
            'timestamp': datetime.now().isoformat(),
            'format': format_type,
            'filename': filename,
            'records': record_count
        })
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """Get export history."""
        return self.export_history.copy()
    
    def export_data(self, data_list: List[Dict[str, Any]], format_type: str, 
                   filename: Optional[str] = None) -> bool:
        """Main export function that handles all formats."""
        try:
            # Validate data
            self.validate_data(data_list)
            
            # Generate filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"exported_data_{timestamp}"
            
            # Export based on format
            format_type = format_type.lower()
            if format_type == 'csv':
                return self.export_to_csv(data_list, filename)
            elif format_type == 'json':
                return self.export_to_json(data_list, filename)
            elif format_type == 'xml':
                return self.export_to_xml(data_list, filename)
            elif format_type == 'excel':
                return self.export_to_excel(data_list, filename)
            elif format_type == 'parquet':
                return self.export_to_parquet(data_list, filename)
            else:
                raise ValueError(f"Unsupported format: {format_type}. Supported formats: {', '.join(self.supported_formats)}")
                
        except Exception as e:
            print(f"Export failed: {e}")
            return False


class DataInputHandler:
    """Handles data input with validation and parsing."""
    
    @staticmethod
    def get_structured_data() -> List[Dict[str, Any]]:
        """Get structured data from user input with validation."""
        data = []
        print("=== Data Entry Mode ===")
        print("Enter data in format: key1=value1,key2=value2")
        print("Commands: 'done' to finish, 'help' for help, 'list' to show current data")
        
        while True:
            try:
                user_input = input(f"Enter data #{len(data) + 1}: ").strip()
                
                if user_input.lower() == 'done':
                    break
                elif user_input.lower() == 'help':
                    DataInputHandler._show_help()
                    continue
                elif user_input.lower() == 'list':
                    DataInputHandler._show_current_data(data)
                    continue
                elif user_input.lower() == 'clear':
                    data.clear()
                    print("✓ Data cleared")
                    continue
                
                if user_input:
                    parsed_data = DataInputHandler._parse_input(user_input)
                    if parsed_data:
                        data.append(parsed_data)
                        print(f"✓ Added: {parsed_data}")
                    else:
                        print("✗ Invalid format. Use: key1=value1,key2=value2")
                
            except KeyboardInterrupt:
                print("\n\nData entry interrupted.")
                break
            except EOFError:
                print("\n\nEnd of input reached.")
                break
        
        return data
    
    @staticmethod
    def _parse_input(user_input: str) -> Optional[Dict[str, Any]]:
        """Parse user input string into dictionary."""
        try:
            pairs = user_input.split(',')
            result = {}
            
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key and value:
                        # Try to convert value to appropriate type
                        result[key] = DataInputHandler._convert_value(value)
            
            return result if result else None
            
        except Exception:
            return None
    
    @staticmethod
    def _convert_value(value: str) -> Union[str, int, float, bool]:
        """Convert string value to appropriate type."""
        # Try boolean
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    @staticmethod
    def _show_help():
        """Show help information."""
        print("\n=== Help ===")
        print("Data Format: key1=value1,key2=value2")
        print("Examples:")
        print("  name=John,age=25,city=New York")
        print("  product=Laptop,price=999.99,in_stock=true")
        print("\nCommands:")
        print("  'done'  - Finish data entry")
        print("  'help'  - Show this help")
        print("  'list'  - Show current data")
        print("  'clear' - Clear all data")
        print("  Ctrl+C  - Interrupt entry")
        print()
    
    @staticmethod
    def _show_current_data(data: List[Dict[str, Any]]):
        """Show currently entered data."""
        if not data:
            print("No data entered yet.")
            return
        
        print(f"\n=== Current Data ({len(data)} entries) ===")
        for i, entry in enumerate(data, 1):
            print(f"  {i}: {entry}")
        print()


def main():
    """Main function with improved user interface."""
    print("=== Data Export Tool ===")
    print("This tool allows you to enter data and export it to various formats.")
    
    try:
        # Get data from user
        data = DataInputHandler.get_structured_data()
        
        if not data:
            print("No data entered. Exiting.")
            return
        
        print(f"\n✓ Data entry complete. Total entries: {len(data)}")
        
        # Show export options
        exporter = DataExporter()
        print(f"\nSupported export formats: {', '.join(exporter.supported_formats)}")
        
        while True:
            export_format = input(f"Enter export format ({', '.join(exporter.supported_formats)}): ").lower().strip()
            
            if export_format in exporter.supported_formats:
                break
            else:
                print(f"Invalid format. Please choose from: {', '.join(exporter.supported_formats)}")
        
        # Export data
        success = exporter.export_data(data, export_format)
        
        if success:
            print("✓ Data exported successfully!")
            
            # Show export history
            history = exporter.get_export_history()
            if history:
                latest = history[-1]
                print(f"File: {latest['filename']}")
                print(f"Records: {latest['records']}")
                print(f"Format: {latest['format']}")
        else:
            print("✗ Export failed. Please check the error messages above.")
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()