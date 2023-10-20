import csv
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

def export_to_csv(data_list, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_list[0].keys())  # Write the header row using the keys of the dictionary (column names)
        for item in data_list:
            writer.writerow(item.values())  # Write the data rows using the values of the dictionary

def export_to_json(data_list, filename):
    with open(filename, 'w') as jsonfile:
        json.dump(data_list, jsonfile, indent=2)

def export_to_xml(data_list, filename):
    root = ET.Element("data")
    for row in data_list:
        data_element = ET.SubElement(root, "item")
        for key, value in row.items():
            column_element = ET.SubElement(data_element, key)
            column_element.text = value

    tree = ET.ElementTree(root)
    tree.write(filename)

if __name__ == "__main__":
    data = []

    # Get user input for data entry
    while True:
        new_data = input("Enter data (or type 'done' to finish): ")
        if new_data.lower() == 'done':
            break
        columns = new_data.split(",")
        if len(columns) > 1:
            data.append(dict(zip(columns[0::2], columns[1::2])))
        else:
            print("Invalid input. Please enter data in the format 'column1,value1,column2,value2,...'")
        
    if not data:
        print("No data entered. Exiting.")
    else:
        export_choice = input("Enter the format to export (csv, json, xml): ").lower()
        if export_choice == 'csv':
            export_to_csv(data, "data.csv")
        elif export_choice == 'json':
            export_to_json(data, "data.json")
        elif export_choice == 'xml':
            export_to_xml(data, "data.xml")
        else:
            print("Invalid export format. Data not exported.")
        print("Data exported successfully.")