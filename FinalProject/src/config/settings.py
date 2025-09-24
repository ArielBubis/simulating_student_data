"""
Configuration settings for the educational data generation pipeline.
This file contains all the parameters that control the data generation process.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any

# School names from the requirements
SCHOOL_NAMES = [
    'אורט', 
    'אורט בהמה', 
    'בית ספר כציר - מסגב', 
    'מרכז חינוכי כרמל זבולון', 
    'בית ספר קציני חיל הים עכו', 
    'אירגון חקלאי פרדס חנה'
]

# Mid-semester configuration settings
MID_SEMESTER_SETTINGS = {
    # Default mid-semester date (can be overridden via command line)
    "target_date": datetime(2024, 11, 1),  # Set to approximately middle of academic year
    
    # Variation window (in days) around target date to create natural progress variation
    "variation_days": 14,  
    
    # Progress profile adjustments - how each student profile affects completion probability
    "profile_progress_modifiers": {
        "High Achiever": 0.3,      # High achievers are more likely to be ahead
        "Above Average": 0.15,     # Above average students slightly ahead
        "Average": 0,             # Average students on track
        "Struggling": -0.2         # Struggling students behind
    },
    
    # Subject strength impact - how subject proficiency affects completion likelihood
    "subject_strength_impact": 0.25,  # Maximum adjustment based on subject strength
    
    # Time factors - how assignment timing affects completion probability
    "time_decay_factor": 0.1,      # Rate at which older assignments are more likely completed
    
    # Minimum completion probabilities by profile
    "min_completion_probability": {
        "High Achiever": 0.7,
        "Above Average": 0.6,
        "Average": 0.5,
        "Struggling": 0.3
    },
    
    # Maximum completion probabilities for future assignments by profile
    "future_assignment_probability": {
        "High Achiever": 0.2,      # High achievers sometimes work ahead
        "Above Average": 0.1,
        "Average": 0.05,
        "Struggling": 0.0          # Struggling students don't work ahead
    }
}

# Academic calendar settings
ACADEMIC_YEAR = {
    "start_date": datetime(2024, 9, 1),  # September 1, 2024
    "end_date": datetime(2025, 6, 30),   # June 30, 2025
    "semester_break": {
        "start_date": datetime(2025, 1, 20),
        "end_date": datetime(2025, 2, 5)
    },
    "holidays": [
        {"name": "Rosh Hashanah", "start_date": datetime(2024, 10, 2), "end_date": datetime(2024, 10, 4)},
        {"name": "Yom Kippur", "start_date": datetime(2024, 10, 11), "end_date": datetime(2024, 10, 12)},
        {"name": "Sukkot", "start_date": datetime(2024, 10, 16), "end_date": datetime(2024, 10, 23)},
        {"name": "Hanukkah", "start_date": datetime(2024, 12, 25), "end_date": datetime(2025, 1, 2)},
        {"name": "Passover", "start_date": datetime(2025, 4, 12), "end_date": datetime(2025, 4, 20)},
        {"name": "Independence Day", "start_date": datetime(2025, 5, 6), "end_date": datetime(2025, 5, 6)}
    ]
}

# Course generation settings
COURSE_SETTINGS = {
    "min_courses_per_school": 5,
    "max_courses_per_school": 9,
    "subject_areas": [
        "מתמטיקה",        # Mathematics
        "מדעים",          # Sciences  
        "היסטוריה",       # History
        "ספרות",          # Literature
        "מדעי המחשב",     # Computer Science - Fixed encoding
        "אמנות",          # Art
        "מוזיקה",         # Music
        "חינוך גופני",    # Physical Education
        "שפות זרות",      # Foreign Languages
        "מדעי החברה"      # Social Sciences
    ],
    "course_duration_weeks": {
        "min": 10,
        "max": 40
    }
}

# Module generation settings
MODULE_SETTINGS = {
    "min_modules_per_course": 5,
    "max_modules_per_course": 30,
    # "min_modules_per_course": 1,
    # "max_modules_per_course": 5,

    "module_types": ["Theory", "Practice", "Project", "Research", "Discussion"],
    "required_module_probability": 0.8  # 80% chance a module is required
}

# Assignment generation settings
ASSIGNMENT_SETTINGS = {
    "min_assignments_per_module": 1,
    "max_assignments_per_module": 2,
    "assignment_types": [
        {
            "name": "Quiz",
            "weight": 0.15,
            "mean_score": 75,
            "std_dev": 12,
            "skewness": -0.5
        },
        {
            "name": "Exam",
            "weight": 0.30,
            "mean_score": 70,
            "std_dev": 15,
            "skewness": -0.7
        },
        {
            "name": "Homework",
            "weight": 0.20,
            "mean_score": 85,
            "std_dev": 8,
            "skewness": -1.0
        },
        {
            "name": "Project",
            "weight": 0.25,
            "mean_score": 82,
            "std_dev": 10,
            "skewness": -0.8
        },
        # {
        #     "name": "Participation",
        #     "weight": 0.10,
        #     "mean_score": 90,
        #     "std_dev": 5,
        #     "skewness": -1.2
        # }
    ],
    "late_submission_probability": 0.15,  # 15% chance of late submission
    "max_days_late": 5  # Maximum days late for submission
}

# User generation settings
USER_SETTINGS = {
    "teachers_per_school": {
        "min": 5,
        "max": 20
        # "min": 1,
        # "max": 3

    },
    "courses_per_teacher": {
        # "min": 1,
        # "max": 3
        "min": 1,
        "max": 5
    },
    "students_per_course": {
        "min": 12,
        "max": 30
        # "min": 7,
        # "max": 15

    },
    "student_performance_profiles": [
        {"name": "High Achiever", "base_score": 90, "consistency": 0.85, "proportion": 0.15},
        {"name": "Above Average", "base_score": 80, "consistency": 0.75, "proportion": 0.35},
        {"name": "Average", "base_score": 70, "consistency": 0.65, "proportion": 0.35},
        {"name": "Struggling", "base_score": 60, "consistency": 0.55, "proportion": 0.15}
    ],    # Correlation between subject areas (e.g., students good at math tend to be good at science)
    "subject_correlation": {
        "מתמטיקה": ["מדעי המחשב", "מדעים"],
        "מדעים": ["מתמטיקה", "מדעי המחשב"],
        "ספרות": ["היסטוריה", "שפה זרה"],
        "היסטוריה": ["ספרות", "מדעי החברה"],
        "מדעי המחשב": ["מתמטיקה", "מדעים"],
        "שפה זרה": ["ספרות"],
        "מדעי החברה": ["היסטוריה"]
    }
}

# Time tracking settings
TIME_TRACKING = {
    "time_per_assignment_minutes": {
        "Quiz": {"min": 10, "max": 60},
        "Exam": {"min": 30, "max": 180},
        "Homework": {"min": 30, "max": 120},
        "Project": {"min": 60, "max": 600},
        # "Participation": {"min": 30, "max": 90}
    },
    "time_variability": 0.3  # 30% random variation in time spent
}

# Database settings
DATABASE_SETTINGS = {
    "batch_size": 500  # Number of documents to write in a single batch
}

