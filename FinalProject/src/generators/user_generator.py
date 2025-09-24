"""
User Generator module for creating realistic teacher and student data.
This module provides classes for generating Teacher and Student objects.
"""
import random
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from faker import Faker

from config.settings import USER_SETTINGS
from models.teacher import Teacher
from models.student import Student
from models.school import School
from generators.id_generator import generate_user_id
from utils.distribution_utils import generate_correlated_subject_performance

# Hebrew names for realistic Israeli students and teachers (RTL formatted)
HEBREW_FIRST_NAMES = {
    'male': [
        'אריאל', 'דוד', 'יוסף', 'מיכאל', 'דניאל', 'אבירם', 'רון', 'עמית', 'תום', 'נועם',
        'יונתן', 'אלעד', 'איתי', 'שי', 'גיל', 'עומר', 'אורי', 'יובל', 'נתן', 'עידו',
        'ליאור', 'אוהד', 'אלון', 'טל', 'רועי', 'אורן', 'יאיר', 'בן', 'משה', 'אחמד'
    ],
    'female': [
        'שרה', 'רבקה', 'רחל', 'לאה', 'מירב', 'נועה', 'שירה', 'תמר', 'רונית', 'דנה',
        'מיכל', 'יעל', 'ליאור', 'מעיין', 'שני', 'רותם', 'אוריה', 'גלי', 'הדר', 'ענבל',
        'אילנה', 'נעמה', 'עדי', 'ליה', 'אביבה', 'זהר', 'ארבל', 'מור', 'אילה', 'פאטמה'
    ]
}

HEBREW_LAST_NAMES = [
    'כהן', 'לוי', 'מזרחי', 'פרץ', 'ביטון', 'דהן', 'אברמוביץ', 'פרידמן', 'כהן', 'אמיר',
    'שמואל', 'רוזנברג', 'גולדשטיין', 'ישראלי', 'עמר', 'אלכסנדר', 'חדד', 'עזרא', 'שמעון', 'יעקב',
    'אשכנזי', 'יוסף', 'בן דוד', 'אליאס', 'נחמן', 'גרין', 'בראון', 'שוורץ', 'ציון', 'סולומון'
]


def generate_hebrew_name() -> Tuple[str, str]:
    """Generate a Hebrew first and last name with proper RTL formatting."""
    gender = random.choice(['male', 'female'])
    first_name = random.choice(HEBREW_FIRST_NAMES[gender])
    last_name = random.choice(HEBREW_LAST_NAMES)
    return first_name, last_name


def format_hebrew_full_name(first_name: str, last_name: str) -> str:
    """
    Format Hebrew names properly for display.
    In Hebrew, the format is typically: first_name last_name
    """
    return f"{first_name} {last_name}"


def create_english_email_from_hebrew_name(first_name: str, last_name: str, school_name: str, user_type: str = "student") -> str:
    """
    Create an English email from Hebrew names to avoid Hebrew characters in emails.
    
    Args:
        first_name (str): Hebrew first name
        last_name (str): Hebrew last name  
        school_name (str): School name (might be Hebrew)
        user_type (str): 'student' or 'teacher'
    
    Returns:
        str: English email address
    """
    # Hebrew to English transliteration mapping
    transliteration_map = {
        'א': 'a', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h', 'ו': 'v', 'ז': 'z', 'ח': 'ch',
        'ט': 't', 'י': 'y', 'כ': 'k', 'ך': 'k', 'ל': 'l', 'מ': 'm', 'ם': 'm', 'ן': 'n',
        'נ': 'n', 'ס': 's', 'ע': 'a', 'פ': 'p', 'ף': 'f', 'צ': 'tz', 'ץ': 'tz', 'ק': 'k',
        'ר': 'r', 'ש': 'sh', 'ת': 't'
    }
    
    def transliterate_hebrew(text: str) -> str:
        """Transliterate Hebrew text to English."""
        result = ""
        for char in text:
            if char in transliteration_map:
                result += transliteration_map[char]
            else:
                result += char
        return result
    
    # Transliterate names
    eng_first = transliterate_hebrew(first_name).lower()
    eng_last = transliterate_hebrew(last_name).lower()
    
    # Clean school name for email domain
    school_domain = re.sub(r'[^\w]', '', school_name.lower())
    school_domain = transliterate_hebrew(school_domain)
    
    if user_type == "student":
        # Students get username + random number format
        username = f"{eng_first}{random.randint(1, 999)}"
        email = f"{username}@student.{school_domain}.edu"
    else:
        # Teachers get formal first.last format
        email = f"{eng_first}.{eng_last}@{school_domain}.edu"
    
    return email


class UserGenerator:
    """
    Base class for generating user data.
    """
    def __init__(self, schools: List[School]):
        """
        Initialize the UserGenerator.
        
        Args:
            schools (List[School]): List of schools to assign users to
        """
        self.faker = Faker()
        self.schools = schools
        
        # Ensure we have some schools to work with
        if not schools:
            raise ValueError("No schools provided for user generation")


class TeacherGenerator(UserGenerator):
    """
    Generator for creating realistic teacher data.
    """
    def __init__(self, schools: List[School]):
        """
        Initialize the TeacherGenerator.
        
        Args:
            schools (List[School]): List of schools to assign teachers to
        """
        super().__init__(schools)
        self.teachers: List[Teacher] = []
        
        # Common teacher titles
        self.titles = ["Dr.", "Prof.", "Mr.", "Mrs.", "Ms."]
          # Common departments
        self.departments = [
            "Mathematics", "Science", "Humanities", "Languages", 
            "Arts", "Physical Education", "Computer Science", 
            "Social Studies", "Special Education"
        ]
    
    def generate_teacher(self, school: School) -> Teacher:
        """
        Generate a single teacher for a specified school.
        
        Args:
            school (School): School to assign the teacher to
            
        Returns:
            Teacher: A newly generated Teacher instance
        """        # Generate a unique ID
        teacher_id = generate_user_id()
        
        # Generate Hebrew names
        first_name, last_name = generate_hebrew_name()
        name = format_hebrew_full_name(first_name, last_name)
        
        # Create work email (English to avoid Hebrew in emails)
        email = create_english_email_from_hebrew_name(first_name, last_name, school.name, "teacher")
        
        # Generate phone
        phone = self.faker.phone_number()
        
        # Select random title and department
        title = random.choice(self.titles)
        department = random.choice(self.departments)
        
        # Create the teacher
        teacher = Teacher(
            id=teacher_id,
            name=name,
            email=email,
            phone=phone,
            school_id=school.id,
            department=department,
            title=title
        )
        
        return teacher
    
    def generate_teachers(self, min_per_school: Optional[int] = None, max_per_school: Optional[int] = None) -> List[Teacher]:
        """
        Generate teachers for all schools.
        
        Args:
            min_per_school (Optional[int]): Minimum teachers per school, uses settings if None
            max_per_school (Optional[int]): Maximum teachers per school, uses settings if None
            
        Returns:
            List[Teacher]: List of all generated teachers
        """
        # Clear existing teachers
        self.teachers = []
        
        # Use settings if not specified
        if min_per_school is None:
            min_per_school = USER_SETTINGS.get('teachers_per_school', {}).get('min', 5)
        if max_per_school is None:
            max_per_school = USER_SETTINGS.get('teachers_per_school', {}).get('max', 20)
        
        # Generate teachers for each school
        for school in self.schools:
            # Determine how many teachers for this school
            num_teachers = random.randint(min_per_school, max_per_school)
            
            # Generate the teachers
            for _ in range(num_teachers):
                teacher = self.generate_teacher(school)
                self.teachers.append(teacher)
                
                # Update school's teacher list
                school.add_teacher(teacher.id)
        
        return self.teachers
    
    def get_teachers_for_school(self, school_id: str) -> List[Teacher]:
        """
        Get all teachers for a specific school.
        
        Args:
            school_id (str): ID of the school
            
        Returns:
            List[Teacher]: List of teachers for the school
        """
        return [t for t in self.teachers if t.school_id == school_id]
    
    def get_teacher_by_id(self, teacher_id: str) -> Optional[Teacher]:
        """
        Find a teacher by ID.
        
        Args:
            teacher_id (str): ID of the teacher to find
            
        Returns:
            Optional[Teacher]: The teacher if found, None otherwise
        """
        for teacher in self.teachers:
            if teacher.id == teacher_id:
                return teacher
        return None
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all teachers to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of teacher dictionaries
        """
        return [teacher.to_dict() for teacher in self.teachers]


class StudentGenerator(UserGenerator):
    """
    Generator for creating realistic student data.
    """
    def __init__(self, schools: List[School]):
        """
        Initialize the StudentGenerator.
        
        Args:
            schools (List[School]): List of schools to assign students to
        """
        super().__init__(schools)
        self.students: List[Student] = []
        
        # Load student performance profiles from settings
        self.performance_profiles = USER_SETTINGS.get('student_performance_profiles', [])
          # Subject correlation information from settings
        self.subject_correlation = USER_SETTINGS.get('subject_correlation', {})
    
    def generate_student(self, school: School) -> Student:
        """
        Generate a single student for a specified school.
        
        Args:
            school (School): School to assign the student to
            
        Returns:
            Student: A newly generated Student instance
        """        # Generate a unique ID
        student_id = generate_user_id()
        
        # Generate Hebrew names
        first_name, last_name = generate_hebrew_name()
        name = format_hebrew_full_name(first_name, last_name)
        
        # Create student email (English to avoid Hebrew in emails)
        email = create_english_email_from_hebrew_name(first_name, last_name, school.name, "student")
        
        # Generate phone
        phone = self.faker.phone_number()
        
        # Determine grade level (1-12) and entry year
        current_year = datetime.now().year
        grade_level = random.randint(9, 12)  # High school level
        entry_year = current_year - (grade_level - 7)  # Assuming 9th grade is first year
        
        # Create the student
        student = Student(
            id=student_id,
            name=name,
            email=email,
            phone=phone,
            school_id=school.id,
            grade_level=grade_level,
            entry_year=entry_year
        )
        
        # Assign a performance profile
        self._assign_performance_profile(student)
        
        return student
    
    def _assign_performance_profile(self, student: Student) -> None:
        """
        Assign a performance profile to a student for data generation.
        
        This creates a realistic profile of the student's academic abilities,
        with consistent performance across related subjects.
        
        Args:
            student (Student): The student to assign a profile to
        """
        # Select a profile based on distribution proportions
        profile_weights = [p.get('proportion', 0.25) for p in self.performance_profiles]
        selected_profile = random.choices(
            self.performance_profiles, 
            weights=profile_weights, 
            k=1
        )[0]
        
        # Get base performance with some random variation
        base_score = selected_profile.get('base_score', 75) or 70
        # variation = random.uniform(-5, 5)
        variation = 1
        student.base_performance = max(0, min(100, base_score + variation))
        
        # Generate subject strengths
        subject_strengths = {}
        
        # Start with a few random subject strengths
        primary_subjects = random.sample(list(self.subject_correlation.keys()), 
                                        k=min(2, len(self.subject_correlation)))
        
        for subject in primary_subjects:
            # Student is better or worse at this subject compared to their base performance
            subject_strengths[subject] = random.uniform(0.7, 1.3)
            
            # Now generate correlated performance for related subjects
            if subject in self.subject_correlation:
                for related_subject in self.subject_correlation[subject]:
                    if related_subject not in subject_strengths:
                        correlated_strength = generate_correlated_subject_performance(
                            subject_strengths[subject], 
                            0.80,  # Correlation strength
                            0.10   # Randomness
                        )
                        subject_strengths[related_subject] = correlated_strength
        
        # Update student's profile
        student.subject_strengths = subject_strengths
    
    def generate_students_for_course(self, course_id: str, school_id: str, count: int) -> List[Student]:
        """
        Generate students for a specific course.
        
        Args:
            course_id (str): ID of the course
            school_id (str): ID of the school
            count (int): Number of students to generate
            
        Returns:
            List[Student]: List of students assigned to the course
        """
        # Find all existing students for this school
        school_students = [s for s in self.students if s.school_id == school_id]
        
        # If we don't have enough existing students, generate more
        if len(school_students) < count:
            school = next((s for s in self.schools if s.id == school_id), None)
            if not school:
                raise ValueError(f"School with ID {school_id} not found")
                
            # Generate additional students
            additional_needed = count - len(school_students)
            for _ in range(additional_needed):
                student = self.generate_student(school)
                self.students.append(student)
                school_students.append(student)
                
                # Update school's student list
                school.add_student(student.id)
        
        # Select random students for this course
        selected_students = random.sample(school_students, count)
        
        # Enroll them in the course
        for student in selected_students:
            # print(f"Enrolling student {student.id} in course {course_id}")
            student.add_course(course_id)
            
        return selected_students
    
    def generate_students(self, students_per_school: Optional[int] = None) -> List[Student]:
        """
        Generate a pool of students for all schools.
        This doesn't assign them to courses yet.
        
        Args:
            students_per_school (Optional[int]): Number of students per school
                                               If None, uses school capacity
            
        Returns:
            List[Student]: List of all generated students
        """
        # Clear existing students
        self.students = []
        
        # Generate students for each school
        for school in self.schools:
            # Determine how many students for this school
            # if students_per_school is None:
            #     # Use a percentage of the school's capacity
            #     num_students = int(school.student_capacity * 0.8)  # 80% capacity
            # else:
            #     num_students = students_per_school
            num_students = 2000
            # Generate the students
            for _ in range(num_students):
                student = self.generate_student(school)
                self.students.append(student)
                
                # Update school's student list
                school.add_student(student.id)
        
        return self.students
    
    def get_students_for_school(self, school_id: str) -> List[Student]:
        """
        Get all students for a specific school.
        
        Args:
            school_id (str): ID of the school
            
        Returns:
            List[Student]: List of students for the school
        """
        return [s for s in self.students if s.school_id == school_id]
    
    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        """
        Find a student by ID.
        
        Args:
            student_id (str): ID of the student to find
            
        Returns:
            Optional[Student]: The student if found, None otherwise
        """
        for student in self.students:
            if student.id == student_id:
                return student
        return None
    
    def to_firestore_batch(self) -> List[Dict[str, Any]]:
        """
        Convert all students to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of student dictionaries
        """
        # Remove performance profile data that's only used for generation
        student_dicts = []
        for student in self.students:
            student_dict = student.to_dict()
            # Remove any generation-only fields if needed
            student_dicts.append(student_dict)
        
        return student_dicts