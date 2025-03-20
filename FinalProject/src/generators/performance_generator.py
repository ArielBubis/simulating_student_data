"""
Performance Generator for creating realistic student performance data.
This module provides functionality for generating assignment submissions,
assessment scores, and time tracking metrics.
"""
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta

from config.settings import ASSIGNMENT_SETTINGS, TIME_TRACKING
from models.student import Student
from models.course import Course
from models.module import Module
from models.assignment import Assignment
from generators.id_generator import generate_unique_id
from utils.date_utils import generate_submission_date
from utils.distribution_utils import (
    generate_consistent_student_performance,
    generate_realistic_time_spent,
    calculate_weighted_score
)


class PerformanceGenerator:
    """
    Generator for creating realistic student performance data.
    """
    def __init__(
        self,
        students: List[Student],
        courses: List[Course],
        modules: List[Module],
        assignments: List[Assignment]
    ):
        """
        Initialize the PerformanceGenerator.
        
        Args:
            students (List[Student]): List of students
            courses (List[Course]): List of courses
            modules (List[Module]): List of modules
            assignments (List[Assignment]): List of assignments
        """
        self.students = students
        self.courses = courses
        self.modules = modules
        self.assignments = assignments
        
        # Track generated data
        self.student_assignments: List[Dict[str, Any]] = []
        self.student_courses: List[Dict[str, Any]] = []
        
        # Load settings
        self.late_submission_probability = ASSIGNMENT_SETTINGS.get('late_submission_probability', 0.15)
        self.max_days_late = ASSIGNMENT_SETTINGS.get('max_days_late', 5)
        self.time_per_assignment_minutes = TIME_TRACKING.get('time_per_assignment_minutes', {})
        self.time_variability = TIME_TRACKING.get('time_variability', 0.3)
    
    def _get_assignment_type_info(self, assignment_type: str) -> Dict[str, Any]:
        """
        Get configuration information for a specific assignment type.
        
        Args:
            assignment_type (str): Name of the assignment type
            
        Returns:
            Dict[str, Any]: Assignment type configuration
        """
        assignment_types = ASSIGNMENT_SETTINGS.get('assignment_types', [])
        
        for type_info in assignment_types:
            if type_info.get("name") == assignment_type:
                return type_info
        
        # Default if not found
        return {
            "name": assignment_type,
            "weight": 1.0,
            "mean_score": 75,
            "std_dev": 10,
            "skewness": -0.5
        }
    
    def _get_modules_for_course(self, course_id: str) -> List[Module]:
        """
        Get all modules for a specific course.
        
        Args:
            course_id (str): ID of the course
            
        Returns:
            List[Module]: List of modules for the course
        """
        return [m for m in self.modules if m.course_id == course_id]
    
    def _get_assignments_for_module(self, module_id: str) -> List[Assignment]:
        """
        Get all assignments for a specific module.
        
        Args:
            module_id (str): ID of the module
            
        Returns:
            List[Assignment]: List of assignments for the module
        """
        return [a for a in self.assignments if a.module_id == module_id]
    
    def _get_assignments_for_course(self, course_id: str) -> List[Assignment]:
        """
        Get all assignments for a specific course.
        
        Args:
            course_id (str): ID of the course
            
        Returns:
            List[Assignment]: List of assignments for the course
        """
        # Get modules for this course
        course_modules = self._get_modules_for_course(course_id)
        module_ids = [m.id for m in course_modules]
        
        # Get assignments for these modules
        return [a for a in self.assignments if a.module_id in module_ids]
    
    def _get_time_range_for_assignment_type(self, assignment_type: str) -> Tuple[int, int]:
        """
        Get the expected time range for a specific assignment type.
        
        Args:
            assignment_type (str): Type of assignment
            
        Returns:
            Tuple[int, int]: Minimum and maximum time in minutes
        """
        default_range = (30, 120)  # Default: 30 min to 2 hours
        
        if not self.time_per_assignment_minutes:
            return default_range
        
        type_range = self.time_per_assignment_minutes.get(assignment_type)
        if not type_range:
            return default_range
        
        return (type_range.get('min', 30), type_range.get('max', 120))
    
    def generate_student_assignment_data(
        self, 
        student: Student, 
        assignment: Assignment
    ) -> Dict[str, Any]:
        """
        Generate assignment submission data for a specific student and assignment.
        
        Args:
            student (Student): The student
            assignment (Assignment): The assignment
            
        Returns:
            Dict[str, Any]: Generated student-assignment data
        """
        # Determine if this will be a late submission
        is_late = random.random() < self.late_submission_probability
        
        # Generate submission date
        submission_date = generate_submission_date(
            assignment.assign_date,
            assignment.due_date,
            is_late,
            self.max_days_late
        )
        
        # Get assignment type info for score distribution
        assignment_type = assignment.assignment_type or "Assignment"
        type_info = self._get_assignment_type_info(assignment_type)
        
        # Determine student's score based on their performance profile
        # and the assignment characteristics
        mean_score = type_info.get('mean_score', 75)
        std_dev = type_info.get('std_dev', 10)
        skewness = type_info.get('skewness', -0.5)
        
        # Find subject area from module
        subject_area = None
        for module in self.modules:
            if module.id == assignment.module_id:
                subject_area = module.subject
                break
        
        # Apply student's subject strength if applicable
        subject_modifier = 1.0
        if subject_area and subject_area in student.subject_strengths:
            subject_modifier = student.subject_strengths[subject_area]
        
        # Calculate base score from student's performance profile
        base_score = student.base_performance * subject_modifier
        
        # Apply late penalty if applicable (reduce score by 5-15%)
        late_penalty = random.uniform(0.05, 0.15) if is_late else 0
        
        # Generate a score with some randomness
        score_multiplier = random.uniform(0.85, 1.15) * (1 - late_penalty)
        assessment_score = min(100, max(0, base_score * score_multiplier))
        
        # Generate time spent on the assignment
        min_time, max_time = self._get_time_range_for_assignment_type(assignment_type)
        time_spent = generate_realistic_time_spent(
            (min_time + max_time) / 2,  # Average time
            student.base_performance / 100,  # Higher performing students are more efficient
            self.time_variability
        )
        
        # Create student-assignment record
        student_assignment = {
            "id": generate_unique_id("sa_"),
            "studentId": student.id,
            "assignmentId": assignment.id,
            "submissionDate": submission_date,
            "assessmentScore": round(assessment_score, 1),
            "timeSpentMinutes": time_spent,
            "isLate": is_late,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        return student_assignment
    
    def generate_course_performance_data(self, student: Student, course: Course) -> Dict[str, Any]:
        """
        Generate overall course performance data for a specific student and course.
        
        Args:
            student (Student): The student
            course (Course): The course
            
        Returns:
            Dict[str, Any]: Generated student-course data
        """
        # Get assignments for this course
        course_assignments = self._get_assignments_for_course(course.id)
        
        # Find student's submissions for these assignments
        student_submissions = [
            sa for sa in self.student_assignments 
            if sa['studentId'] == student.id and 
            sa['assignmentId'] in [a.id for a in course_assignments]
        ]
        
        if not student_submissions:
            # No submissions, create basic record with zero score
            return {
                "id": generate_unique_id("sc_"),
                "studentId": student.id,
                "courseId": course.id,
                "finalScore": 0.0,
                "totalTimeSpentMinutes": 0,
                "createdAt": datetime.now(),
                "updatedAt": datetime.now()
            }
        
        # Calculate scores and weights
        assignment_scores = []
        assignment_weights = []
        total_time_spent = 0
        
        for submission in student_submissions:
            # Find the assignment
            assignment = next(
                (a for a in course_assignments if a.id == submission['assignmentId']), 
                None
            )
            
            if assignment:
                assignment_scores.append(submission['assessmentScore'])
                assignment_weights.append(assignment.weight)
                total_time_spent += submission.get('timeSpentMinutes', 0)
        
        # Calculate final score
        if assignment_scores:
            final_score = calculate_weighted_score(assignment_scores, assignment_weights)
        else:
            final_score = 0.0
        
        # Create student-course record
        student_course = {
            "id": generate_unique_id("sc_"),
            "studentId": student.id,
            "courseId": course.id,
            "finalScore": round(final_score, 1),
            "totalTimeSpentMinutes": total_time_spent,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        return student_course
    
    def generate_all_performance_data(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generate performance data for all students enrolled in courses.
        
        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]: Student-assignment and student-course data
        """
        # Clear existing data
        self.student_assignments = []
        self.student_courses = []
        
        # Set to track which student-course pairs we've processed
        processed_student_courses: Set[Tuple[str, str]] = set()
        
        # Process each student
        for student in self.students:
            # For each course the student is enrolled in
            for course_id in student.courses:
                # Track that we've processed this student-course pair
                processed_student_courses.add((student.id, course_id))
                
                # Get all assignments for this course
                course_assignments = self._get_assignments_for_course(course_id)
                
                # Generate student-assignment data for each assignment
                for assignment in course_assignments:
                    student_assignment = self.generate_student_assignment_data(
                        student, assignment
                    )
                    self.student_assignments.append(student_assignment)
                    
                    # Add submission to assignment for tracking
                    assignment.add_student_submission(
                        student.id,
                        student_assignment['submissionDate'],
                        student_assignment['assessmentScore'],
                        student_assignment['timeSpentMinutes']
                    )
                
                # Find the course
                course = next((c for c in self.courses if c.id == course_id), None)
                if course:
                    # Generate overall course performance data
                    student_course = self.generate_course_performance_data(
                        student, course
                    )
                    self.student_courses.append(student_course)
                    
                    # Update student's total score
                    # For simplicity, just average all course scores
                    student_courses = [
                        sc for sc in self.student_courses 
                        if sc['studentId'] == student.id
                    ]
                    if student_courses:
                        total_score = sum(sc['finalScore'] for sc in student_courses) / len(student_courses)
                        student.update_total_score(round(total_score, 1))
        
        return self.student_assignments, self.student_courses
    
    def get_student_performance_summary(self, student_id: str) -> Dict[str, Any]:
        """
        Get a summary of a student's performance across all courses.
        
        Args:
            student_id (str): ID of the student
            
        Returns:
            Dict[str, Any]: Performance summary
        """
        # Find student
        student = next((s for s in self.students if s.id == student_id), None)
        if not student:
            return {"error": f"Student with ID {student_id} not found"}
        
        # Get student's course records
        student_courses = [
            sc for sc in self.student_courses 
            if sc['studentId'] == student_id
        ]
        
        # Get student's assignment records
        student_assignments = [
            sa for sa in self.student_assignments 
            if sa['studentId'] == student_id
        ]
        
        # Calculate metrics
        total_assignments = len(student_assignments)
        completed_assignments = sum(1 for sa in student_assignments if sa['submissionDate'])
        total_time_spent = sum(sa.get('timeSpentMinutes', 0) for sa in student_assignments)
        average_score = (
            sum(sa['assessmentScore'] for sa in student_assignments) / total_assignments
            if total_assignments > 0 else 0
        )
        
        # Count late submissions
        late_submissions = sum(1 for sa in student_assignments if sa.get('isLate', False))
        late_submission_rate = (
            late_submissions / completed_assignments * 100
            if completed_assignments > 0 else 0
        )
        
        # Build summary
        summary = {
            "studentId": student_id,
            "studentName": student.name,
            "totalScore": student.total_score,
            "coursesEnrolled": len(student.courses),
            "coursesCompleted": sum(1 for sc in student_courses if sc['finalScore'] > 0),
            "totalAssignments": total_assignments,
            "completedAssignments": completed_assignments,
            "completionRate": (
                completed_assignments / total_assignments * 100
                if total_assignments > 0 else 0
            ),
            "averageScore": round(average_score, 1),
            "totalTimeSpentMinutes": total_time_spent,
            "lateSubmissionRate": round(late_submission_rate, 1)
        }
        
        # Add course breakdown
        course_breakdown = []
        for course_id in student.courses:
            course = next((c for c in self.courses if c.id == course_id), None)
            if course:
                course_record = next(
                    (sc for sc in student_courses if sc['courseId'] == course_id),
                    None
                )
                
                if course_record:
                    course_breakdown.append({
                        "courseId": course_id,
                        "courseName": course.name,
                        "finalScore": course_record['finalScore'],
                        "timeSpentMinutes": course_record['totalTimeSpentMinutes']
                    })
        
        summary["courseBreakdown"] = course_breakdown
        
        return summary
    
    def get_course_performance_summary(self, course_id: str) -> Dict[str, Any]:
        """
        Get a summary of student performance in a specific course.
        
        Args:
            course_id (str): ID of the course
            
        Returns:
            Dict[str, Any]: Performance summary
        """
        # Find course
        course = next((c for c in self.courses if c.id == course_id), None)
        if not course:
            return {"error": f"Course with ID {course_id} not found"}
        
        # Get course's student records
        course_students = [
            sc for sc in self.student_courses 
            if sc['courseId'] == course_id
        ]
        
        # Get course's assignments
        course_assignments = self._get_assignments_for_course(course_id)
        
        # Calculate metrics
        enrolled_students = len(course.students)
        completed_students = sum(1 for cs in course_students if cs['finalScore'] > 0)
        
        # Calculate average score
        if course_students:
            average_score = sum(cs['finalScore'] for cs in course_students) / len(course_students)
        else:
            average_score = 0
        
        # Build summary
        summary = {
            "courseId": course_id,
            "courseName": course.name,
            "enrolledStudents": enrolled_students,
            "completedStudents": completed_students,
            "completionRate": (
                completed_students / enrolled_students * 100
                if enrolled_students > 0 else 0
            ),
            "averageScore": round(average_score, 1),
            "totalAssignments": len(course_assignments)
        }
        
        # Add student breakdown
        student_breakdown = []
        for student_id in course.students:
            student = next((s for s in self.students if s.id == student_id), None)
            if student:
                student_record = next(
                    (sc for sc in course_students if sc['studentId'] == student_id),
                    None
                )
                
                if student_record:
                    student_breakdown.append({
                        "studentId": student_id,
                        "studentName": student.name,
                        "finalScore": student_record['finalScore'],
                        "timeSpentMinutes": student_record['totalTimeSpentMinutes']
                    })
        
        summary["studentBreakdown"] = student_breakdown
        
        # Add assignment breakdown
        assignment_breakdown = []
        for assignment in course_assignments:
            # Find all submissions for this assignment
            submissions = [
                sa for sa in self.student_assignments 
                if sa['assignmentId'] == assignment.id
            ]
            
            if submissions:
                average_assignment_score = (
                    sum(sa['assessmentScore'] for sa in submissions) / len(submissions)
                )
                
                assignment_breakdown.append({
                    "assignmentId": assignment.id,
                    "assignmentName": assignment.name,
                    "assignmentType": assignment.assignment_type,
                    "averageScore": round(average_assignment_score, 1),
                    "submissionCount": len(submissions),
                    "submissionRate": (
                        len(submissions) / len(course.students) * 100
                        if course.students else 0
                    )
                })
        
        summary["assignmentBreakdown"] = assignment_breakdown
        
        return summary
    
    def student_assignments_to_firestore(self) -> List[Dict[str, Any]]:
        """
        Convert student-assignment data to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries for Firestore
        """
        return self.student_assignments
    
    def student_courses_to_firestore(self) -> List[Dict[str, Any]]:
        """
        Convert student-course data to a format suitable for Firestore batch insertion.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries for Firestore
        """
        return self.student_courses