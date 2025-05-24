"""
Assignment model for the educational data generator.
This module defines the Assignment class representing tasks within modules.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class Assignment:
    """
    Assignment class representing a task within a module in the educational system.
    """
    def __init__(
        self,
        id: str,
        name: str,
        module_id: str,
        assign_date: datetime,
        due_date: datetime,
        description: Optional[str] = None,
        assignment_type: Optional[str] = None,
        max_score: float = 100.0,
        weight: float = 1.0,
        max_attempts: Optional[int] = None,
        course_id: Optional[str] = None
    ):
        """
        Initialize a new Assignment instance.
        
        Args:
            id (str): Unique identifier for the assignment
            name (str): Name of the assignment
            module_id (str): ID of the module this assignment belongs to
            assign_date (datetime): Date when the assignment is assigned
            due_date (datetime): Due date for the assignment
            description (Optional[str]): Description of the assignment
            assignment_type (Optional[str]): Type of assignment (Quiz, Exam, Project, etc.)
            max_score (float): Maximum possible score for the assignment
            weight (float): Weight of this assignment in the module grade calculation
            max_attempts (Optional[int]): Maximum number of attempts allowed
            course_id (Optional[str]): ID of the course this assignment belongs to (for easier access)
        """
        self.id = id
        self.name = name
        self.module_id = module_id
        self.course_id = course_id
        self.assign_date = assign_date
        self.due_date = due_date
        self.description = description
        self.assignment_type = assignment_type
        self.max_score = max_score
        self.weight = weight
        self.max_attempts = max_attempts
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Tracking student submissions
        self.student_submissions: Dict[str, Dict[str, Any]] = {}  # student_id -> submission data
    
    def add_student_submission(
        self,
        student_id: str,
        submission_date: datetime,
        assessment_score: float,
        time_spent_minutes: Optional[float] = None
    ) -> None:
        """
        Record a student's submission for this assignment.
        
        Args:
            student_id (str): ID of the student
            submission_date (datetime): Date and time of submission
            assessment_score (float): Score the student received
            time_spent_minutes (Optional[float]): Time spent on the assignment
        """
        self.student_submissions[student_id] = {
            "submissionDate": submission_date,
            "assessmentScore": assessment_score,
            "timeSpentMinutes": time_spent_minutes,
            "isLate": submission_date > self.due_date if submission_date and self.due_date else False
        }
        self.updated_at = datetime.now()
    
    def get_submission_rate(self) -> float:
        """
        Calculate the submission rate for this assignment.
        
        Returns:
            float: Percentage of student submissions (0-100)
        """
        # This would require knowing the total number of students
        # For now, just return the number of submissions
        return len(self.student_submissions)
    
    def get_average_score(self) -> float:
        """
        Calculate the average score for this assignment.
        
        Returns:
            float: Average score across all submissions
        """
        if not self.student_submissions:
            print("No student submissions found.")
            return 0.0
        
        total_score = sum(
            submission.get("assessmentScore", 0) 
            for submission in self.student_submissions.values()
        )
        return total_score / len(self.student_submissions)
    
    def get_late_rate(self) -> float:
        """
        Calculate the percentage of late submissions.
        
        Returns:
            float: Percentage of late submissions (0-100)
        """
        if not self.student_submissions:
            return 0.0
        
        late_count = sum(
            1 for submission in self.student_submissions.values() 
            if submission.get("isLate", False)
        )
        return (late_count / len(self.student_submissions)) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Assignment object to a dictionary for Firestore.
        
        Returns:
            Dict[str, Any]: Assignment data as a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "moduleId": self.module_id,
            "courseId": self.course_id,
            "assignDate": self.assign_date,
            "dueDate": self.due_date,
            "description": self.description,
            "assignmentType": self.assignment_type,
            "maxScore": self.max_score,
            "weight": self.weight,
            "maxAttempts": self.max_attempts,
            "averageScore": self.get_average_score(),
            "submissionRate": self.get_submission_rate(),
            "lateRate": self.get_late_rate(),
            "createdAt": self.created_at,
            "updatedAt": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Assignment':
        """
        Create an Assignment instance from a dictionary.
        
        Args:
            data (Dict[str, Any]): Dictionary containing assignment data
            
        Returns:
            Assignment: A new Assignment instance
        """
        assignment = cls(
            id=data.get('id', ''),
            name=data.get('name', ''),
            module_id=data.get('moduleId', ''),
            assign_date=data.get('assignDate', datetime.now()),
            due_date=data.get('dueDate', datetime.now()),
            description=data.get('description'),
            assignment_type=data.get('assignmentType'),
            max_score=data.get('maxScore', 100.0),
            weight=data.get('weight', 1.0),
            max_attempts=data.get('maxAttempts'),
            course_id=data.get('courseId', '')
        )
        
        # Set student submissions if available
        if 'studentSubmissions' in data:
            assignment.student_submissions = data['studentSubmissions']
        
        # Set timestamps if available
        if 'createdAt' in data:
            assignment.created_at = data['createdAt']
        if 'updatedAt' in data:
            assignment.updated_at = data['updatedAt']
            
        return assignment
    
    def __repr__(self) -> str:
        """
        String representation of the Assignment instance.
        
        Returns:
            str: A string representation
        """
        return f"Assignment(id={self.id}, name={self.name}, type={self.assignment_type}, course_id={self.course_id})"