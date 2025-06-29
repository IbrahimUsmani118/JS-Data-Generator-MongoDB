#!/usr/bin/env python3
"""
Data Input Module - Optimized version
Provides functionality for collecting and validating user data input.
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime


class DataCollector:
    """A class to handle data collection with validation and error handling."""
    
    def __init__(self, data_type: str = "general"):
        self.data_type = data_type
        self.data_list: List[Dict[str, Any]] = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "data_type": data_type,
            "total_entries": 0
        }
    
    def validate_input(self, user_input: str) -> bool:
        """Validate user input based on data type."""
        if not user_input or not user_input.strip():
            return False
        
        # Add specific validation based on data_type
        if self.data_type == "email":
            return "@" in user_input and "." in user_input
        elif self.data_type == "numeric":
            try:
                float(user_input)
                return True
            except ValueError:
                return False
        
        return True
    
    def get_user_data(self, prompt: str = "Enter data") -> List[Dict[str, Any]]:
        """Collect user data with improved validation and structure."""
        print(f"=== {self.data_type.upper()} Data Collection ===")
        print("Enter data (or 'done' to stop, 'help' for options):")
        
        entry_count = 0
        
        while True:
            try:
                user_input = input(f"{prompt} #{entry_count + 1}: ").strip()
                
                if user_input.lower() == 'done':
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif user_input.lower() == 'list':
                    self._show_current_data()
                    continue
                
                if self.validate_input(user_input):
                    entry = {
                        "id": entry_count + 1,
                        "value": user_input,
                        "timestamp": datetime.now().isoformat(),
                        "data_type": self.data_type
                    }
                    self.data_list.append(entry)
                    entry_count += 1
                    print(f"✓ Added: {user_input}")
                else:
                    print(f"✗ Invalid input: {user_input}")
                    
            except KeyboardInterrupt:
                print("\n\nData collection interrupted by user.")
                break
            except EOFError:
                print("\n\nEnd of input reached.")
                break
        
        self.metadata["total_entries"] = entry_count
        return self.data_list
    
    def _show_help(self):
        """Display help information."""
        print("\n=== Help ===")
        print("Commands:")
        print("  'done'  - Finish data collection")
        print("  'help'  - Show this help")
        print("  'list'  - Show current data")
        print("  Ctrl+C  - Interrupt collection")
        print()
    
    def _show_current_data(self):
        """Display currently collected data."""
        if not self.data_list:
            print("No data collected yet.")
            return
        
        print(f"\n=== Current Data ({len(self.data_list)} entries) ===")
        for entry in self.data_list:
            print(f"  {entry['id']}: {entry['value']}")
        print()
    
    def save_to_file(self, filename: Optional[str] = None) -> str:
        """Save collected data to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"collected_data_{self.data_type}_{timestamp}.json"
        
        data_to_save = {
            "metadata": self.metadata,
            "data": self.data_list
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            print(f"✓ Data saved to: {filename}")
            return filename
        except Exception as e:
            print(f"✗ Error saving data: {e}")
            return ""


def get_user_data(data_type: str = "general", save_to_file: bool = True) -> List[Dict[str, Any]]:
    """
    Main function to get user data with improved functionality.
    
    Args:
        data_type: Type of data being collected
        save_to_file: Whether to save data to file
    
    Returns:
        List of collected data entries
    """
    collector = DataCollector(data_type)
    data = collector.get_user_data()
    
    if data and save_to_file:
        collector.save_to_file()
    
    print(f"\n✓ Data collection complete. Total entries: {len(data)}")
    return data


if __name__ == "__main__":
    # Example usage with different data types
    print("Choose data type:")
    print("1. General data")
    print("2. Email addresses")
    print("3. Numeric data")
    
    try:
        choice = input("Enter choice (1-3): ").strip()
        data_types = {
            "1": "general",
            "2": "email", 
            "3": "numeric"
        }
        
        selected_type = data_types.get(choice, "general")
        data = get_user_data(data_type=selected_type)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
