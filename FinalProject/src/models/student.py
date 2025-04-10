"""
Student model for the educational data generator.
This module defines the Student class that inherits from the base User class.
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from models.user import User


class Student(User):
    """
    Student class representing a student in the educational system.
    Inherits from the base User class.
    """
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        school_id: Optional[str] = None,
        grade_level: Optional[int] = None,
        entry_year: Optional[int] = None
    ):
        """
        Initialize a new Student instance.
        
        Args:
            id (str): Unique 9-digit identifier for the student
            name (str): Full name of the student
            email (str): Email address of the student
            phone (Optional[str]): Phone number of the student
            school_id (Optional[str]): ID of the school the student belongs to
            grade_level (Optional[int]): Student's grade level or year
            entry_year (Optional[int]): Year the student entered the school
        """
        # Initialize the parent User class
        super().__init__(id, name, email, phone, school_id)
        
        # Student-specific attributes
        self.grade_level = grade_level
        self.entry_year = entry_year
        self.courses: List[str] = []  # Course IDs the student is enrolled in
        self.total_score: float = 0.0  # Aggregate score across all courses
        self.completion_percentage: float = 0.0  # Track percentage of assignments completed

        # Performance profile (for data generation)
        self.base_performance: float = 75.0  # Base performance level (0-100)
        self.subject_strengths: Dict[str, float] = {}  # Subject area to strength modifier
    
    def add_course(self, course_id: str) -> None:
        """
        Enroll the student in a course.
        
        Args:
            course_id (str): ID of the course to enroll in
        """
        if course_id not in self.courses:
            self.courses.append(course_id)
            self.updated_at = datetime.now()
    
    def remove_course(self, course_id: str) -> bool:
        """
        Remove a course enrollment.
        
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
    
    def update_performance_profile(
        self, 
        base_performance: float,
        subject_strengths: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Update the student's performance profile for data generation.
        
        Args:
            base_performance (float): Base performance level (0-100)
            subject_strengths (Optional[Dict[str, float]]): Subject area to strength modifier mapping
        """
        self.base_performance = base_performance
        if subject_strengths:
            self.subject_strengths = subject_strengths
    
    def update_total_score(self, new_score: float, completion_percentage: float = None) -> None:
        """
        Update the student's total score and completion percentage.
        
        Args:
            new_score (float): New total score
            completion_percentage (float): New completion percentage
        """
        self.total_score = new_score
        if completion_percentage is not None:
            self.completion_percentage = completion_percentage
        self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Student object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: Student data as a dictionary
        """
        # Get the base user dictionary
        user_dict = super().to_dict()
        
        # Add student-specific fields
        student_dict = {
            **user_dict,
            "type": "student",  # Add type field for inheritance
            "gradeLevel": self.grade_level,
            "entryYear": self.entry_year,
            "courses": self.courses,
            "totalScore": self.total_score
        }
        
        return student_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """
        Create a Student instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing student data
            
        Returns:
            Student: A new Student instance
        """
        student = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            school_id=data.get('schoolId'),
            grade_level=data.get('gradeLevel'),
            entry_year=data.get('entryYear')
        )
        
        # Set courses if available
        student.courses = data.get('courses', [])
        
        # Set total score if available
        if 'totalScore' in data:
            student.total_score = data['totalScore']
        
        # Set timestamps if available
        if 'createdAt' in data:
            student.created_at = data['createdAt']
        if 'updatedAt' in data:
            student.updated_at = data['updatedAt']
            
        return student
    
    def __repr__(self) -> str:
        """
        String representation of the Student instance.
        
        Returns:
            str: A string representation
        """
        return f"Student(id={self.id}, name={self.name}, courses={len(self.courses)})"