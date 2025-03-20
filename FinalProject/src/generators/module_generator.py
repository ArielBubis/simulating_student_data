"""
Module Generator for creating realistic module data.
This module provides classes for generating Module objects within courses.
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from config.settings import MODULE_SETTINGS
from models.module import Module
from models.course import Course
from generators.id_generator import generate_module_id
from utils.date_utils import generate_module_dates


class ModuleGenerator:
    """
    Generator for creating realistic module data.
    """
    def __init__(self, courses: List[Course]):
        """
        Initialize the ModuleGenerator.
        
        Args:
            courses (List[Course]): List of courses to generate modules for
        """
        self.courses = courses
        self.modules: List[Module] = []
        
        # Ensure we have courses to work with
        if not courses:
            raise ValueError("No courses provided for module generation")
        
        # Load settings
        self.min_modules_per_course = MODULE_SETTINGS.get('min_modules_per_course', 5)
        self.max_modules_per_course = MODULE_SETTINGS.get('max_modules_per_course', 30)
        self.module_types = MODULE_SETTINGS.get('module_types', [])
        self.required_module_probability = MODULE_SETTINGS.get('required_module_probability', 0.8)
    
    def _generate_module_name(self, course_name: str, sequence_number: int, module_type: str) -> str:
        """
        Generate a realistic name for a module.
        
        Args:
            course_name (str): Name of the course this module belongs to
            sequence_number (int): Module's sequence number within the course
            module_type (str): Type of module (Theory, Practice, etc.)
            
        Returns:
            str: A module name
        """
        # Extract main subject from course name
        parts = course_name.split()
        subject = parts[0] if parts else course_name
        
        # Common module naming templates
        templates = [
            f"Module {sequence_number}: {subject} {module_type}",
            f"Unit {sequence_number}: {module_type} in {subject}",
            f"{subject} {module_type} - Part {sequence_number}",
            f"{module_type} {sequence_number}: {subject} Fundamentals",
            f"{subject} {sequence_number}: {module_type} Applications"
        ]
        
        return random.choice(templates)
    
    def _generate_module_description(self, module_name: str, module_type: str) -> str:
        """
        Generate a realistic description for a module.
        
        Args:
            module_name (str): Name of the module
            module_type (str): Type of module
            
        Returns:
            str: A module description
        """
        # Generic descriptions based on module type
        descriptions = {
            "Theory": [
                "This module covers the theoretical foundations of the subject.",
                "Students will learn the core concepts and principles.",
                "Explore the fundamental theories that underpin this subject area."
            ],
            "Practice": [
                "Apply theoretical knowledge through practical exercises and problems.",
                "This hands-on module focuses on developing practical skills.",
                "Practice core techniques through guided exercises and activities."
            ],
            "Project": [
                "Develop and complete a project that demonstrates mastery of key concepts.",
                "This project-based module allows application of learned skills.",
                "Work on a comprehensive project to solidify understanding."
            ],
            "Research": [
                "Conduct research on topics related to the course material.",
                "Explore advanced concepts through guided research activities.",
                "This module focuses on research methodologies and applications."
            ],
            "Discussion": [
                "Engage in critical discussions about important topics in the field.",
                "This discussion-based module promotes critical thinking and analysis.",
                "Participate in structured discussions to deepen understanding."
            ]
        }
        
        # Default if module type not in predefined list
        default_descriptions = [
            "This module provides essential knowledge and skills in the subject area.",
            "Learn key concepts and their applications in this comprehensive module.",
            "Develop understanding and proficiency in important subject matter."
        ]
        
        # Get appropriate descriptions based on module type
        type_descriptions = descriptions.get(module_type, default_descriptions)
        selected_description = random.choice(type_descriptions)
        
        # Add more specific information
        return f"{selected_description} Module content relates to {module_name.split(':')[-1].strip() if ':' in module_name else module_name}."
    
    def generate_modules_for_course(self, course: Course) -> List[Module]:
        """
        Generate a set of modules for a specific course.
        
        Args:
            course (Course): The course to generate modules for
            
        Returns:
            List[Module]: List of generated modules
        """
        # Determine how many modules for this course
        num_modules = random.randint(self.min_modules_per_course, self.max_modules_per_course)
        
        # Get module date ranges within the course timeline
        module_dates = generate_module_dates(
            course.start_date, course.end_date, num_modules
        )
        
        # Generate modules
        course_modules = []
        for i, (start_date, end_date) in enumerate(module_dates, 1):
            # Generate a unique ID
            module_id = generate_module_id()
            
            # Select module type
            module_type = random.choice(self.module_types) if self.module_types else "General"
            
            # Generate name and description
            name = self._generate_module_name(course.name, i, module_type)
            description = self._generate_module_description(name, module_type)
            
            # Determine if this module is required
            required = random.random() < self.required_module_probability
            
            # Create the module
            module = Module(
                id=module_id,
                name=name,
                course_id=course.id,
                start_date=start_date,
                end_date=end_date,
                description=description,
                subject=course.subject_area,
                required=required,
                sequence_number=i
            )
            
            # Add to our lists
            course_modules.append(module)
            self.modules.append(module)
            
            # Update course's module list
            course.add_module(module.id)
        
        return course_modules
    
    def generate_all_modules(self) -> List[Module]:
        """
        Generate modules for all courses.
        
        Returns:
            List[Module]: List of all generated modules
        """
        # Clear existing modules
        self.modules = []
        
        # Generate modules for each course
        for course in self.courses:
            self.generate_modules_for_course(course)
        
        return self.modules
    
    def get_modules_for_course(self, course_id: str) -> List[Module]:
        """
        Get all modules for a specific course.
        
        Args:
            course_id (str): ID of the course
            
        Returns:
            List[Module]: List of modules for the course
        """
        return [m for m in self.modules if m.course_id == course_id]
    
    def get_module_by_id(self, module_id: str) -> Optional[Module]:
        """
        Find a module by ID.
        
        Args:
            module_id (str): ID of the module to find
            
        Returns:
            Optional[Module]: The module if found, None otherwise
        """
        for module in self.modules:
            if module.id == module_id:
                return module
        return None
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all modules to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of module dictionaries
        """
        return [module.to_dict() for module in self.modules]