"""
Detailed school data for the educational data generation pipeline.
This file contains expanded information about each school that will be used
in the data generation process.
"""
from typing import Dict, List, Any

# School data with expanded information about each school
SCHOOLS = [   
     {
        "name": "אורט",
        "type": "General Education",
        "location": "תל אביב",
        "founding_year": 2010,        "student_capacity": 950,
        "specialization": "טכנולוגיה וחדשנות",
        "website": "www.revoducate.edu","ranking": 4.6,  # Out of 5
        "course_focus": ["מדעי המחשב", "מתמטיקה", "מדעים", "שפה זרה"]
    },
            {
        "name": "אורט בהמה",
        "type": "Technical",
        "location": "חיפה",
        "founding_year": 1980,        
        "student_capacity": 1200,
        "specialization": "הנדסה ומיומנויות טכניות",
        "website": "www.ort-bahamas.edu",
        "ranking": 4.2,
        "course_focus": ["מדעי המחשב", "מתמטיקה", "מדעים", "אמנות"]
    },
    {
        "name": "בית ספר כציר - מסגב",
        "type": "General Education",
        "location": "מסגב",
        "founding_year": 1995,        "student_capacity": 800,
        "specialization": "מדעי הרוח והחברה",
        "website": "www.katzir-misgav.edu","ranking": 4.4,
        "course_focus": ["ספרות", "היסטוריה", "מדעי החברה", "מדעים"]
    },
    {
        "name": "מרכז חינוכי כרמל זבולון",
        "type": "Regional",
        "location": "עמק זבולון",
        "founding_year": 1970,        "student_capacity": 1000,
        "specialization": "לימודי סביבה וחקלאות",
        "website": "www.carmel-zevulun.edu","ranking": 3.9,
        "course_focus": ["מדעים", "מדעי החברה", "חינוך גופני", "אמנות"]
    },
    {
        "name": "בית ספר קציני חיל הים עכו",
        "type": "Vocational",
        "location": "עכו",
        "founding_year": 1938,        "student_capacity": 600,
        "specialization": "לימודים ימיים וניווט",
        "website": "www.naval-acre.edu","ranking": 4.1,
        "course_focus": ["מתמטיקה", "מדעים", "חינוך גופני", "היסטוריה"]
    },
    {
        "name": "אירגון חקלאי פרדס חנה",
        "type": "Agricultural",
        "location": "פרדס חנה-כרכור",
        "founding_year": 1952,        "student_capacity": 850,
        "specialization": "חקלאות ומדעי הסביבה",
        "website": "www.ort-agricultural.edu","ranking": 4.0,
        "course_focus": ["מדעים", "מדעי המחשב", "מדעי החברה", "אמנות"]
    }
]
# Course types and specializations that could be offered at these schools
# COURSE_SPECIALIZATIONS = {
#     "Technology and Innovation": [
#         "Design Patterns",
#         "Graphic Design Fundamentals", 
#         "Web Development",
#         "Mobile App Creation",
#         "Data Science Fundamentals",
#         "Digital Marketing",
#         "מערכות ספרתיות",
#         "תכנות מתקדם",
#         "עיצוב גרפי",
#         "פיתוח אפליקציות"
#     ],
#     "Engineering and Technical Skills": [
#         "Engineering Principles",
#         "3D Modeling and Design",
#         "Electronics Fundamentals",
#         "רובוטיקה",
#         "Technical Drawing",
#         "Mechanical Systems",
#         "הנדסת חשמל",
#         "מערכות מכניות",
#         "עיצוב תלת מימד"
#     ],
#     "Liberal Arts and Sciences": [
#         "Literature Analysis",
#         "World History",
#         "Philosophy",
#         "Political Science",
#         "Creative Writing",
#         "Sociology",
#         "ספרות עברית",
#         "היסטוריה של ישראל",
#         "פילוסופיה יהודית",
#         "מדעי החברה"
#     ],
#     "Environmental Studies and Agriculture": [
#         "Environmental Science",
#         "Sustainable Agriculture",
#         "Ecology",
#         "Natural Resource Management",
#         "Climate Studies",
#         "Conservation Biology",
#         "מדעי הסביבה",
#         "חקלאות בת קיימא",
#         "אקולוגיה",
#         "שימור טבע"
#     ],
#     "Maritime Studies and Navigation": [
#         "Maritime Navigation",
#         "Marine Biology",
#         "Naval Architecture",
#         "Oceanography",
#         "Seamanship",
#         "Maritime Law",
#         "ניווט חופי",
#         "ניווט מכשירים",
#         "חוקי הים",
#         "אוקיינוגרפיה",
#         "ביולוגיה ימית"
#     ],
#     "Agriculture and Environmental Science": [
#         "Agricultural Science",
#         "Horticulture",
#         "Soil Science",
#         "Agricultural Economics",
#         "Animal Science",
#         "Sustainable Farming",
#         "מדעי החקלאות",
#         "גננות",
#         "מדעי הקרקע",
#         "כלכלה חקלאית"
#     ]
# }

# # Map to help generate appropriate course names for each school based on their focus
# SUBJECT_COURSE_NAMES = {
#     "Mathematics": [
#         "Algebra and Functions",
#         "Geometry and Measurement", 
#         "Calculus Foundations",
#         "Statistics and Probability",
#         "Mathematical Modeling",
#         "Discrete Mathematics",
#         "מתמטיקה - בגרות",
#         "אלגברה ליניארית",
#         "חשבון דיפרנציאלי",
#         "סטטיסטיקה"
#     ],
#     "Science": [
#         "Physics Principles",
#         "Chemistry in Context",
#         "Biology of Living Systems",
#         "Earth and Space Science",
#         "Laboratory Techniques",
#         "Applied Scientific Research",
#         "פיזיקה - בגרות",
#         "כימיה - בגרות", 
#         "ביולוגיה - בגרות",
#         "מדעי כדור הארץ"
#     ],
#     "History": [
#         "World History",
#         "National History",
#         "Ancient Civilizations",
#         "Modern History",
#         "Historical Research Methods",
#         "Cultural Studies",
#         "היסטוריה - בגרות",
#         "תולדות עם ישראל",
#         "היסטוריה של המזרח התיכון",
#         "מחקר היסטורי"
#     ],
#     "Literature": [
#         "World Literature",
#         "Poetry Analysis",
#         "Creative Writing",
#         "Contemporary Literature",
#         "Literary Criticism",
#         "Drama and Theater",
#         "ספרות עברית - בגרות",
#         "שירה עברית",
#         "ספרות עולמית",
#         "כתיבה יצירתית"
#     ],
#     "Social Studies": [
#         "Sociology Fundamentals",
#         "Psychology Basics",
#         "Economics Principles",
#         "Political Science",
#         "Anthropology",
#         "Human Geography",
#         "אזרחות - בגרות",
#         "פסיכולוגיה",
#         "סוציולוגיה",
#         "כלכלה"
#     ],
#     "Computer Science": [
#         "Programming Fundamentals",
#         "Data Structures",
#         "Algorithm Design",
#         "Web Development",
#         "Database Systems",
#         "Software Engineering",
#         "מדעי המחשב - בגרות",
#         "תכנות בשפת Python",
#         "מבני נתונים",
#         "פיתוח אתרים"
#     ],
#     "Foreign Language": [
#         "English as Second Language",
#         "French Language",
#         "Spanish Language",
#         "German Language",
#         "Arabic Language",
#         "Language Literature",
#         "אנגלית - בגרות",
#         "ערבית - בגרות",
#         "צרפתית",
#         "ספרדית"
#     ],
#     "Art": [
#         "Visual Arts",
#         "Digital Art",
#         "Photography",
#         "Sculpture",
#         "Drawing and Painting",
#         "Art History",
#         "אמנות פלסטית - בגרות",
#         "עיצוב גרפי",
#         "צילום",
#         "פיסול"
#     ],
#     "Physical Education": [
#         "Physical Fitness",
#         "Team Sports",
#         "Individual Sports",
#         "Health Education",
#         "Sports Psychology",
#         "Athletic Training",
#         "חינוך גופני - בגרות",
#         "כושר גופני",
#         "ספורט קבוצתי",
#         "מחול"    ]
# }
COURSE_SPECIALIZATIONS = {
    "טכנולוגיה וחדשנות": [
        "תבניות עיצוב",
        "יסודות עיצוב גרפי",
        "פיתוח אתרי אינטרנט",
        "בניית אפליקציות לנייד",
        "יסודות מדע הנתונים",
        "שיווק דיגיטלי",
        "מערכות ספרתיות",
        "תכנות מתקדם",
        "עיצוב גרפי",
        "פיתוח אפליקציות"
    ],
    "הנדסה ומיומנויות טכניות": [
        "עקרונות הנדסה",
        "עיצוב ותלת מימד",
        "יסודות באלקטרוניקה",
        "רובוטיקה",
        "שרטוט טכני",
        "מערכות מכניות",
        "הנדסת חשמל",
        "מערכות מכניות",
        "עיצוב תלת מימד"
    ],
    "מדעי הרוח והחברה": [
        "ניתוח ספרות",
        "היסטוריה עולמית",
        "פילוסופיה",
        "מדע המדינה",
        "כתיבה יוצרת",
        "סוציולוגיה",
        "ספרות עברית",
        "היסטוריה של ישראל",
        "פילוסופיה יהודית",
        "מדעי החברה"
    ],
    "לימודי סביבה וחקלאות": [
        "מדעי הסביבה",
        "חקלאות בת קיימא",
        "אקולוגיה",
        "ניהול משאבים טבעיים",
        "לימודי אקלים",
        "ביולוגיה של שימור",
        "מדעי הסביבה",
        "חקלאות בת קיימא",
        "אקולוגיה",
        "שימור טבע"
    ],
    "לימודים ימיים וניווט": [
        "ניווט ימי",
        "ביולוגיה ימית",
        "אדריכלות ימית",
        "אוקיינוגרפיה",
        "ימאות",
        "חוקי ים",
        "ניווט חופי",
        "ניווט מכשירים",
        "חוקי הים",
        "אוקיינוגרפיה",
        "ביולוגיה ימית"
    ],
    "חקלאות ומדעי הסביבה": [
        "מדעי החקלאות",
        "גננות",
        "מדעי הקרקע",
        "כלכלה חקלאית",
        "מדעי בעלי חיים",
        "חקלאות בת קיימא",
        "מדעי החקלאות",
        "גננות",
        "מדעי הקרקע",
        "כלכלה חקלאית"
    ]
}

# מפת נושאים לקורסים רלוונטיים לפי תחום התמחות
SUBJECT_COURSE_NAMES = {
    "מתמטיקה": [
        "אלגברה ופונקציות",
        "גיאומטריה ומדידות",
        "יסודות החשבון האינפיניטסימלי",
        "סטטיסטיקה והסתברות",
        "מודלים מתמטיים",
        "מתמטיקה בדידה",
        "מתמטיקה - בגרות",
        "אלגברה ליניארית",
        "חשבון דיפרנציאלי",
        "סטטיסטיקה"
    ],
    "מדעים": [
        "יסודות הפיזיקה",
        "כימיה בהקשר יישומי",
        "ביולוגיה של מערכות חיות",
        "מדעי כדור הארץ והחלל",
        "טכניקות מעבדה",
        "מחקר מדעי יישומי",
        "פיזיקה - בגרות",
        "כימיה - בגרות", 
        "ביולוגיה - בגרות",
        "מדעי כדור הארץ"
    ],
    "היסטוריה": [
        "היסטוריה עולמית",
        "היסטוריה לאומית",
        "תרבויות עתיקות",
        "היסטוריה מודרנית",
        "שיטות מחקר היסטורי",
        "לימודי תרבות",
        "היסטוריה - בגרות",
        "תולדות עם ישראל",
        "היסטוריה של המזרח התיכון",
        "מחקר היסטורי"
    ],
    "ספרות": [
        "ספרות עולמית",
        "ניתוח שירה",
        "כתיבה יצירתית",
        "ספרות עכשווית",
        "ביקורת ספרותית",
        "תיאטרון ודרמה",
        "ספרות עברית - בגרות",
        "שירה עברית",
        "ספרות עולמית",
        "כתיבה יצירתית"
    ],
    "מדעי החברה": [
        "יסודות סוציולוגיה",
        "מבוא לפסיכולוגיה",
        "עקרונות בכלכלה",
        "מדע המדינה",
        "אנתרופולוגיה",
        "גיאוגרפיה אנושית",
        "אזרחות - בגרות",
        "פסיכולוגיה",
        "סוציולוגיה",
        "כלכלה"
    ],
    "מדעי המחשב": [
        "יסודות תכנות",
        "מבני נתונים",
        "תכנון אלגוריתמים",
        "פיתוח אתרים",
        "מערכות בסיסי נתונים",
        "הנדסת תוכנה",
        "מדעי המחשב - בגרות",
        "תכנות בשפת Python",
        "מבני נתונים",
        "פיתוח אתרים"
    ],
    "שפות זרות": [
        "אנגלית כשפה שנייה",
        "צרפתית",
        "ספרדית",
        "גרמנית",
        "ערבית",
        "ספרות בשפה זרה",
        "אנגלית - בגרות",
        "ערבית - בגרות",
        "צרפתית",
        "ספרדית"
    ],
    "אמנות": [
        "אמנות חזותית",
        "אמנות דיגיטלית",
        "צילום",
        "פיסול",
        "ציור ורישום",
        "תולדות האמנות",
        "אמנות פלסטית - בגרות",
        "עיצוב גרפי",
        "צילום",
        "פיסול"
    ],
    "חינוך גופני": [
        "כושר גופני",
        "ספורט קבוצתי",
        "ספורט אישי",
        "חינוך לבריאות",
        "פסיכולוגיית ספורט",
        "אימון אתלטי",
        "חינוך גופני - בגרות",
        "כושר גופני",
        "ספורט קבוצתי",
        "מחול"
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