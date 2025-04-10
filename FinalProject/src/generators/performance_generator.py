"""
Performance Generator for creating realistic student performance data.
This module provides functionality for generating assignment submissions,
assessment scores, and time tracking metrics.
"""
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from datetime import datetime, timedelta

from config.settings import ACADEMIC_YEAR, ASSIGNMENT_SETTINGS, MID_SEMESTER_SETTINGS, TIME_TRACKING
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
        assignments: List[Assignment],
        is_mid_semester: bool = False,
        cutoff_date: Optional[datetime] = None,
        variation_days: Optional[int] = None
    ):
        """
        Initialize the PerformanceGenerator.
        
        Args:
            students (List[Student]): List of students
            courses (List[Course]): List of courses
            modules (List[Module]): List of modules
            assignments (List[Assignment]): List of assignments
            is_mid_semester (bool): Whether to generate mid-semester data
            cutoff_date (Optional[datetime]): The reference date for mid-semester data
            variation_days (Optional[int]): Days of variation around cutoff date
        """
        self.students = students
        self.courses = courses
        self.modules = modules
        self.assignments = assignments
        
        # Mid-semester parameters
        self.is_mid_semester = is_mid_semester
        self.cutoff_date = cutoff_date
        self.variation_days = variation_days
        
        # Track generated data
        self.student_assignments: List[Dict[str, Any]] = []
        self.student_courses: List[Dict[str, Any]] = []
        
        # Load settings
        self.late_submission_probability = ASSIGNMENT_SETTINGS.get('late_submission_probability', 0.15)
        self.max_days_late = ASSIGNMENT_SETTINGS.get('max_days_late', 5)
        self.time_per_assignment_minutes = TIME_TRACKING.get('time_per_assignment_minutes', {})
        self.time_variability = TIME_TRACKING.get('time_variability', 0.3)
        
        # Load mid-semester specific settings if needed
        if is_mid_semester:
            if cutoff_date is None:
                self.cutoff_date = MID_SEMESTER_SETTINGS.get('target_date', datetime.now())
            if variation_days is None:
                self.variation_days = MID_SEMESTER_SETTINGS.get('variation_days', 14)
    
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
    def _is_assignment_available(self, assignment: Assignment, student: Student) -> bool:
        """
        Determine if an assignment would be available to a student at the mid-semester point.
        
        Args:
            assignment (Assignment): The assignment to check
            student (Student): The student to check for
            
        Returns:
            bool: True if the assignment is available to this student, False otherwise
        """
        if not self.is_mid_semester or self.cutoff_date is None:
            return True  # All assignments available in full-semester mode
        
        # Get student's effective cutoff date (varies based on performance)
        student_effective_date = self._get_student_effective_date(student)
        
        # Check if assignment is available based on assign date
        # An assignment is available if its assign_date is before the student's effective cutoff date
        return assignment.assign_date <= student_effective_date
    
    def _get_student_effective_date(self, student: Student) -> datetime:
        """
        Calculate a student-specific effective date for mid-semester progress.
        
        High-performing students will have an effective date further in the future
        (they're ahead), while struggling students will have an effective date
        in the past (they're behind).
        
        Args:
            student (Student): The student to calculate for
            
        Returns:
            datetime: The effective cutoff date for this student
        """
        if not self.is_mid_semester or self.cutoff_date is None:
            return datetime.now()  # Default if not in mid-semester mode
        
        # Get the student's performance profile
        profile = self._get_student_profile(student)
        
        # Get the profile's progress modifier
        profile_mod = MID_SEMESTER_SETTINGS.get('profile_progress_modifiers', {}).get(profile, 0)
        
        # Apply a personalized factor based on the student's exact performance
        # This adds variation even within the same profile category
        performance_factor = (student.base_performance - 75) / 25  # Normalize around 75
        
        # Combine the profile modifier with the personalized factor
        combined_factor = profile_mod + (performance_factor * 0.5)  # Scale the personal factor
        
        # Calculate days offset with some randomness
        # Higher-performing students tend to be more consistent, lower variance
        if profile in ["High Achiever", "Above Average"]:
            variance = self.variation_days / 4  # Less variance for good students
        else:
            variance = self.variation_days / 2  # More variance for average/struggling
            
        # Add some randomized offset around the combined factor
        days_offset = int(combined_factor * self.variation_days + 
                        random.normalvariate(0, variance))
        
        # Apply the offset to the base cutoff date
        effective_date = self.cutoff_date + timedelta(days=days_offset)
        
        # Ensure date stays within reasonable bounds
        academic_year_start = ACADEMIC_YEAR.get("start_date", datetime(2023, 9, 1))
        academic_year_end = ACADEMIC_YEAR.get("end_date", datetime(2024, 6, 30))
        
        # Constrain to academic year boundaries
        effective_date = max(academic_year_start, min(effective_date, academic_year_end))
        
        return effective_date    
    

    def _get_subject_progress_rate(self, student: Student, subject: str) -> float:
        """
        Calculate how quickly a student progresses in a specific subject.
        
        This considers the student's subject strength and their overall
        profile/performance level.
        
        Args:
            student (Student): The student to calculate for
            subject (str): The subject area to check
            
        Returns:
            float: Progress rate multiplier (>1 means faster, <1 means slower)
        """
        if not subject or subject not in student.subject_strengths:
            # No specific strength data, use base performance
            return 1.0
        
        # Get the student's strength in this subject
        subject_strength = student.subject_strengths.get(subject, 1.0)
        
        # Get the student's profile and engagement factors
        profile = self._get_student_profile(student)
        
        # Base progress rate adjustment from subject strength
        # Subject strength is typically 0.7-1.3, we want to transform to 0.5-1.5 range
        progress_rate = 0.5 + subject_strength
        
        # Apply additional profile-based modifiers
        if profile == "High Achiever":
            # High achievers progress more consistently across subjects
            progress_rate = (progress_rate + 1.3) / 2  # Pull toward 1.3
        elif profile == "Above Average":
            # Above average students progress well in stronger subjects
            progress_rate = progress_rate * 1.1
        elif profile == "Average":
            # Average students show more variation based on subject
            progress_rate = progress_rate  # No adjustment
        else:  # Struggling
            # Struggling students show even more extreme variation
            if subject_strength < 1.0:
                # Even worse in weak subjects
                progress_rate = progress_rate * 0.8
            else:
                # But might still do decently in strong subjects
                progress_rate = progress_rate * 0.9
        
        # Ensure rate is in reasonable bounds
        return max(0.3, min(2.0, progress_rate))
    def _get_assignment_subject(self, assignment: Assignment) -> Optional[str]:
        """
        Determine the subject area of an assignment by looking up its module.
        
        Args:
            assignment (Assignment): The assignment to check
            
        Returns:
            Optional[str]: The subject area, or None if not determinable
        """
        # Find the module for this assignment
        module = next((m for m in self.modules if m.id == assignment.module_id), None)
        
        if module and module.subject:
            return module.subject
        
        # If not found at module level, try to determine from the course
        if module:
            course = next((c for c in self.courses if c.id == module.course_id), None)
            if course and course.subject_area:
                return course.subject_area
        
        return None
    
    def _calculate_progress_probability(self, student: Student, assignment: Assignment, subject_area: Optional[str] = None) -> float:
        """
        Calculate the probability that a student has completed an assignment by mid-semester.
        
        This considers multiple factors including student profile, subject strength,
        time since the assignment was made available, and work patterns.
        
        Args:
            student (Student): The student to calculate for
            assignment (Assignment): The assignment to calculate for
            subject_area (Optional[str]): The subject area of the assignment
            
        Returns:
            float: Probability from 0.0 to 1.0 that the assignment is completed
        """
        if not self.is_mid_semester:
            return 1.0  # In full-semester mode, all available assignments are completed
        
        # Start with a base probability of 50%
        base_prob = 0.5
        
        # Get student's effective cutoff date
        student_effective_date = self._get_student_effective_date(student)
        
        # Special case: assignment is due after the student's effective date
        # (i.e., it's a future assignment from the student's perspective)
        if assignment.assign_date > student_effective_date:
            # Determine probability of working ahead
            profile = self._get_student_profile(student)
            future_prob = MID_SEMESTER_SETTINGS.get('future_assignment_probability', {}).get(profile, 0.0)
            return future_prob
        
        # Special case: assignment is past due based on student's timeline
        # (high probability of completion, but not 100%)
        if assignment.due_date < student_effective_date:
            # Start with a high probability for past-due assignments
            base_prob = 0.9
        
        # Adjust based on student profile
        profile_adjustment = self._get_profile_adjustment(student)
        
        # Adjust based on subject strength
        subject_adjustment = self._get_subject_adjustment(student, subject_area)
        
        # Adjust based on time factors
        time_adjustment = self._get_time_adjustment(assignment, student, student_effective_date)
        
        # Adjust based on student's work patterns
        work_pattern_adjustment = self._get_work_pattern_adjustment(student, assignment)
        
        # Combine all factors
        final_prob = base_prob + profile_adjustment + subject_adjustment + time_adjustment + work_pattern_adjustment
        
        # Get minimum completion probability based on student profile
        profile = self._get_student_profile(student)
        min_completion = MID_SEMESTER_SETTINGS.get('min_completion_probability', {}).get(profile, 0.0)
        
        # Ensure probability is at least the minimum and at most 1.0
        final_prob = max(min_completion, min(1.0, final_prob))
        
        return final_prob    
    
    def _get_time_adjustment(self, assignment: Assignment, student: Student, effective_date: datetime) -> float:
        """
        Calculate probability adjustment based on time since the assignment was made available.
        
        Args:
            assignment (Assignment): The assignment to calculate for
            student (Student): The student to calculate for
            effective_date (datetime): The student's effective mid-semester date
            
        Returns:
            float: Adjustment value to add to base probability
        """
        # If assignment isn't yet available or is past due, no additional time adjustment
        if assignment.assign_date > effective_date or assignment.due_date < effective_date:
            return 0.0
        
        # Calculate where we are in the assignment timeline
        total_days = max(1, (assignment.due_date - assignment.assign_date).days)
        elapsed_days = max(0, (effective_date - assignment.assign_date).days)
        
        # Calculate fraction of time elapsed
        time_fraction = elapsed_days / total_days
        
        # Calculate time decay factor from settings
        time_decay = MID_SEMESTER_SETTINGS.get('time_decay_factor', 0.1)
        
        # Apply a non-linear function for time probability:
        # - Low at the beginning (students just starting)
        # - Accelerates in the middle (most work happens here)
        # - Rapidly increases near the deadline (cramming effect)
        if time_fraction < 0.3:
            # Initial slow period
            time_adjustment = time_fraction * 0.5  # Max +0.15
        elif time_fraction < 0.7:
            # Middle period, steady progress
            time_adjustment = 0.15 + (time_fraction - 0.3) * 0.5  # From +0.15 to +0.35
        else:
            # Final rush period
            time_adjustment = 0.35 + (time_fraction - 0.7) * 1.5  # From +0.35 to +0.8
        
        # Adjust based on the time decay setting
        time_adjustment = time_adjustment * (1 + time_decay)
        
        return time_adjustment
    
    def _get_work_pattern_adjustment(self, student: Student, assignment: Assignment) -> float:
        """
        Calculate probability adjustment based on student's work patterns.
        
        Args:
            student (Student): The student to calculate for
            assignment (Assignment): The assignment to calculate for
            
        Returns:
            float: Adjustment value to add to base probability
        """
        # Get student's work patterns
        work_pattern = self._get_student_work_pattern(student)
        
        # Initialize adjustment
        adjustment = 0.0
        
        # Early starters are more likely to have completed assignments
        if work_pattern["early_starter"]:
            adjustment += 0.1
        
        # Procrastinators are less likely to have completed assignments until close to due date
        if work_pattern["procrastinator"]:
            adjustment -= 0.15
        
        # Consistent workers are more likely to stay on top of assignments
        if work_pattern["consistent"]:
            adjustment += 0.1
        
        # Binge workers are more variable
        if work_pattern["binge_worker"]:
            # Add some randomness to binge workers - they might have had a "binge" session
            # that included this assignment, or they might not have done it yet
            if random.random() < 0.5:
                adjustment += 0.2
            else:
                adjustment -= 0.1
        
        # Weekend preferences can matter
        today = self.cutoff_date if self.cutoff_date else datetime.now()
        is_weekend = today.weekday() >= 5  # 5=Saturday, 6=Sunday
        
        if work_pattern["weekend_worker"]:
            if is_weekend:
                # Weekend workers do more work on weekends
                adjustment += 0.1
            else:
                # ...and less on weekdays
                adjustment -= 0.05
        
        # Consider assignment type - some students prioritize certain types
        assignment_type = assignment.assignment_type or "Assignment"
        if assignment_type.lower() in ["exam", "quiz"]:
            # Most students prioritize exams/quizzes more
            adjustment += 0.1
        elif assignment_type.lower() in ["project"]:
            # Projects are more variable - binge workers might push them off
            if work_pattern["binge_worker"]:
                adjustment -= 0.1
        
        # Return the total work pattern adjustment
        return adjustment


    def _get_student_work_pattern(self, student: Student) -> Dict[str, Any]:
        """
        Generate a model of a student's work pattern preferences.
        
        This simulates whether students tend to work ahead, procrastinate,
        work on weekends, etc.
        
        Args:
            student (Student): The student to model
            
        Returns:
            Dict[str, Any]: Work pattern attributes
        """
        # Get the student's profile
        profile = self._get_student_profile(student)
        
        # Initialize with defaults
        work_pattern = {
            "early_starter": False,    # Tends to start assignments early
            "procrastinator": False,   # Tends to do work at the last minute
            "weekend_worker": False,   # Tends to do more work on weekends
            "consistent": False,       # Works at a steady pace
            "binge_worker": False      # Does work in intense bursts
        }
        
        # Set probabilities based on profile
        if profile == "High Achiever":
            early_prob = 0.8
            procrastinate_prob = 0.1
            weekend_prob = 0.6
            consistent_prob = 0.8
            binge_prob = 0.3
        elif profile == "Above Average":
            early_prob = 0.6
            procrastinate_prob = 0.3
            weekend_prob = 0.5
            consistent_prob = 0.6
            binge_prob = 0.4
        elif profile == "Average":
            early_prob = 0.3
            procrastinate_prob = 0.5
            weekend_prob = 0.5
            consistent_prob = 0.4
            binge_prob = 0.5
        else:  # Struggling
            early_prob = 0.1
            procrastinate_prob = 0.8
            weekend_prob = 0.4
            consistent_prob = 0.2
            binge_prob = 0.7
        
        # Apply student-specific random variation to the base probabilities
        work_pattern["early_starter"] = random.random() < early_prob
        work_pattern["procrastinator"] = random.random() < procrastinate_prob
        work_pattern["weekend_worker"] = random.random() < weekend_prob
        work_pattern["consistent"] = random.random() < consistent_prob
        work_pattern["binge_worker"] = random.random() < binge_prob
        
        # Ensure some logical consistency in the patterns
        if work_pattern["early_starter"] and work_pattern["procrastinator"]:
            # These are somewhat contradictory, so pick one based on student profile
            if profile in ["High Achiever", "Above Average"]:
                work_pattern["procrastinator"] = False
            else:
                work_pattern["early_starter"] = False
        
        # Similarly, consistent and binge-working are somewhat contradictory
        if work_pattern["consistent"] and work_pattern["binge_worker"]:
            if profile in ["High Achiever", "Above Average"]:
                work_pattern["binge_worker"] = False
            else:
                work_pattern["consistent"] = False
        
        return work_pattern
    def _get_student_profile(self, student: Student) -> str:
        """Determine a student's performance profile based on their base performance."""
        if student.base_performance >= 90:
            return "High Achiever"
        elif student.base_performance >= 80:
            return "Above Average"
        elif student.base_performance >= 70:
            return "Average"
        else:
            return "Struggling"

    def _get_profile_adjustment(self, student: Student) -> float:
        """
        Calculate probability adjustment based on student's performance profile.
        
        Args:
            student (Student): The student to calculate for
            
        Returns:
            float: Adjustment value to add to base probability
        """
        profile = self._get_student_profile(student)
        
        # Get profile-specific adjustment factor from settings
        base_adjustment = MID_SEMESTER_SETTINGS.get('profile_progress_modifiers', {}).get(profile, 0)
        
        # Scale this to a reasonable probability adjustment (±0.25 max)
        scaled_adjustment = base_adjustment * 0.25
        
        # Add some individualization within the profile
        # Higher performing students within a profile tier have slightly higher completion rates
        performance_factor = (student.base_performance % 10) / 40  # Small adjustment based on performance within tier
        
        # Combine adjustments
        total_adjustment = scaled_adjustment + performance_factor
        
        return total_adjustment
    

    def _get_subject_adjustment(self, student: Student, subject_area: Optional[str]) -> float:
        """
        Calculate probability adjustment based on student's strength in a subject.
        
        Args:
            student (Student): The student to calculate for
            subject_area (Optional[str]): The subject area to check
            
        Returns:
            float: Adjustment value to add to base probability
        """
        if not subject_area or not student.subject_strengths:
            return 0.0  # No adjustment if subject area is unknown
        
        # Get the student's strength in this subject (default to 1.0 if not found)
        subject_strength = student.subject_strengths.get(subject_area, 1.0)
        
        # Convert strength (typically 0.7-1.3) to a probability adjustment (-0.15 to +0.15)
        # A strength of 1.0 means no adjustment
        max_impact = MID_SEMESTER_SETTINGS.get('subject_strength_impact', 0.25)
        adjustment = (subject_strength - 1.0) * max_impact
        
        # Scale based on profile - subject strength has more impact on struggling students
        profile = self._get_student_profile(student)
        if profile == "Struggling":
            # Amplify the effect for struggling students
            adjustment = adjustment * 1.5
        elif profile == "High Achiever":
            # Reduce the effect for high achievers (they're more consistent)
            adjustment = adjustment * 0.8
        
        return adjustment
    
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
    ) -> Optional[Dict[str, Any]]:
        """
        Generate assignment submission data for a specific student and assignment.
        
        Args:
            student (Student): The student
            assignment (Assignment): The assignment
            
        Returns:
            Optional[Dict[str, Any]]: Generated student-assignment data or None if not completed
        """
        # Mid-semester logic: determine if this assignment would be completed
        if self.is_mid_semester:
            # Get the subject area for this assignment
            subject_area = self._get_assignment_subject(assignment)
            
            # Determine if assignment is available to this student
            if not self._is_assignment_available(assignment, student):
                return None  # Assignment not yet available to this student
            
            # Calculate completion probability
            completion_prob = self._calculate_progress_probability(
                student, assignment, subject_area)
            
            # Determine if student has completed this assignment
            if random.random() > completion_prob:
                return None  # Student hasn't completed this assignment yet
        
        # Continue with original logic for generating submission data
        # (Using the existing code from the paste.txt document)
        
        # Determine if this will be a late submission
        assignment_type = assignment.assignment_type or "Assignment"
        if assignment_type.lower() in ["exam", "quiz"]:
            is_late = False  # Exams and quizzes cannot be late
        else:
            is_late = random.random() < self.late_submission_probability

        # Get assignment type info for score distribution
        type_info = self._get_assignment_type_info(assignment_type)

        # Generate submission date
        submission_date = generate_submission_date(
            assignment.assign_date,
            assignment.due_date,
            is_late,
            self.max_days_late
        )
        
        # For mid-semester submissions, ensure the submission date isn't in the future
        if self.is_mid_semester:
            student_effective_date = self._get_student_effective_date(student)
            if submission_date > student_effective_date:
                # Adjust to be at or before the student's effective date
                submission_date = student_effective_date - timedelta(
                    days=random.randint(0, 2))  # Random 0-2 days before cutoff
        
        # Get student's work pattern and adjust submission date accordingly
        work_pattern = self._get_student_work_pattern(student)

        # Adjust submission date based on work pattern
        if work_pattern["early_starter"]:
            # Early starters tend to submit earlier
            early_threshold = 0.6  # 60% of time between assign and due
            elapsed_days = (assignment.due_date - assignment.assign_date).days
            early_days = int(elapsed_days * early_threshold)
            early_date = assignment.due_date - timedelta(days=early_days)
            
            # Generate submission date with bias toward earlier submission
            if random.random() < 0.7:  # 70% chance of early submission
                submission_date = generate_submission_date(
                    assignment.assign_date,
                    early_date,  # Use earlier "due date"
                    is_late=False
                )
        elif work_pattern["procrastinator"]:
            # Procrastinators submit close to due date
            # Higher chance of late submission
            local_late_prob = self.late_submission_probability * 2  # Double the late probability
            is_late = is_late or (random.random() < local_late_prob)
            
            # For on-time submissions, bias toward last minute
            if not is_late:
                last_minute_window = min(5, (assignment.due_date - assignment.assign_date).days // 2)
                last_minute_date = assignment.due_date - timedelta(days=last_minute_window)
                submission_date = generate_submission_date(
                    last_minute_date,
                    assignment.due_date,
                    is_late=False
                )

        # Weekend worker preference
        if work_pattern["weekend_worker"] and not is_late:
            # Adjust submission date to prefer weekends
            for offset in range(-2, 3):  # Try ±2 days to find a weekend
                test_date = submission_date + timedelta(days=offset)
                # Check if weekend (5=Saturday, 6=Sunday)
                if test_date.weekday() >= 5:
                    # 70% chance to move to weekend if reasonably close
                    if random.random() < 0.7:
                        submission_date = test_date
                        break
        
        # Determine student's score based on their performance profile
        # and the assignment characteristics
        mean_score = type_info.get('mean_score', 75)
        std_dev = type_info.get('std_dev', 10)
        skewness = type_info.get('skewness', -0.5)
        
        # Find subject area from module if not already determined
        if subject_area is None:
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
        
        # For mid-semester data, add a status field
        student_assignment["status"] = "completed"        
        return student_assignment    
    
    def generate_course_performance_data(
        self, 
        student: Student, 
        course: Course,
        completed_assignments: List[Dict[str, Any]] = None,
        pending_assignments: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate overall course performance data for a specific student and course.
        
        Args:
            student (Student): The student
            course (Course): The course
            completed_assignments: List of completed assignment submissions
            pending_assignments: List of pending assignment submissions
            
        Returns:
            Dict[str, Any]: Generated student-course data
        """
        # Get assignments for this course
        course_assignments = self._get_assignments_for_course(course.id)
        
        # Find student's submissions for these assignments
        if completed_assignments is None:
            student_submissions = [
                sa for sa in self.student_assignments 
                if sa['studentId'] == student.id and 
                sa['assignmentId'] in [a.id for a in course_assignments]
            ]
        else:
            student_submissions = completed_assignments
        
        # Initialize basic student-course record
        student_course = {
            "id": generate_unique_id("sc_"),
            "studentId": student.id,
            "courseId": course.id,
            "finalScore": 0.0,
            "totalTimeSpentMinutes": 0,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
        
        # Get total assignments count
        total_assignments = len(course_assignments)
        
        # Count completed assignments
        completed_count = len(student_submissions)
        
        # Calculate completion percentage regardless of semester mode
        completion_percentage = round(
            (completed_count / total_assignments * 100), 1
        ) if total_assignments > 0 else 0
        
        # Add completion percentage to record
        student_course["completionPercentage"] = completion_percentage
        
        # If no submissions, return basic record with zero performance but accurate completion
        if not student_submissions:
            return student_course
        
        # Calculate scores and weights from completed assignments only
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
        
        # Calculate final score from completed assignments only
        if assignment_scores:
            final_score = calculate_weighted_score(assignment_scores, assignment_weights)
        else:
            final_score = 0.0
        
        # Update basic fields - score reflects only completed work
        student_course["finalScore"] = round(final_score, 1)
        student_course["totalTimeSpentMinutes"] = total_time_spent
        
        # For mid-semester data, add detailed progress metrics
        if self.is_mid_semester:
            # Determine assignment counts by availability
            available_assignments = 0
            future_assignments = 0
            pending_count = 0
            
            # If pending_assignments was provided, use its length
            if pending_assignments is not None:
                pending_count = len(pending_assignments)
            
            # Count available vs. future assignments
            student_effective_date = self._get_student_effective_date(student)
            for assignment in course_assignments:
                if assignment.assign_date <= student_effective_date:
                    available_assignments += 1
                else:
                    future_assignments += 1
            
            # If pending_count wasn't explicitly provided, calculate it
            if pending_assignments is None:
                pending_count = available_assignments - completed_count
            
            # Calculate weighted completion percentage
            # This gives partial credit for some assignments based on their weights
            total_weight = sum(a.weight for a in course_assignments)
            completed_weight = sum(
                a.weight for a in course_assignments 
                if a.id in [sa['assignmentId'] for sa in student_submissions]
            )
            
            weighted_completion = (completed_weight / total_weight * 100) if total_weight > 0 else 0
            
            # Calculate progress metrics
            progress_metrics = {
                "totalAssignments": total_assignments,
                "completedAssignments": completed_count,
                "pendingAssignments": pending_count,
                "futureAssignments": future_assignments,
                "availableAssignments": available_assignments,
                "completionRate": round(completed_count / available_assignments * 100, 1) if available_assignments > 0 else 0,
                "weightedCompletion": round(weighted_completion, 1),
                "overallProgressPercent": round(completed_count / total_assignments * 100, 1) if total_assignments > 0 else 0
            }
            
            # Calculate estimated final score (for reference only - this is the projected score)
            # For incomplete assignments, estimate using student's performance profile
            if total_assignments > completed_count:
                # Get profile-based expected performance
                profile = self._get_student_profile(student)
                expected_scores = []
                expected_weights = []
                
                # Add actual scores from completed assignments
                expected_scores.extend(assignment_scores)
                expected_weights.extend(assignment_weights)
                
                # Add estimated scores for pending assignments
                for assignment in course_assignments:
                    if assignment.id not in [sa['assignmentId'] for sa in student_submissions]:
                        # Find subject area
                        subject_area = self._get_assignment_subject(assignment)
                        
                        # Calculate expected score based on profile and subject
                        base_score = student.base_performance
                        if subject_area and subject_area in student.subject_strengths:
                            base_score *= student.subject_strengths[subject_area]
                        
                        # Add some randomness
                        expected_score = base_score * random.uniform(0.85, 1.05)
                        expected_scores.append(min(100, max(0, expected_score)))
                        expected_weights.append(assignment.weight)
                
                # Calculate projected final score - this is separate from actual performance
                projected_score = calculate_weighted_score(expected_scores, expected_weights)
                progress_metrics["projectedFinalScore"] = round(projected_score, 1)
            else:
                # If all assignments are complete, projected = actual
                progress_metrics["projectedFinalScore"] = student_course["finalScore"]
            
            # Add on-track status
            if progress_metrics["completionRate"] >= 90:
                progress_metrics["onTrackStatus"] = "Ahead"
            elif progress_metrics["completionRate"] >= 70:
                progress_metrics["onTrackStatus"] = "On Track"
            elif progress_metrics["completionRate"] >= 50:
                progress_metrics["onTrackStatus"] = "Slightly Behind"
            else:
                progress_metrics["onTrackStatus"] = "Behind"
            
            # Add to student-course record
            student_course["progressMetrics"] = progress_metrics
            
            # Add trend analysis
            if completed_count >= 2:
                # Sort submissions by date to analyze trend
                sorted_submissions = sorted(
                    student_submissions, 
                    key=lambda s: s['submissionDate']
                )
                
                # Calculate trend (positive, neutral, negative)
                early_scores = [s['assessmentScore'] for s in sorted_submissions[:completed_count//2]]
                late_scores = [s['assessmentScore'] for s in sorted_submissions[completed_count//2:]]
                
                early_avg = sum(early_scores) / len(early_scores) if early_scores else 0
                late_avg = sum(late_scores) / len(late_scores) if late_scores else 0
                
                trend_diff = late_avg - early_avg
                
                if trend_diff > 5:
                    trend = "Improving"
                elif trend_diff < -5:
                    trend = "Declining"
                else:
                    trend = "Steady"
                    
                student_course["trend"] = trend
        
        return student_course
    
    def get_mid_semester_status_report(self) -> Dict[str, Any]:
        """
        Generate a detailed report on assignment status at mid-semester.
        
        Returns:
            Dict[str, Any]: Report data with statistics on assignment completion
        """
        if not self.is_mid_semester:
            return {"error": "This method is only available in mid-semester mode"}
        
        # Compile statistics about assignment completion
        report = {
            "cutoffDate": self.cutoff_date.isoformat() if self.cutoff_date else None,
            "variationDays": self.variation_days,
            "assignmentStatus": getattr(self, 'assignment_status_counts', {}),
            "profileBreakdown": {}
        }
        
        # Analyze completion by student profile
        profile_stats = {}
        for student in self.students:
            profile = self._get_student_profile(student)
            
            if profile not in profile_stats:
                profile_stats[profile] = {
                    "studentCount": 0,
                    "completedAssignments": 0,
                    "totalAvailableAssignments": 0,
                    "completionRate": 0.0
                }
            
            profile_stats[profile]["studentCount"] += 1
            
            # Count completed assignments for this student
            completed_count = sum(1 for sa in self.student_assignments 
                                if sa['studentId'] == student.id)
            profile_stats[profile]["completedAssignments"] += completed_count
            
            # Count available assignments for this student
            available_count = sum(1 for a in self.assignments 
                                if self._is_assignment_available(a, student))
            profile_stats[profile]["totalAvailableAssignments"] += available_count
        
        # Calculate completion rates
        for profile, stats in profile_stats.items():
            if stats["totalAvailableAssignments"] > 0:
                stats["completionRate"] = round(
                    stats["completedAssignments"] / stats["totalAvailableAssignments"] * 100, 1
                )
        
        report["profileBreakdown"] = profile_stats
        
        return report
    
    def generate_mid_semester_progress_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive report on student progress at mid-semester.
        
        This includes overall statistics, profile breakdowns, and subject-specific analysis.
        
        Returns:
            Dict[str, Any]: Detailed progress report
        """
        if not self.is_mid_semester:
            return {"error": "This method is only available in mid-semester mode"}
        
        # Start with the basic summary
        report = getattr(self, 'mid_semester_summary', {})
        
        # Add subject-specific analysis
        subject_breakdown = {}
        
        # Find all unique subject areas
        all_subjects = set()
        for module in self.modules:
            if module.subject:
                all_subjects.add(module.subject)
        
        # For each subject, analyze completion rates
        for subject in all_subjects:
            subject_assignments = []
            
            # Find all assignments in this subject
            for assignment in self.assignments:
                assignment_subject = self._get_assignment_subject(assignment)
                if assignment_subject == subject:
                    subject_assignments.append(assignment)
            
            if not subject_assignments:
                continue
            
            # Count completed assignments in this subject
            completed_count = 0
            available_count = 0
            future_count = 0
            
            for student in self.students:
                student_effective_date = self._get_student_effective_date(student)
                
                for assignment in subject_assignments:
                    if assignment.assign_date > student_effective_date:
                        future_count += 1
                    else:
                        available_count += 1
                        
                        # Check if this student completed this assignment
                        completed = any(
                            sa['studentId'] == student.id and sa['assignmentId'] == assignment.id
                            for sa in self.student_assignments
                        )
                        
                        if completed:
                            completed_count += 1
            
            # Calculate completion rate for this subject
            completion_rate = round(completed_count / available_count * 100, 1) if available_count > 0 else 0
            
            # Add to subject breakdown
            subject_breakdown[subject] = {
                "totalAssignments": len(subject_assignments),
                "availableAssignments": available_count,
                "completedAssignments": completed_count,
                "futureAssignments": future_count,
                "completionRate": completion_rate
            }
        
        # Add to report
        report["subjectBreakdown"] = subject_breakdown
        
        # Add time-based analysis
        # Group assignments into time periods (early, mid, late semester)
        if self.cutoff_date:
            academic_start = ACADEMIC_YEAR.get("start_date")
            days_elapsed = (self.cutoff_date - academic_start).days
            
            early_cutoff = academic_start + timedelta(days=days_elapsed//3)
            mid_cutoff = academic_start + timedelta(days=2*days_elapsed//3)
            
            time_periods = {
                "early": {"completed": 0, "available": 0, "rate": 0},
                "mid": {"completed": 0, "available": 0, "rate": 0},
                "recent": {"completed": 0, "available": 0, "rate": 0}
            }
            
            # Analyze completion by time period
            for assignment in self.assignments:
                if assignment.assign_date <= early_cutoff:
                    period = "early"
                elif assignment.assign_date <= mid_cutoff:
                    period = "mid"
                else:
                    period = "recent"
                
                # Count available and completed
                for student in self.students:
                    student_effective_date = self._get_student_effective_date(student)
                    
                    if assignment.assign_date <= student_effective_date:
                        time_periods[period]["available"] += 1
                        
                        # Check if completed
                        completed = any(
                            sa['studentId'] == student.id and sa['assignmentId'] == assignment.id
                            for sa in self.student_assignments
                        )
                        
                        if completed:
                            time_periods[period]["completed"] += 1
            
            # Calculate completion rates
            for period, data in time_periods.items():
                if data["available"] > 0:
                    data["rate"] = round(data["completed"] / data["available"] * 100, 1)
            
            report["timeAnalysis"] = time_periods
        
        # Add student outlier analysis
        outliers = {
            "highPerformers": [],
            "strugglingStudents": []
        }
        
        # Sort students by completion rate
        sorted_metrics = sorted(
            getattr(self, 'student_progress_metrics', []),
            key=lambda m: m["completionRate"],
            reverse=True
        )
        
        # Get top and bottom 10%
        if sorted_metrics:
            num_outliers = max(1, len(sorted_metrics) // 10)
            
            outliers["highPerformers"] = [
                {"studentId": m["studentId"], 
                "completionRate": m["completionRate"],
                "profile": m["profile"]}
                for m in sorted_metrics[:num_outliers]
            ]
            
            outliers["strugglingStudents"] = [
                {"studentId": m["studentId"], 
                "completionRate": m["completionRate"],
                "profile": m["profile"]}
                for m in sorted_metrics[-num_outliers:]
            ]
        
        report["outlierAnalysis"] = outliers
        
        return report

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
        
        # Track assignment status data for mid-semester reporting
        if self.is_mid_semester:
            assignment_status_counts = {
                "completed": 0,
                "pending": 0,
                "future": 0
            }
            
            # Track detailed assignment status by student profile
            status_by_profile = {
                "High Achiever": {"completed": 0, "pending": 0, "future": 0, "total": 0},
                "Above Average": {"completed": 0, "pending": 0, "future": 0, "total": 0},
                "Average": {"completed": 0, "pending": 0, "future": 0, "total": 0},
                "Struggling": {"completed": 0, "pending": 0, "future": 0, "total": 0}
            }
            
            # For storing additional metadata about student progress
            student_progress_metrics = []
        
        # Process each student
        for student in self.students:
            student_profile = self._get_student_profile(student)
            student_metrics = {
                "studentId": student.id,
                "profile": student_profile,
                "totalAssignments": 0,
                "completedAssignments": 0,
                "pendingAssignments": 0,
                "futureAssignments": 0,
                "completionRate": 0
            }
            
            # For each course the student is enrolled in
            for course_id in student.courses:
                # Track that we've processed this student-course pair
                processed_student_courses.add((student.id, course_id))
                
                # Get all assignments for this course
                course_assignments = self._get_assignments_for_course(course_id)
                
                # Lists to track assignment status
                student_completed_assignments = []
                student_pending_assignments = []
                student_future_assignments = []
                
                # Generate student-assignment data for each assignment
                for assignment in course_assignments:
                    # Update total assignments count for metrics
                    student_metrics["totalAssignments"] += 1
                    
                    # Determine assignment status for this student
                    if self.is_mid_semester:
                        # Check if this assignment is available
                        student_effective_date = self._get_student_effective_date(student)
                        subject_area = self._get_assignment_subject(assignment)
                        
                        # Determine assignment status
                        if assignment.assign_date > student_effective_date:
                            # Future assignment
                            status = "future"
                            student_future_assignments.append(assignment)
                            student_metrics["futureAssignments"] += 1
                            assignment_status_counts["future"] += 1
                            status_by_profile[student_profile]["future"] += 1
                        else:
                            # Assignment is available, check if completed
                            completion_prob = self._calculate_progress_probability(
                                student, assignment, subject_area)
                            
                            if random.random() <= completion_prob:
                                # Assignment is completed
                                status = "completed"
                                
                                # Generate submission data
                                student_assignment = self.generate_student_assignment_data(
                                    student, assignment
                                )
                                
                                if student_assignment:
                                    self.student_assignments.append(student_assignment)
                                    student_completed_assignments.append(student_assignment)
                                    student_metrics["completedAssignments"] += 1
                                    assignment_status_counts["completed"] += 1
                                    status_by_profile[student_profile]["completed"] += 1
                                    
                                    # Add submission to assignment for tracking
                                    assignment.add_student_submission(
                                        student.id,
                                        student_assignment['submissionDate'],
                                        student_assignment['assessmentScore'],
                                        student_assignment['timeSpentMinutes']
                                    )
                            else:
                                # Assignment is available but not completed
                                status = "pending"
                                pending_assignment = {
                                    "id": generate_unique_id("sa_"),
                                    "studentId": student.id,
                                    "assignmentId": assignment.id,
                                    "status": status,
                                    "isAvailable": True,
                                    "createdAt": datetime.now(),
                                    "updatedAt": datetime.now()
                                }
                                student_pending_assignments.append(pending_assignment)
                                student_metrics["pendingAssignments"] += 1
                                assignment_status_counts["pending"] += 1
                                status_by_profile[student_profile]["pending"] += 1
                    else:
                        # Not in mid-semester mode, all assignments should be completed
                        student_assignment = self.generate_student_assignment_data(
                            student, assignment
                        )
                        
                        if student_assignment:
                            self.student_assignments.append(student_assignment)
                            student_completed_assignments.append(student_assignment)
                            student_metrics["completedAssignments"] += 1  # Count completed assignments
                            
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
                        student, course, student_completed_assignments, student_pending_assignments
                    )
                    self.student_courses.append(student_course)
            
            # After processing all courses for this student, update the student's total metrics
            student_courses = [sc for sc in self.student_courses if sc['studentId'] == student.id]
            if student_courses:
                # Calculate score only based on completed assignments (finalScore already only includes completed work)
                total_score = sum(sc['finalScore'] for sc in student_courses) / len(student_courses)
                
                # Calculate overall completion percentage
                overall_completion = sum(sc.get('completionPercentage', 0) for sc in student_courses) / len(student_courses)
                
                # Update student with both metrics
                student.update_total_score(round(total_score, 1))
                
                # Store completion percentage if the student class has this attribute
                if hasattr(student, 'completion_percentage'):
                    student.completion_percentage = round(overall_completion, 1)
                
                # Calculate completion rate for student metrics
                available_assignments = student_metrics["completedAssignments"] + student_metrics["pendingAssignments"]
                if available_assignments > 0:
                    student_metrics["completionRate"] = round(
                        student_metrics["completedAssignments"] / available_assignments * 100, 1
                    )
                
                # Increment profile total count
                if self.is_mid_semester:
                    status_by_profile[student_profile]["total"] += student_metrics["totalAssignments"]
                    student_progress_metrics.append(student_metrics)
        
        # If in mid-semester mode, store statistics about assignment completion status
        if self.is_mid_semester:
            # Calculate total assignments
            total_assignments = sum(assignment_status_counts.values())
            
            # Calculate percentages
            if total_assignments > 0:
                # Use a temporary dictionary to store the percentages
                percentages = {
                    f"{status}Percent": round(count / total_assignments * 100, 1) 
                    for status, count in assignment_status_counts.items()
                }
                # Update the original dictionary with the new keys
                assignment_status_counts.update(percentages)
            
            # Calculate profile-specific completion rates
            for profile, stats in status_by_profile.items():
                if stats["total"] > 0:
                    available = stats["completed"] + stats["pending"]
                    if available > 0:
                        stats["completionRate"] = round(stats["completed"] / available * 100, 1)
                    stats["completedPercent"] = round(stats["completed"] / stats["total"] * 100, 1)
                    stats["pendingPercent"] = round(stats["pending"] / stats["total"] * 100, 1)
                    stats["futurePercent"] = round(stats["future"] / stats["total"] * 100, 1)
            
            # Store all the metrics
            self.assignment_status_counts = assignment_status_counts
            self.status_by_profile = status_by_profile
            self.student_progress_metrics = student_progress_metrics
            
            # Generate a summary report
            self.mid_semester_summary = {
                "cutoffDate": self.cutoff_date.isoformat() if self.cutoff_date else None,
                "overallCompletion": round(
                    assignment_status_counts["completed"] / 
                    (assignment_status_counts["completed"] + assignment_status_counts["pending"]) * 100, 1
                ) if (assignment_status_counts["completed"] + assignment_status_counts["pending"]) > 0 else 0,
                "statusCounts": assignment_status_counts,
                "profileBreakdown": status_by_profile
            }
        
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
    
