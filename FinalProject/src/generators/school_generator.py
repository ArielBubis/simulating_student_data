"""
School generator module for creating school entities.
This module generates realistic school data using the configuration in settings.py and school_data.py.
"""
import random
from typing import List, Dict, Any, Optional

from config.settings import SCHOOL_NAMES
from config.school_data import SCHOOLS
from generators.id_generator import generate_school_id
from datetime import datetime
from models.school import School

# class School:
#     """
#     School model class representing an educational institution.
#     """
#     def __init__(
#         self,
#         id: str,
#         name: str,
#         type: str,
#         location: str,
#         founding_year: int,
#         student_capacity: int,
#         specialization: str,
#         website: str,
#         ranking: float
#     ):
#         self.id = id
#         self.name = name
#         self.type = type
#         self.location = location
#         self.founding_year = founding_year
#         self.student_capacity = student_capacity
#         self.specialization = specialization
#         self.website = website
#         self.ranking = ranking
#         self.course_focus = []  # Will be populated from config
#         self.created_at = datetime.now()
#         self.updated_at = datetime.now()
    
#     def to_dict(self) -> Dict[str, Any]:
#         """
#         Convert the School object to a dictionary for Firestore.
        
#         Returns:
#             Dict[str, Any]: School data as a dictionary
#         """
#         return {
#             "id": self.id,
#             "name": self.name,
#             "type": self.type,
#             "location": self.location,
#             "foundingYear": self.founding_year,
#             "studentCapacity": self.student_capacity,
#             "specialization": self.specialization,
#             "website": self.website,
#             "ranking": self.ranking,
#             "courseFocus": self.course_focus,
#             "createdAt": self.created_at,
#             "updatedAt": self.updated_at
#         }


class SchoolGenerator:
    """
    Generator class for creating realistic school data.
    """
    def __init__(self):
        """
        Initialize the SchoolGenerator.
        """
        self.schools: List[School] = []

    def generate_schools(self) -> List[School]:
        """
        Generate school data based on configuration.
        
        Returns:
            List[School]: List of generated School objects
        """
        # Clear any existing schools
        self.schools = []
        
        # Generate a school for each name in the configuration
        for school_data in SCHOOLS:
            # Generate a unique ID for this school
            school_id = generate_school_id()
            
            # Create a new School object
            school = School(
                id=school_id,
                name=school_data["name"],
                type=school_data["type"],
                location=school_data["location"],
                founding_year=school_data["founding_year"],
                student_capacity=school_data["student_capacity"],
                specialization=school_data["specialization"],
                website=school_data["website"],
                ranking=school_data["ranking"]
            )
            
            # Add course focus
            school.course_focus = school_data.get("course_focus", [])
            # Add the school to our list
            self.schools.append(school)
            
        return self.schools

    def get_school_by_name(self, name: str) -> Optional[School]:
        """
        Find a school by its name.
        
        Args:
            name (str): The name of the school to find
            
        Returns:
            Optional[School]: The school object if found, None otherwise
        """
        for school in self.schools:
            if school.name == name:
                return school
        return None
    
    def get_school_by_id(self, school_id: str) -> Optional[School]:
        """
        Find a school by its ID.
        
        Args:
            school_id (str): The ID of the school to find
            
        Returns:
            Optional[School]: The school object if found, None otherwise
        """
        for school in self.schools:
            if school.id == school_id:
                return school
        return None
    
    def get_all_schools(self) -> List[School]:
        """
        Get all generated schools.
        
        Returns:
            List[School]: List of all School objects
        """
        return self.schools
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all schools to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of school dictionaries ready for Firestore
        """
        return [school.to_dict() for school in self.schools]


# Example usage
if __name__ == "__main__":
    # This code only runs if the file is executed directly (not imported)
    generator = SchoolGenerator()
    schools = generator.generate_schools()
    
    print(f"Generated {len(schools)} schools:")
    for school in schools:
        print(f"- {school.name} ({school.id}): {school.specialization}")