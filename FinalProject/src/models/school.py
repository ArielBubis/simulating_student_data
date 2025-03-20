"""
School model for the educational data generator.
This module defines the School class representing an educational institution.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime


class School:
    """
    School class representing an educational institution.
    """
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        location: str,
        founding_year: int,
        student_capacity: int,
        specialization: str,
        website: str,
        ranking: float,
        course_focus: Optional[List[str]] = None
    ):
        """
        Initialize a new School instance.
        
        Args:
            id (str): Unique identifier for the school
            name (str): Name of the school
            type (str): Type of school (e.g., Technical, Vocational, General)
            location (str): Geographic location of the school
            founding_year (int): Year the school was founded
            student_capacity (int): Maximum number of students the school can accommodate
            specialization (str): Main focus or specialization of the school
            website (str): School's website URL
            ranking (float): School's ranking (out of 5)
            course_focus (Optional[List[str]]): List of subject areas the school focuses on
        """
        self.id = id
        self.name = name
        self.type = type
        self.location = location
        self.founding_year = founding_year
        self.student_capacity = student_capacity
        self.specialization = specialization
        self.website = website
        self.ranking = ranking
        self.course_focus = course_focus or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Relationships (to be populated later)
        self.courses: List[str] = []  # List of course IDs
        self.teachers: List[str] = []  # List of teacher IDs
        self.students: List[str] = []  # List of student IDs

    def add_course(self, course_id: str) -> None:
        """
        Add a course to this school.
        
        Args:
            course_id (str): ID of the course to add
        """
        if course_id not in self.courses:
            self.courses.append(course_id)
            self.updated_at = datetime.now()

    def add_teacher(self, teacher_id: str) -> None:
        """
        Add a teacher to this school.
        
        Args:
            teacher_id (str): ID of the teacher to add
        """
        if teacher_id not in self.teachers:
            self.teachers.append(teacher_id)
            self.updated_at = datetime.now()

    def add_student(self, student_id: str) -> None:
        """
        Add a student to this school.
        
        Args:
            student_id (str): ID of the student to add
        """
        if student_id not in self.students:
            self.students.append(student_id)
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the School object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: School data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "location": self.location,
            "foundingYear": self.founding_year,
            "studentCapacity": self.student_capacity,
            "specialization": self.specialization,
            "website": self.website,
            "ranking": self.ranking,
            "courseFocus": self.course_focus,
            "courses": self.courses,
            "teachers": self.teachers,
            "students": self.students,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'School':
        """
        Create a School instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing school data
            
        Returns:
            School: A new School instance
        """
        school = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            type=data.get('type', ''),
            location=data.get('location', ''),
            founding_year=data.get('foundingYear', 0),
            student_capacity=data.get('studentCapacity', 0),
            specialization=data.get('specialization', ''),
            website=data.get('website', ''),
            ranking=data.get('ranking', 0.0),
            course_focus=data.get('courseFocus', [])
        )
        
        # Set relationships
        school.courses = data.get('courses', [])
        school.teachers = data.get('teachers', [])
        school.students = data.get('students', [])
        
        # Set timestamps if available
        if 'createdAt' in data:
            school.created_at = data['createdAt']
        if 'updatedAt' in data:
            school.updated_at = data['updatedAt']
            
        return school
    
    def __repr__(self) -> str:
        """
        String representation of the School instance.
        
        Returns:
            str: A string representation
        """
        return f"School(id={self.id}, name={self.name}, type={self.type})"