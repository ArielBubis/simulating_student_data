"""
User model for the educational data generator.
This module defines the base User class that Teacher and Student will inherit from.
"""
from typing import Dict, Any, Optional
from datetime import datetime


class User:
    """
    Base User class representing any user in the system.
    This is the parent class for Teacher and Student classes.
    """
    def __init__(
        self,
        id: str,
        name: str,
        email: str,
        phone: Optional[str] = None,
        school_id: Optional[str] = None
    ):
        """
        Initialize a new User instance.
        
        Args:
            id (str): Unique 9-digit identifier for the user
            name (str): Full name of the user
            email (str): Email address of the user
            phone (Optional[str]): Phone number of the user
            school_id (Optional[str]): ID of the school the user belongs to
        """
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.school_id = school_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def update_school(self, school_id: str) -> None:
        """
        Update the user's school.
        
        Args:
            school_id (str): ID of the new school
        """
        self.school_id = school_id
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the User object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: User data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "schoolId": self.school_id,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """
        Create a User instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing user data
            
        Returns:
            User: A new User instance
        """
        user = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            email=data.get('email', ''),
            phone=data.get('phone'),
            school_id=data.get('schoolId')
        )
        
        # Set timestamps if available
        if 'createdAt' in data:
            user.created_at = data['createdAt']
        if 'updatedAt' in data:
            user.updated_at = data['updatedAt']
            
        return user
    
    def __repr__(self) -> str:
        """
        String representation of the User instance.
        
        Returns:
            str: A string representation
        """
        return f"User(id={self.id}, name={self.name})"