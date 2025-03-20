"""
Export utilities for saving generated data to various file formats.
This module provides functions for exporting data to CSV and JSON formats.
"""
import os
import csv
import json
from typing import List, Dict, Any, Union
from datetime import datetime

def serialize_for_export(value: Any) -> Any:
    """
    Convert complex data types to serializable formats.
    
    Args:
        value: The value to serialize
        
    Returns:
        A serializable version of the value
    """
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, (list, tuple)):
        return json.dumps([serialize_for_export(item) for item in value])
    elif isinstance(value, dict):
        return json.dumps({k: serialize_for_export(v) for k, v in value.items()})
    return value

def export_to_csv(data: List[Dict[str, Any]], filename: str, directory: str = './output/csv') -> bool:
    """
    Export a collection of data to a CSV file.
    
    Args:
        data: List of dictionaries to export
        filename: Name of the CSV file
        directory: Directory to save the file in
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    if not data:
        return False
    
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, filename)
    if not file_path.endswith('.csv'):
        file_path += '.csv'
    
    try:
        # Get all unique fields across all documents
        fields = set()
        for item in data:
            fields.update(item.keys())
        fields = sorted(list(fields))
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            
            # Process each document
            for item in data:
                # Convert any complex values to strings
                row = {}
                for key, value in item.items():
                    row[key] = serialize_for_export(value)
                writer.writerow(row)
        
        return True
    except Exception as e:
        print(f"Error exporting to CSV: {str(e)}")
        return False

def export_collection_to_csv(collection_name: str, data: List[Dict[str, Any]], 
                            base_dir: str = './output') -> bool:
    """
    Export a named collection to a CSV file.
    
    Args:
        collection_name: Name of the collection (used for filename)
        data: List of dictionaries to export
        base_dir: Base directory for exports
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    csv_dir = os.path.join(base_dir, 'csv')
    return export_to_csv(data, f"{collection_name}.csv", csv_dir)

def export_to_json(data: Union[List, Dict], filename: str, 
                  directory: str = './output/json', indent: int = 2) -> bool:
    """
    Export data to a JSON file.
    
    Args:
        data: Data to export (list or dictionary)
        filename: Name of the JSON file
        directory: Directory to save the file in
        indent: Indentation for JSON formatting
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    # Create directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, filename)
    if not file_path.endswith('.json'):
        file_path += '.json'
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, default=serialize_for_export, indent=indent)
        return True
    except Exception as e:
        print(f"Error exporting to JSON: {str(e)}")
        return False

def export_collection_to_json(collection_name: str, data: List[Dict[str, Any]], 
                             base_dir: str = './output') -> bool:
    """
    Export a named collection to a JSON file.
    
    Args:
        collection_name: Name of the collection (used for filename)
        data: List of dictionaries to export
        base_dir: Base directory for exports
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    json_dir = os.path.join(base_dir, 'json')
    return export_to_json(data, f"{collection_name}.json", json_dir)

def export_all_collections(data_objects: Dict[str, List[Dict[str, Any]]], 
                         formats: List[str] = ['json', 'csv'],
                         base_dir: str = './output') -> Dict[str, bool]:
    """
    Export all collections to specified formats.
    
    Args:
        data_objects: Dictionary of collections to export
        formats: List of formats to export to ('json', 'csv', or both)
        base_dir: Base directory for exports
        
    Returns:
        Dict[str, bool]: Dictionary of export results by collection
    """
    results = {}
    
    for collection_name, documents in data_objects.items():
        if not documents:
            results[collection_name] = False
            continue
        
        success = True
        
        if 'json' in formats:
            json_success = export_collection_to_json(collection_name, documents, base_dir)
            success = success and json_success
        
        if 'csv' in formats:
            csv_success = export_collection_to_csv(collection_name, documents, base_dir)
            success = success and csv_success
        
        results[collection_name] = success
    
    return results