"""
Module model for the educational data generator.
This module defines the Module class representing components of courses.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class Module:
    """
    Module class representing a component of a course in the educational system.
    """
    def __init__(
        self,
        id: str,
        name: str,
        course_id: str,
        start_date: datetime,
        end_date: datetime,
        description: Optional[str] = None,
        subject: Optional[str] = None,
        required: bool = True,
        sequence_number: int = 1
    ):
        """
        Initialize a new Module instance.
        
        Args:
            id (str): Unique identifier for the module
            name (str): Name of the module
            course_id (str): ID of the course this module belongs to
            start_date (datetime): Start date of the module
            end_date (datetime): End date of the module
            description (Optional[str]): Description of the module
            subject (Optional[str]): Subject area of the module
            required (bool): Whether this module is required or optional
            sequence_number (int): Order of this module within the course
        """
        self.id = id
        self.name = name
        self.course_id = course_id
        self.start_date = start_date
        self.end_date = end_date
        self.description = description
        self.subject = subject
        self.required = required
        self.sequence_number = sequence_number
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Relationships
        self.assignments: List[str] = []  # List of assignment IDs
    
    def add_assignment(self, assignment_id: str) -> None:
        """
        Add an assignment to this module.
        
        Args:
            assignment_id (str): ID of the assignment to add
        """
        if assignment_id not in self.assignments:
            self.assignments.append(assignment_id)
            self.updated_at = datetime.now()
    
    def remove_assignment(self, assignment_id: str) -> bool:
        """
        Remove an assignment from this module.
        
        Args:
            assignment_id (str): ID of the assignment to remove
            
        Returns:
            bool: True if the assignment was removed, False if it wasn't in the list
        """
        if assignment_id in self.assignments:
            self.assignments.remove(assignment_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_duration_days(self) -> int:
        """
        Calculate the duration of the module in days.
        
        Returns:
            int: Module duration in days
        """
        delta = self.end_date - self.start_date
        return max(1, delta.days)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Module object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: Module data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "courseId": self.course_id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "description": self.description,
            "subject": self.subject,
            "required": self.required,
            "sequenceNumber": self.sequence_number,
            "assignments": self.assignments,
            "durationDays": self.get_duration_days(),
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Module':
        """
        Create a Module instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing module data
            
        Returns:
            Module: A new Module instance
        """
        module = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            course_id=data.get('courseId', ''),
            start_date=data.get('startDate', datetime.now()),
            end_date=data.get('endDate', datetime.now()),
            description=data.get('description'),
            subject=data.get('subject'),
            required=data.get('required', True),
            sequence_number=data.get('sequenceNumber', 1)
        )
        
        # Set assignments if available
        module.assignments = data.get('assignments', [])
        
        # Set timestamps if available
        if 'createdAt' in data:
            module.created_at = data['createdAt']
        if 'updatedAt' in data:
            module.updated_at = data['updatedAt']
            
        return module
    
    def __repr__(self) -> str:
        """
        String representation of the Module instance.
        
        Returns:
            str: A string representation
        """
        return f"Module(id={self.id}, name={self.name}, seq={self.sequence_number})"