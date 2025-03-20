"""
Course model for the educational data generator.
This module defines the Course class representing educational courses.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class Course:
    """
    Course class representing an educational course in the system.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        school_id: str,
        start_date: datetime,
        end_date: datetime,
        access_code: Optional[str] = None,
        subject_area: Optional[str] = None,
        published: bool = True
    ):
        """
        Initialize a new Course instance.
        
        Args:
            id (str): Unique identifier for the course
            name (str): Name of the course
            description (str): Description of the course
            school_id (str): ID of the school offering the course
            start_date (datetime): Start date of the course
            end_date (datetime): End date of the course
            access_code (Optional[str]): Access code for enrollment
            subject_area (Optional[str]): Subject area of the course
            published (bool): Whether the course is published/active
        """
        self.id = id
        self.name = name
        self.description = description
        self.school_id = school_id
        self.start_date = start_date
        self.end_date = end_date
        self.access_code = access_code
        self.subject_area = subject_area
        self.published = published
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Relationships
        self.modules: List[str] = []  # List of module IDs
        self.teachers: List[str] = []  # List of teacher IDs
        self.students: List[str] = []  # List of student IDs
    
    def add_module(self, module_id: str) -> None:
        """
        Add a module to this course.
        
        Args:
            module_id (str): ID of the module to add
        """
        if module_id not in self.modules:
            self.modules.append(module_id)
            self.updated_at = datetime.now()
    
    def add_teacher(self, teacher_id: str) -> None:
        """
        Add a teacher to this course.
        
        Args:
            teacher_id (str): ID of the teacher to add
        """
        if teacher_id not in self.teachers:
            self.teachers.append(teacher_id)
            self.updated_at = datetime.now()
    
    def add_student(self, student_id: str) -> None:
        """
        Add a student to this course.
        
        Args:
            student_id (str): ID of the student to add
        """
        if student_id not in self.students:
            self.students.append(student_id)
            self.updated_at = datetime.now()
    
    def remove_student(self, student_id: str) -> bool:
        """
        Remove a student from this course.
        
        Args:
            student_id (str): ID of the student to remove
            
        Returns:
            bool: True if the student was removed, False if they weren't enrolled
        """
        if student_id in self.students:
            self.students.remove(student_id)
            self.updated_at = datetime.now()
            return True
        return False
    
    def set_published(self, published: bool) -> None:
        """
        Set the published status of the course.
        
        Args:
            published (bool): New published status
        """
        self.published = published
        self.updated_at = datetime.now()
    
    def get_duration_weeks(self) -> int:
        """
        Calculate the duration of the course in weeks.
        
        Returns:
            int: Course duration in weeks
        """
        delta = self.end_date - self.start_date
        return max(1, delta.days // 7)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Course object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: Course data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "schoolId": self.school_id,
            "startDate": self.start_date,
            "endDate": self.end_date,
            "accessCode": self.access_code,
            "subjectArea": self.subject_area,
            "published": self.published,
            "modules": self.modules,
            "teachers": self.teachers,
            "students": self.students,
            "durationWeeks": self.get_duration_weeks(),
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Course':
        """
        Create a Course instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing course data
            
        Returns:
            Course: A new Course instance
        """
        course = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            description=data.get('description', ''),
            school_id=data.get('schoolId', ''),
            start_date=data.get('startDate', datetime.now()),
            end_date=data.get('endDate', datetime.now()),
            access_code=data.get('accessCode'),
            subject_area=data.get('subjectArea'),
            published=data.get('published', True)
        )
        
        # Set relationships if available
        course.modules = data.get('modules', [])
        course.teachers = data.get('teachers', [])
        course.students = data.get('students', [])
        
        # Set timestamps if available
        if 'createdAt' in data:
            course.created_at = data['createdAt']
        if 'updatedAt' in data:
            course.updated_at = data['updatedAt']
            
        return course
    
    def __repr__(self) -> str:
        """
        String representation of the Course instance.
        
        Returns:
            str: A string representation
        """
        return f"Course(id={self.id}, name={self.name}, modules={len(self.modules)})"