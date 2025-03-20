"""
Detailed school data for the educational data generation pipeline.
This file contains expanded information about each school that will be used
in the data generation process.
"""
from typing import Dict, List, Any

# School data with expanded information about each school
SCHOOLS = [
    {
        "name": "REVODUCATE",
        "type": "General Education",
        "location": "Tel Aviv",
        "founding_year": 2010,
        "student_capacity": 950,
        "specialization": "Technology and Innovation",
        "website": "www.revoducate.edu",
        "ranking": 4.6,  # Out of 5
        "course_focus": ["Computer Science", "Mathematics", "Science", "Foreign Language"]
    },
    {
        "name": "אורט בהאמס",
        "type": "Technical",
        "location": "Haifa",
        "founding_year": 1980,
        "student_capacity": 1200,
        "specialization": "Engineering and Technical Skills",
        "website": "www.ort-bahamas.edu",
        "ranking": 4.2,
        "course_focus": ["Computer Science", "Mathematics", "Science", "Art"]
    },
    {
        "name": "בית ספר קציר - משגב",
        "type": "General Education",
        "location": "Misgav",
        "founding_year": 1995,
        "student_capacity": 800,
        "specialization": "Liberal Arts and Sciences",
        "website": "www.katzir-misgav.edu",
        "ranking": 4.4,
        "course_focus": ["Literature", "History", "Social Studies", "Science"]
    },
    {
        "name": "בית החינוך כרמל זבולון",
        "type": "Regional",
        "location": "Zevulun Valley",
        "founding_year": 1970,
        "student_capacity": 1000,
        "specialization": "Environmental Studies and Agriculture",
        "website": "www.carmel-zevulun.edu",
        "ranking": 3.9,
        "course_focus": ["Science", "Social Studies", "Physical Education", "Art"]
    },
    {
        "name": "בית הספר קציני ים עכו",
        "type": "Vocational",
        "location": "Acre",
        "founding_year": 1938,
        "student_capacity": 600,
        "specialization": "Maritime Studies and Navigation",
        "website": "www.naval-acre.edu",
        "ranking": 4.1,
        "course_focus": ["Mathematics", "Science", "Physical Education", "History"]
    },
    {
        "name": "אורט חקלאי פרדס חנה",
        "type": "Agricultural",
        "location": "Pardes Hanna-Karkur",
        "founding_year": 1952,
        "student_capacity": 850,
        "specialization": "Agriculture and Environmental Science",
        "website": "www.ort-agricultural.edu",
        "ranking": 4.0,
        "course_focus": ["Science", "Computer Science", "Social Studies", "Art"]
    }
]

# Course types and specializations that could be offered at these schools
COURSE_SPECIALIZATIONS = {
    "Technology and Innovation": [
        "Introduction to Programming",
        "Data Science Fundamentals",
        "Web Development",
        "Mobile App Creation",
        "Digital Marketing",
        "Entrepreneurship"
    ],
    "Engineering and Technical Skills": [
        "Engineering Principles",
        "3D Modeling and Design",
        "Electronics Fundamentals",
        "Robotics",
        "Technical Drawing",
        "Mechanical Systems"
    ],
    "Liberal Arts and Sciences": [
        "Literature Analysis",
        "World History",
        "Philosophy",
        "Political Science",
        "Creative Writing",
        "Sociology"
    ],
    "Environmental Studies and Agriculture": [
        "Environmental Science",
        "Sustainable Agriculture",
        "Ecology",
        "Natural Resource Management",
        "Climate Studies",
        "Conservation Biology"
    ],
    "Maritime Studies and Navigation": [
        "Maritime Navigation",
        "Marine Biology",
        "Naval Architecture",
        "Oceanography",
        "Seamanship",
        "Maritime Law"
    ],
    "Agriculture and Environmental Science": [
        "Agricultural Science",
        "Horticulture",
        "Soil Science",
        "Agricultural Economics",
        "Animal Science",
        "Sustainable Farming"
    ]
}

# Map to help generate appropriate course names for each school based on their focus
SUBJECT_COURSE_NAMES = {
    "Mathematics": [
        "Algebra and Functions",
        "Geometry and Measurement",
        "Calculus Foundations",
        "Statistics and Probability",
        "Mathematical Modeling",
        "Discrete Mathematics"
    ],
    "Science": [
        "Physics Principles",
        "Chemistry in Context",
        "Biology of Living Systems",
        "Earth and Space Science",
        "Laboratory Techniques",
        "Applied Scientific Research"
    ],
    "History": [
        "World History",
        "National History",
        "Ancient Civilizations",
        "Modern History",
        "Historical Research Methods",
        "Cultural Studies"
    ],
    "Literature": [
        "World Literature",
        "Literary Analysis",
        "Creative Writing",
        "Poetry and Expression",
        "Drama and Performance",
        "Contemporary Literature"
    ],
    "Computer Science": [
        "Introduction to Programming",
        "Data Structures and Algorithms",
        "Web Development",
        "Mobile App Development",
        "Databases and SQL",
        "Computer Systems"
    ],
    "Art": [
        "Visual Arts",
        "Studio Art",
        "Art History",
        "Digital Design",
        "Multimedia Production",
        "Photography"
    ],
    "Music": [
        "Music Theory",
        "Instrumental Practice",
        "Music Composition",
        "Music History",
        "Performance Skills",
        "Digital Music Production"
    ],
    "Physical Education": [
        "Team Sports",
        "Individual Fitness",
        "Health and Wellness",
        "Sports Science",
        "Recreation Management",
        "Outdoor Education"
    ],
    "Foreign Language": [
        "English Language",
        "Arabic Studies",
        "French Language",
        "Spanish Language",
        "Language Acquisition Theory",
        "Cultural Communication"
    ],
    "Social Studies": [
        "Sociology",
        "Psychology",
        "Economics",
        "Political Science",
        "Anthropology",
        "Geography and Culture"
    ]
}

# Helper function to get appropriate courses for a school
def get_courses_for_school(school_name: str) -> List[str]:
    """
    Returns a list of appropriate course names for the given school
    based on its specialization and course focus.
    """
    school = next((s for s in SCHOOLS if s["name"] == school_name), None)
    
    if not school:
        return []
    
    # Get specialization courses
    specialization_courses = COURSE_SPECIALIZATIONS.get(school["specialization"], [])
    
    # Get subject-focused courses
    subject_courses = []
    for subject in school["course_focus"]:
        subject_courses.extend(SUBJECT_COURSE_NAMES.get(subject, []))
    
    # Combine and return
    return specialization_courses + subject_courses