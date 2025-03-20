"""
Teacher model for the educational data generator.
This module defines the Teacher class that inherits from the base User class.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.user import User


class Teacher(User):
    """
    Teacher class representing a teacher in the educational system.
    Inherits from the base User class.
    """
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        school_id: Optional[str] = None,
        department: Optional[str] = None,
        title: Optional[str] = None
    ):
        """
        Initialize a new Teacher instance.
        
        Args:
            id (str): Unique 9-digit identifier for the teacher
            name (str): Full name of the teacher
            email (str): Email address of the teacher
            phone (Optional[str]): Phone number of the teacher
            school_id (Optional[str]): ID of the school the teacher belongs to
            department (Optional[str]): Department the teacher belongs to
            title (Optional[str]): Teacher's title (e.g., "Professor", "Dr.")
        """
        # Initialize the parent User class
        super().__init__(id, name, email, phone, school_id)
        
        # Teacher-specific attributes
        self.department = department
        self.title = title
        self.courses: List[str] = []  # List of course IDs the teacher is mentoring
    
    def add_course(self, course_id: str) -> None:
        """
        Add a course to the teacher's list of mentored courses.
        
        Args:
            course_id (str): ID of the course to add
        """
        if course_id not in self.courses:
            self.courses.append(course_id)
            self.updated_at = datetime.now()
    
    def remove_course(self, course_id: str) -> bool:
        """
        Remove a course from the teacher's list of mentored courses.
        
        Args:
            course_id (str): ID of the course to remove
            
        Returns:
            bool: True if the course was removed, False if it wasn't in the list
        """
        if course_id in self.courses:
            self.courses.remove(course_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Teacher object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: Teacher data as a dictionary
        """
        # Get the base user dictionary
        user_dict = super().to_dict()
        
        # Add teacher-specific fields
        teacher_dict = {
            **user_dict,
            "type": "teacher",  # Add type field for inheritance
            "department": self.department,
            "title": self.title,
            "courses": self.courses
        }
        
        return teacher_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Teacher':
        """
        Create a Teacher instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing teacher data
            
        Returns:
            Teacher: A new Teacher instance
        """
        teacher = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            school_id=data.get('schoolId'),
            department=data.get('department'),
            title=data.get('title')
        )
        
        # Set courses if available
        teacher.courses = data.get('courses', [])
        
        # Set timestamps if available
        if 'createdAt' in data:
            teacher.created_at = data['createdAt']
        if 'updatedAt' in data:
            teacher.updated_at = data['updatedAt']
            
        return teacher
    
    def __repr__(self) -> str:
        """
        String representation of the Teacher instance.
        
        Returns:
            str: A string representation
        """
        return f"Teacher(id={self.id}, name={self.name}, courses={len(self.courses)})"