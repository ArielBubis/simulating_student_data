"""
ID Generator module for creating unique identifiers for educational data.
This module provides functions to generate 9-digit IDs for various entities.
"""
import random
import uuid
from typing import Set, Dict, Any

# Track used IDs to ensure uniqueness
_used_ids: Dict[str, Set[str]] = {
    "users": set(),
    "schools": set(),
    "courses": set(),
    "modules": set(),
    "assignments": set()
}

def generate_user_id() -> str:
    """
    Generate a unique 9-digit ID for a user (student or teacher).
    Format: 9 digits, starting with 1-9 (not 0)
    
    Returns:
        str: A unique 9-digit ID
    """
    while True:
        # Generate a 9-digit number, ensuring first digit isn't 0
        first_digit = random.randint(1, 9)
        rest_digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
        user_id = f"{first_digit}{rest_digits}"
        
        # Ensure uniqueness
        if user_id not in _used_ids["users"]:
            _used_ids["users"].add(user_id)
            return user_id


def generate_school_id() -> str:
    """
    Generate a unique ID for a school.
    Format: 'SCH' + 6 digits
    
    Returns:
        str: A unique school ID
    """
    while True:
        # Generate a 6-digit number
        digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        school_id = f"SCH{digits}"
        
        # Ensure uniqueness
        if school_id not in _used_ids["schools"]:
            _used_ids["schools"].add(school_id)
            return school_id


def generate_course_id() -> str:
    """
    Generate a unique ID for a course.
    Format: 'CRS' + 6 digits
    
    Returns:
        str: A unique course ID
    """
    while True:
        # Generate a 6-digit number
        digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        course_id = f"CRS{digits}"
        
        # Ensure uniqueness
        if course_id not in _used_ids["courses"]:
            _used_ids["courses"].add(course_id)
            return course_id


def generate_module_id() -> str:
    """
    Generate a unique ID for a module.
    Format: 'MOD' + 6 digits
    
    Returns:
        str: A unique module ID
    """
    while True:
        # Generate a 6-digit number
        digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        module_id = f"MOD{digits}"
        
        # Ensure uniqueness
        if module_id not in _used_ids["modules"]:
            _used_ids["modules"].add(module_id)
            return module_id


def generate_assignment_id() -> str:
    """
    Generate a unique ID for an assignment.
    Format: 'ASG' + 6 digits
    
    Returns:
        str: A unique assignment ID
    """
    while True:
        # Generate a 6-digit number
        digits = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        assignment_id = f"ASG{digits}"
        
        # Ensure uniqueness
        if assignment_id not in _used_ids["assignments"]:
            _used_ids["assignments"].add(assignment_id)
            return assignment_id


def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a generic unique ID using UUID.
    Useful for junction records or other entities.
    
    Args:
        prefix (str, optional): A prefix to add to the ID. Defaults to "".
    
    Returns:
        str: A unique ID
    """
    # Generate a UUID and take the first 8 characters
    unique_id = str(uuid.uuid4()).replace('-', '')[:8]
    return f"{prefix}{unique_id}" if prefix else unique_id


def reset_used_ids() -> None:
    """
    Reset all used IDs. Useful for testing or starting fresh.
    """
    for key in _used_ids:
        _used_ids[key] = set()


def get_id_stats() -> Dict[str, int]:
    """
    Get statistics on how many IDs have been generated.
    
    Returns:
        Dict[str, int]: A dictionary with counts of used IDs by entity type
    """
    return {key: len(value) for key, value in _used_ids.items()}