"""
Date utilities for generating realistic academic timelines.
This module provides functions for creating and validating date sequences
for courses, modules, assignments, and submissions.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

from config.settings import ACADEMIC_YEAR


def is_in_holiday(date: datetime) -> bool:
    """
    Check if a given date falls within a holiday period.
    
    Args:
        date (datetime): The date to check
        
    Returns:
        bool: True if the date is within a holiday period, False otherwise
    """
    # Check semester break
    semester_break = ACADEMIC_YEAR.get("semester_break", {})
    if (semester_break.get("start_date") and 
        semester_break.get("end_date") and
        semester_break["start_date"] <= date <= semester_break["end_date"]):
        return True
    
    # Check other holidays
    for holiday in ACADEMIC_YEAR.get("holidays", []):
        if (holiday.get("start_date") and 
            holiday.get("end_date") and
            holiday["start_date"] <= date <= holiday["end_date"]):
            return True
    
    return False


def get_next_valid_date(start_date: datetime, days_to_add: int = 1) -> datetime:
    """
    Get the next valid date by skipping holidays.
    
    Args:
        start_date (datetime): The starting date
        days_to_add (int): Number of days to add (default: 1)
        
    Returns:
        datetime: The next valid date
    """
    current_date = start_date
    days_added = 0
    
    while days_added < days_to_add:
        current_date += timedelta(days=1)
        if not is_in_holiday(current_date):
            days_added += 1
    
    return current_date


def generate_course_dates() -> Tuple[datetime, datetime]:
    """
    Generate realistic start and end dates for a course within the academic year.
    
    Returns:
        Tuple[datetime, datetime]: A tuple of (start_date, end_date)
    """
    academic_start = ACADEMIC_YEAR.get("start_date", datetime(2023, 9, 1))
    academic_end = ACADEMIC_YEAR.get("end_date", datetime(2024, 6, 30))
    
    # Courses typically start at the beginning of a semester
    # First semester starts at the beginning of the academic year
    # Second semester starts after the semester break
    
    semester_break = ACADEMIC_YEAR.get("semester_break", {})
    semester_break_end = semester_break.get("end_date")
    
    # 70% chance of first semester, 30% chance of second semester
    if semester_break_end and random.random() > 0.7:
        # Second semester course
        start_date = semester_break_end + timedelta(days=random.randint(0, 7))
        
        # Course duration between 10-20 weeks
        duration_weeks = random.randint(10, 20)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Ensure end date is within academic year
        end_date = min(end_date, academic_end)
    else:
        # First semester course
        start_date = academic_start + timedelta(days=random.randint(0, 14))
        
        # Course duration between 10-20 weeks
        duration_weeks = random.randint(10, 20)
        end_date = start_date + timedelta(weeks=duration_weeks)
        
        # Ensure end date is within first semester or academic year
        if semester_break and semester_break.get("start_date"):
            end_date = min(end_date, semester_break["start_date"] - timedelta(days=1))
        end_date = min(end_date, academic_end)
    
    return start_date, end_date


def generate_module_dates(
    course_start: datetime, 
    course_end: datetime, 
    module_count: int
) -> List[Tuple[datetime, datetime]]:
    """
    Generate a chronological sequence of module dates within a course timeline.
    
    Args:
        course_start (datetime): Course start date
        course_end (datetime): Course end date
        module_count (int): Number of modules to generate dates for
        
    Returns:
        List[Tuple[datetime, datetime]]: List of (start_date, end_date) tuples for each module
    """
    total_days = (course_end - course_start).days
    
    # Ensure we have enough days for all modules
    if total_days < module_count * 7:
        # If not enough days, reduce module count or extend course
        module_count = max(1, total_days // 7)
    
    # Calculate average module duration
    avg_module_days = total_days // module_count
    
    module_dates = []
    current_start = course_start
    
    for i in range(module_count):
        # Last module ends exactly at course end
        if i == module_count - 1:
            module_dates.append((current_start, course_end))
            break
        
        # Add some variability to module duration
        variation = random.uniform(0.7, 1.3)
        module_days = int(avg_module_days * variation)
        
        # Ensure minimum module duration of 7 days
        module_days = max(7, module_days)
        
        module_end = current_start + timedelta(days=module_days)
        
        # Ensure module end doesn't exceed course end
        module_end = min(module_end, course_end)
        
        module_dates.append((current_start, module_end))
        
        # Next module starts after current one
        current_start = module_end + timedelta(days=1)
        
        # If we've reached the course end, stop generating modules
        if current_start >= course_end:
            break
    
    return module_dates


def generate_assignment_date(
    module_start: datetime, 
    module_end: datetime
) -> Tuple[datetime, datetime]:
    """
    Generate realistic due dates for an assignment within a module.
    
    Args:
        module_start (datetime): Module start date
        module_end (datetime): Module end date
        
    Returns:
        Tuple[datetime, datetime]: A tuple of (assign_date, due_date)
    """
    total_days = (module_end - module_start).days
    
    # Ensure minimum duration
    if total_days < 3:
        assign_date = module_start
        due_date = module_end
        return assign_date, due_date
    
    # Assignment is given in the first third of the module
    assign_date_offset = random.randint(0, max(1, total_days // 3))
    assign_date = module_start + timedelta(days=assign_date_offset)
    
    # Due date is in the last third of the module
    due_date_offset = random.randint(max(1, 2 * total_days // 3), total_days)
    due_date = module_start + timedelta(days=due_date_offset)
    
    # Ensure due date doesn't exceed module end
    due_date = min(due_date, module_end)
    
    # Ensure assign date is before due date
    if assign_date >= due_date:
        assign_date = module_start
    
    return assign_date, due_date


def generate_submission_date(
    assign_date: datetime, 
    due_date: datetime, 
    is_late: bool = False, 
    max_days_late: int = 5
) -> datetime:
    """
    Generate a realistic submission date for an assignment.
    
    Args:
        assign_date (datetime): Date when the assignment was given
        due_date (datetime): Due date for the assignment
        is_late (bool): Whether the submission is late (default: False)
        max_days_late (int): Maximum days late for a late submission (default: 5)
        
    Returns:
        datetime: A realistic submission date
    """
    if assign_date >= due_date:
        # If dates are invalid, return due date
        return due_date
    
    total_days = (due_date - assign_date).days
    
    if is_late:
        # Late submission (after due date)
        days_late = random.randint(1, max_days_late)
        return due_date + timedelta(days=days_late)
    else:
        # On-time submission
        if total_days <= 1:
            # If very short assignment, submit on due date
            return due_date
        
        # Most students submit close to the deadline
        # Use exponential distribution to model this
        days_before_due = random.expovariate(1.0) * total_days
        days_before_due = min(total_days - 1, int(days_before_due))
        
        submission_date = due_date - timedelta(days=days_before_due)
        
        # Ensure submission is after assignment date
        submission_date = max(submission_date, assign_date + timedelta(days=1))
        
        return submission_date


def format_date(date: datetime) -> str:
    """
    Format a datetime object as a string in ISO format.
    
    Args:
        date (datetime): The date to format
        
    Returns:
        str: Formatted date string
    """
    return date.isoformat()


def get_formatted_academic_calendar() -> Dict[str, Any]:
    """
    Get a formatted version of the academic calendar from settings.
    
    Returns:
        Dict[str, Any]: Formatted academic calendar
    """
    calendar = {
        "academicYear": {
            "startDate": format_date(ACADEMIC_YEAR.get("start_date", datetime(2023, 9, 1))),
            "endDate": format_date(ACADEMIC_YEAR.get("end_date", datetime(2024, 6, 30)))
        }
    }
    
    # Add semester break if available
    semester_break = ACADEMIC_YEAR.get("semester_break", {})
    if semester_break.get("start_date") and semester_break.get("end_date"):
        calendar["semesterBreak"] = {
            "startDate": format_date(semester_break["start_date"]),
            "endDate": format_date(semester_break["end_date"])
        }
    
    # Add holidays
    calendar["holidays"] = []
    for holiday in ACADEMIC_YEAR.get("holidays", []):
        if holiday.get("start_date") and holiday.get("end_date"):
            calendar["holidays"].append({
                "name": holiday.get("name", "Holiday"),
                "startDate": format_date(holiday["start_date"]),
                "endDate": format_date(holiday["end_date"])
            })
    
    return calendar