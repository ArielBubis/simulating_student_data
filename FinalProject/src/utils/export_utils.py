"""
Export utilities for saving generated data to various file formats.
This module provides functions for exporting data to CSV and JSON formats.
"""
import os
import csv
import json
from typing import List, Dict, Any, Union
from datetime import datetime
from venv import logger

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
    
    # Check if we're exporting mid-semester data
    is_mid_semester = False
    metadata = data_objects.get('metadata', [{}])[0]
    if metadata.get('isMidSemester'):
        is_mid_semester = True
    
    # Ensure base directory exists
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    for collection_name, documents in data_objects.items():
        if not documents:
            results[collection_name] = False
            continue
        
        success = True
        
        # For studentAssignments, add status field if not present
        if collection_name == 'studentAssignments' and is_mid_semester:
            # Ensure each document has a status field
            for doc in documents:
                if 'status' not in doc:
                    doc['status'] = 'completed'
        
        if 'json' in formats:
            # Create JSON export filename
            filename = collection_name
            
            # Add mid-semester indicator if applicable
            if is_mid_semester:
                filename = f"{filename}_mid_semester"
            
            json_dir = os.path.join(base_dir, 'json')
            json_success = export_collection_to_json(filename, documents, json_dir)
            success = success and json_success
        
        if 'csv' in formats:
            # Create CSV export filename
            filename = collection_name
            
            # Add mid-semester indicator if applicable
            if is_mid_semester:
                filename = f"{filename}_mid_semester"
            
            csv_dir = os.path.join(base_dir, 'csv')
            csv_success = export_collection_to_csv(filename, documents, csv_dir)
            success = success and csv_success
        
        results[collection_name] = success
    
    return results

def export_mid_semester_summary(self, directory: str = './output/summary') -> bool:
    """
    Export a mid-semester summary report in human-readable format.
    
    Args:
        directory (str): Directory to save the summary file
        
    Returns:
        bool: True if export was successful, False otherwise
    """
    if not self.is_mid_semester:
        logger.warning("Mid-semester summary export is only available in mid-semester mode")
        return False
    
    # Ensure directory exists
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    try:
        # Generate progress report
        report = self.generate_mid_semester_progress_report()
        
        # Create a human-readable summary
        summary_path = os.path.join(directory, 'mid_semester_summary.md')
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Mid-Semester Progress Summary\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Cutoff date: {self.cutoff_date.strftime('%Y-%m-%d') if self.cutoff_date else 'Unknown'}\n\n")
            
            # Overall statistics
            f.write(f"## Overall Statistics\n\n")
            f.write(f"- Overall completion rate: {report.get('overallCompletion', 0)}%\n")
            
            status_counts = report.get('statusCounts', {})
            completed = status_counts.get('completed', 0)
            pending = status_counts.get('pending', 0)
            future = status_counts.get('future', 0)
            total = completed + pending + future
            
            f.write(f"- Total assignments: {total}\n")
            f.write(f"  - Completed: {completed} ({status_counts.get('completedPercent', 0)}%)\n")
            f.write(f"  - Pending: {pending} ({status_counts.get('pendingPercent', 0)}%)\n")
            f.write(f"  - Future: {future} ({status_counts.get('futurePercent', 0)}%)\n\n")
            
            # Profile breakdown
            f.write(f"## Completion by Student Profile\n\n")
            f.write(f"| Profile | Completion Rate | Completed | Pending | Future |\n")
            f.write(f"|---------|----------------|-----------|---------|--------|\n")
            
            for profile, stats in report.get('profileBreakdown', {}).items():
                f.write(f"| {profile} | {stats.get('completionRate', 0)}% | " +
                        f"{stats.get('completedPercent', 0)}% | " +
                        f"{stats.get('pendingPercent', 0)}% | " +
                        f"{stats.get('futurePercent', 0)}% |\n")
            
            f.write(f"\n")
            
            # Subject breakdown
            f.write(f"## Completion by Subject\n\n")
            f.write(f"| Subject | Completion Rate | Completed | Available | Future |\n")
            f.write(f"|---------|----------------|-----------|-----------|--------|\n")
            
            for subject, stats in report.get('subjectBreakdown', {}).items():
                completed = stats.get('completedAssignments', 0)
                available = stats.get('availableAssignments', 0)
                future = stats.get('futureAssignments', 0)
                rate = stats.get('completionRate', 0)
                
                f.write(f"| {subject} | {rate}% | {completed} | {available} | {future} |\n")
            
            f.write(f"\n")
            
            # Time analysis
            if 'timeAnalysis' in report:
                f.write(f"## Completion by Time Period\n\n")
                f.write(f"| Period | Completion Rate | Completed | Available |\n")
                f.write(f"|--------|----------------|-----------|----------|\n")
                
                for period, data in report.get('timeAnalysis', {}).items():
                    period_name = period.capitalize()
                    rate = data.get('rate', 0)
                    completed = data.get('completed', 0)
                    available = data.get('available', 0)
                    
                    f.write(f"| {period_name} | {rate}% | {completed} | {available} |\n")
                
                f.write(f"\n")
            
            # Outlier analysis
            if 'outlierAnalysis' in report:
                f.write(f"## Student Outliers\n\n")
                
                f.write(f"### Top Performers\n\n")
                for student in report.get('outlierAnalysis', {}).get('highPerformers', []):
                    f.write(f"- Student {student.get('studentId')}: {student.get('completionRate')}% " +
                            f"completion rate ({student.get('profile')})\n")
                
                f.write(f"\n### Struggling Students\n\n")
                for student in report.get('outlierAnalysis', {}).get('strugglingStudents', []):
                    f.write(f"- Student {student.get('studentId')}: {student.get('completionRate')}% " +
                            f"completion rate ({student.get('profile')})\n")
        
        logger.info(f"Exported mid-semester summary to {summary_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting mid-semester summary: {str(e)}")
        return False