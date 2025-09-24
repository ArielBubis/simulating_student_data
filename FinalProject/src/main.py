import os
from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager

from config.settings import MID_SEMESTER_SETTINGS
# from firestore_admin_services import db, add_object_to_firestore

# new_object = {
#     "name": "Ariel Bubis",
#     "email": "ariel@example.com",
#     "age": 29
# }

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     try:
#         print("Starting lifespan context manager")
#         users_ref = db.collection("users")
#         docs = users_ref.where("email", "==", new_object["email"]).stream()
#         if not any(docs):
#             print("Adding new user to Firestore")
#             await add_object_to_firestore("users", new_object)
#         else:
#             print("User already exists in Firestore")
#         yield
#     except Exception as e:
#         print(f"Error during startup event: {e}")
#         yield
#     finally:
#         print("Lifespan context manager completed")

# app = FastAPI(lifespan=lifespan)

# if __name__ == "__main__":
#     print("Starting FastAPI application")
#     uvicorn.run("main:myApp", host="127.0.0.1", port=8000, reload=True)
#     print("FastAPI application has stopped")

"""
Main script for the educational data generation pipeline.
This script orchestrates the generation of all data entities and uploads to Firebase.
"""
import argparse
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import generators
from generators.id_generator import generate_unique_id, reset_used_ids, get_id_stats
from generators.school_generator import SchoolGenerator
from generators.user_generator import TeacherGenerator, StudentGenerator
from generators.course_generator import CourseGenerator
from generators.module_generator import ModuleGenerator
from generators.assignment_generator import AssignmentGenerator
from generators.performance_generator import PerformanceGenerator

# Import validation utilities
from utils.validation_utils import validate_data_consistency, log_validation_errors

# Import Firebase utilities
# from firebase.firestore import Firestore

log_file = os.path.join(os.path.expanduser("~"), "logs", "src/data_generation.log")

# Ensure the directory exists
log_dir = os.path.dirname(log_file)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='data_generation.log',
    filemode='w'
)

# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger(__name__)


class DataGenerator:
    """
    Main class for orchestrating the data generation pipeline.
    """
    def __init__(self, 
                 upload_to_firebase: bool = False, 
                 export_format: str = 'none', 
                 output_dir: str = './src/output',
                 is_mid_semester: bool = False,
                 cutoff_date: Optional[datetime] = None,
                 variation_days: Optional[int] = None):
        """
        Initialize the DataGenerator.
        
        Args:
            upload_to_firebase (bool): Whether to upload generated data to Firebase
            export_format (str): Format to export data ('json', 'csv', 'both', or 'none')
            output_dir (str): Directory to save exported data
            is_mid_semester (bool): Whether to generate mid-semester data
            cutoff_date (Optional[datetime]): Custom mid-semester cutoff date
            variation_days (Optional[int]): Custom variation window in days
        """
        self.upload_to_firebase = upload_to_firebase
        self.firestore = Firestore() if upload_to_firebase else None
        self.export_format = export_format
        self.output_dir = output_dir
        
        # Mid-semester parameters
        self.is_mid_semester = is_mid_semester
        
        # Use provided cutoff date or default from settings
        if is_mid_semester:
            self.cutoff_date = cutoff_date or MID_SEMESTER_SETTINGS["target_date"]
            self.variation_days = variation_days or MID_SEMESTER_SETTINGS["variation_days"]
            logger.info(f"Generating mid-semester data with target date: {self.cutoff_date}")
        else:
            self.cutoff_date = None
            self.variation_days = None
        
        # Initialize generators
        self.school_generator = None
        self.teacher_generator = None
        self.student_generator = None
        self.course_generator = None
        self.module_generator = None
        self.assignment_generator = None
        self.performance_generator = None
        
        # Track generated data
        self.schools = []
        self.teachers = []
        self.students = []
        self.courses = []
        self.modules = []
        self.assignments = []
        self.student_assignments = []
        self.student_courses = []
        
        # Statistics
        self.generation_stats = {}
        self.start_time = None
        self.end_time = None
        
    def _export_data(self) -> None:
        """Export generated data to local files in specified format."""
        # Create export directory with semester state in the name
        semester_state = "mid_semester" if self.is_mid_semester else "full_semester"
        output_dir = f"{self.output_dir}/{semester_state}"
        
        # If mid-semester, add the cutoff date to the directory name
        if self.is_mid_semester and self.cutoff_date:
            date_str = self.cutoff_date.strftime("%Y%m%d")
            output_dir = f"{output_dir}_{date_str}"
        
        logger.info(f"Exporting data in {self.export_format} format to {output_dir}...")
          # Prepare comprehensive student assignments data
        all_student_assignments = list(self.student_assignments)  # Start with completed assignments
        
        # Add mid-semester specific data and combine all assignment statuses
        if self.is_mid_semester:
            # Add pending assignments data (assignments available but not submitted)
            pending_assignments = []
            future_assignments = []
            
            # Generate records for all non-submitted assignments
            for student in self.students:
                student_effective_date = self.performance_generator._get_student_effective_date(student)                
                for assignment in self.assignments:
                    # Check if this student-assignment pair exists in completed submissions
                    is_completed = any(
                        sa['studentId'] == student.id and sa['assignmentId'] == assignment.id
                        for sa in self.student_assignments
                    )
                    
                    if not is_completed:
                        # Determine if assignment is available to this student
                        if assignment.assign_date <= student_effective_date:
                            # Assignment is available but not completed
                            pending_assignment = {
                                "id": generate_unique_id("pa_"),
                                "studentId": student.id,
                                "assignmentId": assignment.id,
                                "courseId": assignment.course_id,
                                "moduleId": assignment.module_id,
                                "status": "pending",
                                "isAvailable": True,
                                "createdAt": datetime.now(),
                                "updatedAt": datetime.now()
                            }
                            pending_assignments.append(pending_assignment)
                            all_student_assignments.append(pending_assignment)  # Add to main collection
                        else:
                            # Assignment is not yet available
                            future_assignment = {
                                "id": generate_unique_id("fa_"),
                                "studentId": student.id,
                                "assignmentId": assignment.id,
                                "courseId": assignment.course_id,
                                "moduleId": assignment.module_id,
                                "status": "future",
                                "isAvailable": False,
                                "createdAt": datetime.now(),
                                "updatedAt": datetime.now()
                            }
                            future_assignments.append(future_assignment)
                            all_student_assignments.append(future_assignment)  # Add to main collection
          # Debug: Print the size of all_student_assignments
        logger.info(f"DEBUG: all_student_assignments contains {len(all_student_assignments)} records")
        if len(all_student_assignments) > 0:
            logger.info(f"DEBUG: First record: {all_student_assignments[0]}")
        
        # Prepare data for export
        data_objects = {
            'schools': [s.to_dict() for s in self.schools],
            'teachers': [t.to_dict() for t in self.teachers],
            'students': [s.to_dict() for s in self.students],
            'courses': [c.to_dict() for c in self.courses],
            'modules': [m.to_dict() for m in self.modules],
            'assignments': [a.to_dict() for a in self.assignments],
            'studentAssignments': all_student_assignments,  # Now includes all assignment statuses
            'studentCourses': self.student_courses
        }
        
        # Add mid-semester specific data as separate collections for backward compatibility
        if self.is_mid_semester:
            # Add these as separate collections for specific analysis if needed
            data_objects['pendingAssignments'] = pending_assignments
            data_objects['futureAssignments'] = future_assignments
            
            # Include mid-semester progress report
            if hasattr(self.performance_generator, 'generate_mid_semester_progress_report'):
                progress_report = self.performance_generator.generate_mid_semester_progress_report()
                data_objects['midSemesterReport'] = [progress_report]
        
        # Add metadata about the generation
        metadata = {
            "generatedAt": datetime.now().isoformat(),
            "isMidSemester": self.is_mid_semester,
        }
        
        if self.is_mid_semester and self.cutoff_date:
            metadata['cutoffDate'] = self.cutoff_date.isoformat()
            metadata['variationDays'] = self.variation_days
        
        data_objects['metadata'] = [metadata]
        
        # Determine export formats
        formats = []
        if self.export_format == 'json':
            formats = ['json']
        elif self.export_format == 'csv':
            formats = ['csv']
        elif self.export_format == 'both':
            formats = ['json', 'csv']
        
        # Export the data
        results = export_all_collections(data_objects, formats, output_dir)
        
        # Log results
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"Successfully exported {success_count}/{len(results)} collections")
        
        # Log any failures
        failures = [name for name, success in results.items() if not success]
        if failures:
            logger.warning(f"Failed to export these collections: {', '.join(failures)}")
        
        logger.info("Data export completed")

    def generate_all_data(self) -> bool:
        """
        Execute the complete data generation pipeline.
        
        Returns:
            bool: True if generation was successful, False otherwise
        """
        logger.info("Starting data generation pipeline")
        self.start_time = time.time()
        
        try:
            # Reset ID generators
            reset_used_ids()
            
            # Generate data in the correct order
            self._generate_schools()
            self._generate_teachers()
            self._generate_courses()
            self._generate_students_for_courses()
            self._generate_modules()
            self._generate_assignments()
            self._generate_performance_data()
            
            # Validate generated data
            self._validate_data()
            
            # Upload to Firebase if enabled
            if self.upload_to_firebase:
                self._upload_to_firebase()
            
            # Export to local files if enabled
            if self.export_format != 'none':
                self._export_data()
                
                # If in mid-semester mode, export additional specialized files
                if self.is_mid_semester and hasattr(self.performance_generator, 'export_assignment_status_data'):
                    # Create specialized export directory
                    special_export_dir = f"{self.output_dir}/mid_semester_analysis"
                    if self.cutoff_date:
                        date_str = self.cutoff_date.strftime("%Y%m%d")
                        special_export_dir = f"{special_export_dir}_{date_str}"
                    
                    # Export specialized data
                    self.performance_generator.export_assignment_status_data(
                        f"{special_export_dir}/status"
                    )
                    self.performance_generator.export_mid_semester_summary(
                        f"{special_export_dir}/summary"
                    )
            
            # Calculate statistics
            self._calculate_stats()
            
            self.end_time = time.time()
            logger.info(f"Data generation completed in {round(self.end_time - self.start_time, 2)} seconds")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in data generation: {str(e)}", exc_info=True)
            return False    
    def _generate_schools(self) -> None:
        """Generate school data."""
        logger.info("Generating schools...")
        self.school_generator = SchoolGenerator()
        self.schools = self.school_generator.generate_schools()
        logger.info(f"Generated {len(self.schools)} schools")
    
    def _generate_teachers(self) -> None:
        """Generate teacher data."""
        logger.info("Generating teachers...")
        self.teacher_generator = TeacherGenerator(self.schools)
        self.teachers = self.teacher_generator.generate_teachers()
        logger.info(f"Generated {len(self.teachers)} teachers")
    
    def _generate_students(self) -> None:
        """Generate a pool of students (not yet enrolled in courses)."""
        logger.info("Generating student pool...")
        self.student_generator = StudentGenerator(self.schools)
        self.students = self.student_generator.generate_students()
        logger.info(f"Generated {len(self.students)} students")
    
    def _generate_courses(self) -> None:
        """Generate courses and assign teachers."""
        logger.info("Generating courses...")
        self.course_generator = CourseGenerator(self.schools, self.teachers)
        self.courses = self.course_generator.generate_courses()
        logger.info(f"Generated {len(self.courses)} courses")
    def _generate_students_for_courses(self) -> None:
        """Generate students based on course enrollment needs."""
        logger.info("Generating students based on course enrollment...")
        
        # Initialize student generator
        self.student_generator = StudentGenerator(self.schools)
        
        # Keep track of all generated students
        all_students = []
        
        # For each course, generate the appropriate number of students
        for course in self.courses:
            # Get the school for this course
            school_id = course.school_id
            
            # Determine number of students (12-30 per course as specified in USER_SETTINGS)
            num_students = random.randint(
                12,
                30
            )
            
            # Generate students specifically for this course
            course_students = self.student_generator.generate_students_for_course(
                course.id, school_id, num_students
            )
            
            # Add these students to our course
            for student in course_students:
                course.add_student(student.id)
            
            # Add these students to our overall list
            all_students.extend(course_students)
            
            logger.debug(f"Generated {len(course_students)} students for course {course.id}")
        
        # Remove any duplicate students (in case the same student was generated for multiple courses)
        self.students = list({student.id: student for student in all_students}.values())
        
        logger.info(f"Generated a total of {len(self.students)} unique students across all courses")

    def _generate_modules(self) -> None:
        """Generate modules within courses."""
        logger.info("Generating modules...")
        self.module_generator = ModuleGenerator(self.courses)
        self.modules = self.module_generator.generate_all_modules()
        logger.info(f"Generated {len(self.modules)} modules")
    
    def _generate_assignments(self) -> None:
        """Generate assignments within modules."""
        logger.info("Generating assignments...")
        self.assignment_generator = AssignmentGenerator(self.modules)
        self.assignments = self.assignment_generator.generate_all_assignments()
        logger.info(f"Generated {len(self.assignments)} assignments")
    
    def _generate_performance_data(self) -> None:
        """Generate student enrollment and performance data."""
        logger.info("Enrolling students in courses...")
        
        # Enroll students in courses (12-30 per course)
        for course in self.courses:
            # Get the school for this course
            school_id = course.school_id
            
            # Determine number of students (12-30)
            num_students = random.randint(12, 30)
            
            # Enroll students
            enrolled_students = self.student_generator.generate_students_for_course(
                course.id, school_id, num_students
            )
            for student in enrolled_students:
                course.add_student(student.id)
            logger.debug(f"Enrolled {len(enrolled_students)} students in course {course.id}")
        
        logger.info("Generating student performance data...")
        self.performance_generator = PerformanceGenerator(
            self.students, 
            self.courses, 
            self.modules, 
            self.assignments,
            is_mid_semester=self.is_mid_semester,
            cutoff_date=self.cutoff_date,
            variation_days=self.variation_days
        )
        
        self.student_assignments, self.student_courses = self.performance_generator.generate_all_performance_data()
        
        logger.info(f"Generated {len(self.student_assignments)} assignment submissions")
        logger.info(f"Generated {len(self.student_courses)} course performance records")
    
    def _validate_data(self) -> None:
        """Validate the generated data for consistency and realism."""
        logger.info("Validating generated data...")
        
        # Prepare data for validation
        data_objects = {
            'schools': [s.to_dict() for s in self.schools],
            'teachers': [t.to_dict() for t in self.teachers],
            'students': [s.to_dict() for s in self.students],
            'courses': [c.to_dict() for c in self.courses],
            'modules': [m.to_dict() for m in self.modules],
            'assignments': [a.to_dict() for a in self.assignments],
            'studentAssignments': self.student_assignments,
            'studentCourses': self.student_courses
        }
        
        # Add mid-semester flag for validation
        validation_context = {
            'is_mid_semester': self.is_mid_semester,
            'cutoff_date': self.cutoff_date
        }
        
        # Run validation with mid-semester context
        validation_errors = validate_data_consistency(data_objects, validation_context)
        
        if validation_errors:
            logger.warning("Validation found issues with the generated data")
            log_validation_errors(validation_errors)
        else:
            logger.info("Data validation successful")
    
    def _upload_to_firebase(self) -> None:
        """Upload all generated data to Firebase."""
        if not self.firestore:
            logger.error("Firebase client not initialized")
            return
        
        logger.info("Uploading data to Firebase...")
        
        # Upload each data type in batches
        self._upload_collection('schools', [s.to_dict() for s in self.schools])
        self._upload_collection('teachers', [t.to_dict() for t in self.teachers])
        self._upload_collection('students', [s.to_dict() for s in self.students])
        self._upload_collection('courses', [c.to_dict() for c in self.courses])
        self._upload_collection('modules', [m.to_dict() for m in self.modules])
        self._upload_collection('assignments', [a.to_dict() for a in self.assignments])
        self._upload_collection('studentAssignments', self.student_assignments)
        self._upload_collection('studentCourses', self.student_courses)
        
        logger.info("Firebase upload completed")
    
    def _upload_collection(self, collection_name: str, documents: List[Dict[str, Any]]) -> None:
        """
        Upload a collection of documents to Firebase.
        
        Args:
            collection_name (str): Name of the collection
            documents (List[Dict[str, Any]]): List of documents to upload
        """
        if not documents:
            logger.warning(f"No documents to upload for collection {collection_name}")
            return
        
        logger.info(f"Uploading {len(documents)} documents to {collection_name}...")
        
        try:
            self.firestore.batch_write(collection_name, documents)
            logger.info(f"Successfully uploaded {len(documents)} documents to {collection_name}")
        except Exception as e:
            logger.error(f"Error uploading to {collection_name}: {str(e)}")
    
    def _calculate_stats(self) -> None:
        """Calculate and store statistics about the generated data."""
        self.generation_stats = {
            'schools': len(self.schools),
            'teachers': len(self.teachers),
            'students': len(self.students),
            'courses': len(self.courses),
            'modules': len(self.modules),
            'assignments': len(self.assignments),
            'studentAssignments': len(self.student_assignments),
            'studentCourses': len(self.student_courses),
            'id_stats': get_id_stats(),
        }
        
        logger.info("Generation statistics:")
        for key, value in self.generation_stats.items():
            if key != 'id_stats':
                logger.info(f"  {key}: {value}")
    
    def print_summary(self) -> None:
        """Print a summary of the generated data."""
        if not self.generation_stats:
            logger.warning("No statistics available. Run generate_all_data() first.")
            return
        
        print("\n========== DATA GENERATION SUMMARY ==========")
        print(f"Generation completed in {round(self.end_time - self.start_time, 2)} seconds")
        
        # Print mid-semester information if applicable
        if self.is_mid_semester:
            print(f"\nMID-SEMESTER DATA GENERATION")
            print(f"Target date: {self.cutoff_date}")
            print(f"Variation window: ±{self.variation_days} days")
        
        print("\nEntities generated:")
        
        for key, value in self.generation_stats.items():
            if key != 'id_stats':
                print(f"  {key}: {value}")
        
        print("\nIDs generated:")
        for key, value in self.generation_stats.get('id_stats', {}).items():
            print(f"  {key}: {value}")
        
        # If mid-semester, add completion statistics
        if self.is_mid_semester and 'completion_stats' in self.generation_stats:
            print("\nMid-semester completion statistics:")
            for key, value in self.generation_stats.get('completion_stats', {}).items():
                print(f"  {key}: {value}")
        
        print("\nExample data paths:")
        print(f"  School: {self.schools[0].id if self.schools else 'None'}")
        print(f"  Teacher: {self.teachers[0].id if self.teachers else 'None'}")
        print(f"  Student: {self.students[0].id if self.students else 'None'}")
        print(f"  Course: {self.courses[0].id if self.courses else 'None'}")
        
        if self.upload_to_firebase:
            print("\nData was uploaded to Firebase")
        else:
            print("\nData was NOT uploaded to Firebase")
        
        print("==============================================\n")


def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate educational data')
    
    parser.add_argument(
        '--upload',
        action='store_true',
        help='Upload generated data to Firebase'
    )
    
    parser.add_argument(
        '--export',
        choices=['json', 'csv', 'both', 'none'],
        default='none',
        help='Export generated data to local files (json, csv, both, or none)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./src/output',
        help='Directory to save exported data (default: ./src/output)'
    )

    # mid-semester related arguments
    parser.add_argument(
        '--mid-semester',
        action='store_true',
        help='Generate mid-semester data instead of end-of-semester data'
    )
    
    parser.add_argument(
        '--cutoff-date',
        type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
        help='Specify custom mid-semester cutoff date (format: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--variation-days',
        type=int,
        help='Variation window in days around cutoff date (default from settings)'
    )
    return parser.parse_args()

# Update the imports at the top of main.py to include:
from utils.export_utils import export_all_collections




if __name__ == "__main__":
    import random
    
    args = parse_arguments()
    
    generator = DataGenerator(
        upload_to_firebase=args.upload,
        export_format=args.export,
        output_dir=args.output_dir,
        is_mid_semester=args.mid_semester,
        cutoff_date=args.cutoff_date,
        variation_days=args.variation_days
    )
    success = generator.generate_all_data()
    
    if success:
        generator.print_summary()
    else:
        print("Data generation failed. Check logs for details.")