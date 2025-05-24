"""
Assignment Generator for creating realistic assignment data.
This module provides classes for generating Assignment objects within modules.
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from config.settings import ASSIGNMENT_SETTINGS
from models.assignment import Assignment
from models.module import Module
from generators.id_generator import generate_assignment_id
from utils.date_utils import generate_assignment_date


class AssignmentGenerator:
    """
    Generator for creating realistic assignment data.
    """
    def __init__(self, modules: List[Module]):
        """
        Initialize the AssignmentGenerator.
        
        Args:
            modules (List[Module]): List of modules to generate assignments for
        """
        self.modules = modules
        self.assignments: List[Assignment] = []
        
        # Ensure we have modules to work with
        if not modules:
            raise ValueError("No modules provided for assignment generation")
        
        # Load settings
        self.min_assignments_per_module = ASSIGNMENT_SETTINGS.get('min_assignments_per_module', 1)
        self.max_assignments_per_module = ASSIGNMENT_SETTINGS.get('max_assignments_per_module', 2)
        self.assignment_types = ASSIGNMENT_SETTINGS.get('assignment_types', [])
    
    def _get_assignment_type_info(self, assignment_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration information for a specific assignment type, or a random one.
        
        Args:
            assignment_type (Optional[str]): Name of the assignment type, or None for random
            
        Returns:
            Dict[str, Any]: Assignment type configuration
        """
        if not self.assignment_types:
            # Default assignment type if none configured
            return {
                "name": "Assignment",
                "weight": 1.0,
                "mean_score": 75,
                "std_dev": 10,
                "skewness": -0.5
            }
        
        # If type specified, find that specific type
        if assignment_type:
            for type_info in self.assignment_types:
                if type_info.get("name") == assignment_type:
                    return type_info
            
            # If not found, return first type as fallback
            return self.assignment_types[0]
        
        # Otherwise, select a random type
        return random.choice(self.assignment_types)
    
    def _generate_assignment_name(self, module_name: str, assignment_type: str, sequence: int) -> str:
        """
        Generate a realistic name for an assignment.
        
        Args:
            module_name (str): Name of the module this assignment belongs to
            assignment_type (str): Type of assignment (Quiz, Exam, Project, etc.)
            sequence (int): Assignment sequence number within the module
            
        Returns:
            str: An assignment name
        """
        # Extract main subject from module name
        if ':' in module_name:
            subject = module_name.split(':')[1].strip()
        else:
            parts = module_name.split()
            subject = parts[1] if len(parts) > 1 else module_name
        
        # Common assignment naming templates
        templates = [
            f"{assignment_type} {sequence}: {subject}",
            f"{subject} {assignment_type} {sequence}",
            f"{assignment_type} - {subject} Concepts",
            f"{subject} Assessment {sequence}",
            f"{assignment_type} on {subject}"
        ]
        
        return random.choice(templates)
    
    def _generate_assignment_description(self, name: str, assignment_type: str) -> str:
        """
        Generate a realistic description for an assignment.
        
        Args:
            name (str): Name of the assignment
            assignment_type (str): Type of assignment
            
        Returns:
            str: An assignment description
        """
        # Generic descriptions based on assignment type
        descriptions = {
            "Quiz": [
                "A short quiz to test your understanding of key concepts.",
                "This quiz covers the essential material from recent lessons.",
                "Complete this quiz to demonstrate your knowledge of basic concepts."
            ],
            "Exam": [
                "A comprehensive exam covering all major topics in this module.",
                "This exam assesses your overall understanding of the material.",
                "Demonstrate your mastery of the subject through this detailed examination."
            ],
            "Homework": [
                "Complete these exercises to reinforce your understanding.",
                "This homework assignment provides practice with key concepts.",
                "Apply what you've learned by completing these problems."
            ],
            "Project": [
                "Develop a project that demonstrates your understanding of the material.",
                "This project allows you to apply concepts in a practical context.",
                "Create a comprehensive solution that showcases your skills."
            ],
            # "Participation": [
            #     "Contribute to class discussions and activities.",
            #     "Your active participation in class activities will be assessed.",
            #     "Engage with the material through discussion and collaboration."
            # ]
        }
        
        # Default if assignment type not in predefined list
        default_descriptions = [
            "Complete this assignment to demonstrate your understanding.",
            "This assignment assesses your knowledge of key concepts.",
            "Show your mastery of the material through this assignment."
        ]
        
        # Get appropriate descriptions based on assignment type
        type_descriptions = descriptions.get(assignment_type, default_descriptions)
        selected_description = random.choice(type_descriptions)
        
        # Add more specific information
        return f"{selected_description} This {assignment_type.lower()} focuses on {name.split(':')[-1].strip() if ':' in name else name}."
    
    def generate_assignments_for_module(self, module: Module) -> List[Assignment]:
        """
        Generate a set of assignments for a specific module.
        
        Args:
            module (Module): The module to generate assignments for
            
        Returns:
            List[Assignment]: List of generated assignments
        """
        # Determine how many assignments for this module
        num_assignments = random.randint(
            self.min_assignments_per_module, 
            self.max_assignments_per_module
        )
        
        # Generate assignments
        module_assignments = []
        for i in range(1, num_assignments + 1):
            # Get assignment type information
            type_info = self._get_assignment_type_info()
            assignment_type = type_info.get("name", "Assignment")
            weight = type_info.get("weight", 1.0)
            
            # Generate a unique ID
            assignment_id = generate_assignment_id()
            
            # Generate assignment and due dates
            assign_date, due_date = generate_assignment_date(module.start_date, module.end_date)
            
            # Generate name and description
            name = self._generate_assignment_name(module.name, assignment_type, i)
            description = self._generate_assignment_description(name, assignment_type)
            
            # Determine max attempts (usually unlimited for projects, 1-3 for quizzes/exams)
            if assignment_type in ["Quiz", "Exam"]:
                max_attempts = random.randint(1, 3)
            elif assignment_type == "Homework":
                max_attempts = random.randint(1, 5)
            else:
                max_attempts = None  # Unlimited attempts
            
            # Create the assignment
            assignment = Assignment(
                id=assignment_id,
                name=name,
                module_id=module.id,
                assign_date=assign_date,
                due_date=due_date,
                description=description,
                assignment_type=assignment_type,
                max_score=100.0,  # Standard max score
                weight=weight,
                max_attempts=max_attempts,
                course_id=module.course_id  # Add course_id from module
            )
            
            # Add to our lists
            module_assignments.append(assignment)
            self.assignments.append(assignment)
            
            # Update module's assignment list
            module.add_assignment(assignment.id)
        
        return module_assignments
    
    def generate_all_assignments(self) -> List[Assignment]:
        """
        Generate assignments for all modules.
        
        Returns:
            List[Assignment]: List of all generated assignments
        """
        # Clear existing assignments
        self.assignments = []
        
        # Generate assignments for each module
        for module in self.modules:
            self.generate_assignments_for_module(module)
        
        return self.assignments
    
    def get_assignments_for_module(self, module_id: str) -> List[Assignment]:
        """
        Get all assignments for a specific module.
        
        Args:
            module_id (str): ID of the module
            
        Returns:
            List[Assignment]: List of assignments for the module
        """
        return [a for a in self.assignments if a.module_id == module_id]
    
    def get_assignment_by_id(self, assignment_id: str) -> Optional[Assignment]:
        """
        Find an assignment by ID.
        
        Args:
            assignment_id (str): ID of the assignment to find
            
        Returns:
            Optional[Assignment]: The assignment if found, None otherwise
        """
        for assignment in self.assignments:
            if assignment.id == assignment_id:
                return assignment
        return None
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all assignments to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of assignment dictionaries
        """
        return [assignment.to_dict() for assignment in self.assignments]