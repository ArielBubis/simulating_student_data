"""
Course Generator module for creating realistic course data.
This module provides classes for generating Course objects.
"""
import random
import string
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from config.settings import COURSE_SETTINGS
from config.school_data import get_courses_for_school
from models.course import Course
from models.school import School
from models.teacher import Teacher
from generators.id_generator import generate_course_id
from utils.date_utils import generate_course_dates


class CourseGenerator:
    """
    Generator for creating realistic course data.
    """
    def __init__(self, schools: List[School], teachers: List[Teacher]):
        """
        Initialize the CourseGenerator.
        
        Args:
            schools (List[School]): List of schools to generate courses for
            teachers (List[Teacher]): List of teachers to assign to courses
        """
        self.schools = schools
        self.teachers = teachers
        self.courses: List[Course] = []
        
        # Ensure we have schools and teachers to work with
        if not schools:
            raise ValueError("No schools provided for course generation")
        if not teachers:
            raise ValueError("No teachers provided for course generation")
        
        # Load settings
        self.min_courses_per_school = COURSE_SETTINGS.get('min_courses_per_school', 5)
        self.max_courses_per_school = COURSE_SETTINGS.get('max_courses_per_school', 9)
        self.subject_areas = COURSE_SETTINGS.get('subject_areas', [])
    
    def _generate_access_code(self, length: int = 6) -> str:
        """
        Generate a random access code for a course.
        
        Args:
            length (int): Length of the access code
            
        Returns:
            str: A random alphanumeric access code
        """
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=length))
    
    def _get_teachers_for_school(self, school_id: str) -> List[Teacher]:
        """
        Get all teachers for a specific school.
        
        Args:
            school_id (str): ID of the school
            
        Returns:
            List[Teacher]: List of teachers for the school
        """
        return [t for t in self.teachers if t.school_id == school_id]
    
    def _assign_teachers_to_course(self, course: Course, school_id: str) -> None:
        """
        Assign teachers to a course.
        
        Args:
            course (Course): The course to assign teachers to
            school_id (str): ID of the school the course belongs to
        """
        # Get teachers for this school
        school_teachers = self._get_teachers_for_school(school_id)
        
        if not school_teachers:
            return  # No teachers available
        
        # Decide how many teachers for this course (usually 1, sometimes 2)
        num_teachers = 1 if random.random() < 0.8 else 2
        num_teachers = min(num_teachers, len(school_teachers))
        
        # Select random teachers
        selected_teachers = random.sample(school_teachers, num_teachers)
        
        # Assign them to the course
        for teacher in selected_teachers:
            course.add_teacher(teacher.id)
            teacher.add_course(course.id)
    
    def generate_course(self, school: School) -> Course:
        """
        Generate a single course for a specified school.
        
        Args:
            school (School): School to generate the course for
            
        Returns:
            Course: A newly generated Course instance
        """
        # Generate a unique ID
        course_id = generate_course_id()
        
        # Get appropriate course names for this school
        possible_courses = get_courses_for_school(school.name)
        if not possible_courses:
            # Fallback if no specific courses found
            possible_courses = [f"{subject} {random.randint(101, 499)}" 
                              for subject in self.subject_areas]
        
        # Select a course name that hasn't been used yet
        existing_course_names = [c.name for c in self.courses if c.school_id == school.id]
        available_courses = [c for c in possible_courses if c not in existing_course_names]
        
        if not available_courses:
            # If all are used, add a section number to an existing course
            base_name = random.choice(possible_courses)
            name = f"{base_name} - Section {random.randint(2, 9)}"
        else:
            name = random.choice(available_courses)
        
        # Generate description
        description = f"This course covers the fundamentals of {name}. Students will learn key concepts and practical applications."
        
        # Generate course dates
        start_date, end_date = generate_course_dates()
        
        # Generate access code
        access_code = self._generate_access_code()
        
        # Determine subject area
        subject_area = None
        for subject in self.subject_areas:
            if subject.lower() in name.lower():
                subject_area = subject
                break
        
        if not subject_area and self.subject_areas:
            subject_area = random.choice(self.subject_areas)
        
        # Determine if published (most courses are published)
        published = random.random() < 0.9
        
        # Create the course
        course = Course(
            id=course_id,
            name=name,
            description=description,
            school_id=school.id,
            start_date=start_date,
            end_date=end_date,
            access_code=access_code,
            subject_area=subject_area,
            published=published
        )
        
        # Assign teachers to the course
        self._assign_teachers_to_course(course, school.id)
        
        return course
    
    def generate_courses(self) -> List[Course]:
        """
        Generate courses for all schools.
        
        Returns:
            List[Course]: List of all generated courses
        """
        # Clear existing courses
        self.courses = []
        
        # Generate courses for each school
        for school in self.schools:
            # Determine how many courses for this school
            num_courses = random.randint(self.min_courses_per_school, self.max_courses_per_school)
            
            # Generate the courses
            for _ in range(num_courses):
                course = self.generate_course(school)
                self.courses.append(course)
                print(f"Generated course: {course.id}, {course.name}")
                # Update school's course list
                school.add_course(course.id)
        
        return self.courses
    
    def get_courses_for_school(self, school_id: str) -> List[Course]:
        """
        Get all courses for a specific school.
        
        Args:
            school_id (str): ID of the school
            
        Returns:
            List[Course]: List of courses for the school
        """
        return [c for c in self.courses if c.school_id == school_id]
    
    def get_courses_for_teacher(self, teacher_id: str) -> List[Course]:
        """
        Get all courses for a specific teacher.
        
        Args:
            teacher_id (str): ID of the teacher
            
        Returns:
            List[Course]: List of courses taught by the teacher
        """
        return [c for c in self.courses if teacher_id in c.teachers]
    
    def get_course_by_id(self, course_id: str) -> Optional[Course]:
        """
        Find a course by ID.
        
        Args:
            course_id (str): ID of the course to find
            
        Returns:
            Optional[Course]: The course if found, None otherwise
        """
        for course in self.courses:
            if course.id == course_id:
                return course
        return None
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all courses to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of course dictionaries
        """
        return [course.to_dict() for course in self.courses]