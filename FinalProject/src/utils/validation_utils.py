"""
Validation utilities for ensuring data quality and consistency.
This module provides functions for validating generated educational data.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("validation_utils")


def validate_id_format(id_str: str, expected_format: str = "numeric") -> bool:
    """
    Validate that an ID follows the expected format.
    
    Args:
        id_str (str): The ID to validate
        expected_format (str): Expected format ("numeric", "SCH*", "CRS*", etc.)
        
    Returns:
        bool: True if valid, False otherwise
    """
    if id_str is None or not isinstance(id_str, str):
        return False
    
    if expected_format == "numeric":
        # Check for 9-digit numeric ID
        return id_str.isdigit() and len(id_str) == 9
    elif expected_format.endswith("*"):
        # Check for prefix format (e.g., "SCH*")
        prefix = expected_format[:-1]
        return id_str.startswith(prefix) and len(id_str) > len(prefix)
    
    return False


def validate_date_chronology(
    date_pairs: List[Tuple[datetime, datetime, str]]
) -> List[str]:
    """
    Validate that a sequence of date pairs maintains chronological order.
    
    Args:
        date_pairs (List[Tuple[datetime, datetime, str]]): List of (start_date, end_date, entity_name) tuples
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    # First, validate each pair internally
    for start_date, end_date, entity_name in date_pairs:
        if start_date > end_date:
            errors.append(f"Invalid chronology in {entity_name}: start date {start_date} is after end date {end_date}")
    
    # Then, validate sequence chronology
    for i in range(1, len(date_pairs)):
        prev_end = date_pairs[i-1][1]
        current_start = date_pairs[i][0]
        
        if prev_end > current_start:
            errors.append(
                f"Chronology violation between {date_pairs[i-1][2]} and {date_pairs[i][2]}: "
                f"{prev_end} overlaps with {current_start}"
            )
    
    return errors


def validate_entity_relationships(
    parent_ids: Set[str],
    child_entities: List[Dict[str, Any]],
    parent_field: str
) -> List[str]:
    """
    Validate that child entities reference valid parent entities.
    
    Args:
        parent_ids (Set[str]): Set of valid parent entity IDs
        child_entities (List[Dict[str, Any]]): List of child entity dictionaries
        parent_field (str): Field name in child entities that should reference parent ID
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for entity in child_entities:
        parent_id = entity.get(parent_field)
        
        if parent_id is None:
            errors.append(f"Entity {entity.get('id', 'unknown')} missing required parent reference {parent_field}")
        elif parent_id not in parent_ids:
            errors.append(
                f"Entity {entity.get('id', 'unknown')} references non-existent parent "
                f"{parent_field}={parent_id}"
            )
    
    return errors


def validate_score_ranges(entities: List[Dict[str, Any]], score_field: str) -> List[str]:
    """
    Validate that score values are within valid ranges (0-100).
    
    Args:
        entities (List[Dict[str, Any]]): List of entity dictionaries
        score_field (str): Field name containing the score to validate
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for entity in entities:
        score = entity.get(score_field)
        
        if score is not None:
            if not isinstance(score, (int, float)):
                errors.append(
                    f"Entity {entity.get('id', 'unknown')} has non-numeric {score_field}: {score}"
                )
            elif score < 0 or score > 100:
                errors.append(
                    f"Entity {entity.get('id', 'unknown')} has out-of-range {score_field}: {score}"
                )
    
    return errors


def validate_required_fields(
    entities: List[Dict[str, Any]], 
    required_fields: List[str]
) -> List[str]:
    """
    Validate that all entities have the required fields.
    
    Args:
        entities (List[Dict[str, Any]]): List of entity dictionaries
        required_fields (List[str]): List of field names that must be present
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for entity in entities:
        entity_id = entity.get('id', 'unknown')
        for field in required_fields:
            if field not in entity or entity[field] is None:
                errors.append(f"Entity {entity_id} missing required field: {field}")
    
    return errors


def validate_course_enrollment(
    courses: List[Dict[str, Any]], 
    min_students: int = 12, 
    max_students: int = 30
) -> List[str]:
    """
    Validate that courses have appropriate student enrollment counts.
    
    Args:
        courses (List[Dict[str, Any]]): List of course dictionaries
        min_students (int): Minimum expected students per course
        max_students (int): Maximum expected students per course
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for course in courses:
        course_id = course.get('id', 'unknown')
        students = course.get('students', [])
        
        if not isinstance(students, list):
            errors.append(f"Course {course_id} has invalid students field: not a list")
            continue
        
        student_count = len(students)
        
        if student_count < min_students:
            errors.append(
                f"Course {course_id} has too few students: {student_count} (minimum: {min_students})"
            )
        elif student_count > max_students:
            errors.append(
                f"Course {course_id} has too many students: {student_count} (maximum: {max_students})"
            )
    
    return errors


def validate_module_counts(
    courses: List[Dict[str, Any]], 
    min_modules: int = 5, 
    max_modules: int = 30
) -> List[str]:
    """
    Validate that courses have appropriate module counts.
    
    Args:
        courses (List[Dict[str, Any]]): List of course dictionaries
        min_modules (int): Minimum expected modules per course
        max_modules (int): Maximum expected modules per course
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for course in courses:
        course_id = course.get('id', 'unknown')
        modules = course.get('modules', [])
        
        if not isinstance(modules, list):
            errors.append(f"Course {course_id} has invalid modules field: not a list")
            continue
        
        module_count = len(modules)
        
        if module_count < min_modules:
            errors.append(
                f"Course {course_id} has too few modules: {module_count} (minimum: {min_modules})"
            )
        elif module_count > max_modules:
            errors.append(
                f"Course {course_id} has too many modules: {module_count} (maximum: {max_modules})"
            )
    
    return errors


def validate_assignment_counts(
    modules: List[Dict[str, Any]], 
    min_assignments: int = 1, 
    max_assignments: int = 2
) -> List[str]:
    """
    Validate that modules have appropriate assignment counts.
    
    Args:
        modules (List[Dict[str, Any]]): List of module dictionaries
        min_assignments (int): Minimum expected assignments per module
        max_assignments (int): Maximum expected assignments per module
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    for module in modules:
        module_id = module.get('id', 'unknown')
        assignments = module.get('assignments', [])
        
        if not isinstance(assignments, list):
            errors.append(f"Module {module_id} has invalid assignments field: not a list")
            continue
        
        assignment_count = len(assignments)
        
        if assignment_count < min_assignments:
            errors.append(
                f"Module {module_id} has too few assignments: {assignment_count} "
                f"(minimum: {min_assignments})"
            )
        elif assignment_count > max_assignments:
            errors.append(
                f"Module {module_id} has too many assignments: {assignment_count} "
                f"(maximum: {max_assignments})"
            )
    
    return errors


def validate_assignment_submission_rates(
    assignments: List[Dict[str, Any]],
    student_assignments: List[Dict[str, Any]],
    students_per_course: Dict[str, Set[str]],
    modules: List[Dict[str, Any]],
    min_submission_rate: float = 0.7
) -> List[str]:
    """
    Validate that assignments have appropriate submission rates and log statistics.
    
    Args:
        assignments (List[Dict[str, Any]]): List of assignment dictionaries
        student_assignments (List[Dict[str, Any]]): List of student-assignment dictionaries
        students_per_course (Dict[str, Set[str]]): Map of course IDs to student ID sets
        modules (List[Dict[str, Any]]): List of module dictionaries
        min_submission_rate (float): Minimum expected submission rate (0.0-1.0)
        
    Returns:
        List[str]: List of validation error messages, empty if valid
    """
    errors = []
    
    # Create module-to-course mapping for quick lookup
    module_to_course = {module['id']: module['courseId'] for module in modules}
    
    # Group submissions by assignment
    submissions_by_assignment = {}
    for sa in student_assignments:
        assignment_id = sa.get('assignmentId')
        if assignment_id not in submissions_by_assignment:
            submissions_by_assignment[assignment_id] = []
        submissions_by_assignment[assignment_id].append(sa)
    
    # Calculate submission rates and log statistics
    logger.info(f"=== Assignment Submission Statistics ===")
    
    for assignment in assignments:
        assignment_id = assignment.get('id')
        module_id = assignment.get('moduleId')
        name = assignment.get('name', 'Unknown')
        
        if not module_id or module_id not in module_to_course:
            errors.append(f"Assignment {assignment_id} has invalid module reference: {module_id}")
            continue
            
        course_id = module_to_course[module_id]
        
        # Get students in this course
        students_in_course = students_per_course.get(course_id, set())
        expected_submission_count = len(students_in_course)
        
        if expected_submission_count == 0:
            logger.warning(f"Assignment {assignment_id} ({name}) has no expected students")
            continue
            
        # Get actual submissions
        submissions = submissions_by_assignment.get(assignment_id, [])
        actual_submission_count = len(submissions)
        
        # Calculate submission rate
        submission_rate = actual_submission_count / expected_submission_count if expected_submission_count > 0 else 0
        
        # # Log statistics
        # logger.info(
        #     f"Assignment: {assignment_id} ({name}) - "
        #     f"Submissions: {actual_submission_count}/{expected_submission_count} "
        #     f"({submission_rate:.1%})"
        # )
        
        # Calculate late submissions
        late_submissions = 0
        on_time_submissions = 0
        due_date = assignment.get('dueDate')
        
        # if due_date and submissions:
        #     for sub in submissions:
        #         if sub.get('submissionDate') and sub.get('submissionDate') > due_date:
        #             late_submissions += 1
        #         else:
        #             on_time_submissions += 1
                    
        #     late_rate = late_submissions / len(submissions) if submissions else 0
        #     logger.info(
        #         f"  - On-time: {on_time_submissions} ({1-late_rate:.1%}) | "
        #         f"Late: {late_submissions} ({late_rate:.1%})"
        #     )
                    
        # Validate submission rate
        if submission_rate < min_submission_rate:
            errors.append(
                f"Assignment {assignment_id} ({name}) has low submission rate: "
                f"{submission_rate:.1%} (minimum: {min_submission_rate:.1%})"
            )
            logger.info(
                f"  - Low submission rate: {submission_rate:.1%} (minimum: {min_submission_rate:.1%})"
            )
    return errors


def validate_data_consistency(
    data_objects: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, List[str]]:
    """
    Perform comprehensive validation on generated data.
    
    Args:
        data_objects (Dict[str, List[Dict[str, Any]]]): Dictionary of entity lists by type
        
    Returns:
        Dict[str, List[str]]: Dictionary of validation errors by entity type
    """
    validation_errors = {}
    
    # Extract entities by type
    schools = data_objects.get('schools', [])
    teachers = data_objects.get('teachers', [])
    students = data_objects.get('students', [])
    courses = data_objects.get('courses', [])
    modules = data_objects.get('modules', [])
    assignments = data_objects.get('assignments', [])
    
    # Validate school data
    school_errors = validate_required_fields(
        schools, ['id', 'name', 'type', 'location', 'foundingYear']
    )
    if school_errors:
        validation_errors['schools'] = school_errors
    
    # Validate teacher data
    teacher_errors = validate_required_fields(
        teachers, ['id', 'name', 'email', 'schoolId']
    )
    teacher_errors.extend(validate_entity_relationships(
        {school['id'] for school in schools},
        teachers,
        'schoolId'
    ))
    if teacher_errors:
        validation_errors['teachers'] = teacher_errors
    
    # Validate student data
    student_errors = validate_required_fields(
        students, ['id', 'name', 'email', 'schoolId']
    )
    student_errors.extend(validate_entity_relationships(
        {school['id'] for school in schools},
        students,
        'schoolId'
    ))
    if student_errors:
        validation_errors['students'] = student_errors
    
    # Validate course data
    course_errors = validate_required_fields(
        courses, ['id', 'name', 'schoolId', 'startDate', 'endDate']
    )
    course_errors.extend(validate_entity_relationships(
        {school['id'] for school in schools},
        courses,
        'schoolId'
    ))
    course_errors.extend(validate_course_enrollment(courses))
    course_errors.extend(validate_module_counts(courses))
    if course_errors:
        validation_errors['courses'] = course_errors
    
    # Validate module data
    module_errors = validate_required_fields(
        modules, ['id', 'name', 'courseId', 'startDate', 'endDate']
    )
    module_errors.extend(validate_entity_relationships(
        {course['id'] for course in courses},
        modules,
        'courseId'
    ))
    module_errors.extend(validate_assignment_counts(modules))
    if module_errors:
        validation_errors['modules'] = module_errors
    
    # Validate assignment data
    assignment_errors = validate_required_fields(
        assignments, ['id', 'name', 'moduleId', 'assignDate', 'dueDate']
    )
    assignment_errors.extend(validate_entity_relationships(
        {module['id'] for module in modules},
        assignments,
        'moduleId'
    ))
    if assignment_errors:
        validation_errors['assignments'] = assignment_errors
    
    # Build course-to-students mapping for submission rate validation
    students_per_course = {}
    for course in courses:
        course_id = course.get('id')
        students_list = course.get('students', [])
        if isinstance(students_list, list):
            students_per_course[course_id] = set(students_list)
    
    # Also check studentCourses for additional enrollments
    student_courses = data_objects.get('studentCourses', [])
    for sc in student_courses:
        course_id = sc.get('courseId')
        student_id = sc.get('studentId')
        if course_id and student_id:
            if course_id not in students_per_course:
                students_per_course[course_id] = set()
            students_per_course[course_id].add(student_id)
    
    # Validate assignment submission rates
    student_assignments = data_objects.get('studentAssignments', [])
    assignment_submission_errors = validate_assignment_submission_rates(
        assignments, student_assignments, students_per_course, modules
    )
    
    if assignment_submission_errors:
        if 'assignments' not in validation_errors:
            validation_errors['assignments'] = []
        validation_errors['assignments'].extend(assignment_submission_errors)
    
    # Validate student-assignment data
    student_assignments = data_objects.get('studentAssignments', [])
    if student_assignments:
        sa_errors = validate_required_fields(
            student_assignments, ['studentId', 'assignmentId', 'submissionDate', 'assessmentScore']
        )
        sa_errors.extend(validate_entity_relationships(
            {student['id'] for student in students},
            student_assignments,
            'studentId'
        ))
        sa_errors.extend(validate_entity_relationships(
            {assignment['id'] for assignment in assignments},
            student_assignments,
            'assignmentId'
        ))
        sa_errors.extend(validate_score_ranges(student_assignments, 'assessmentScore'))
        if sa_errors:
            validation_errors['studentAssignments'] = sa_errors
    
    # Validate student-course data
    student_courses = data_objects.get('studentCourses', [])
    if student_courses:
        sc_errors = validate_required_fields(
            student_courses, ['studentId', 'courseId', 'finalScore']
        )
        sc_errors.extend(validate_entity_relationships(
            {student['id'] for student in students},
            student_courses,
            'studentId'
        ))
        sc_errors.extend(validate_entity_relationships(
            {course['id'] for course in courses},
            student_courses,
            'courseId'
        ))
        sc_errors.extend(validate_score_ranges(student_courses, 'finalScore'))
        if sc_errors:
            validation_errors['studentCourses'] = sc_errors
    
    # Log validation summary
    total_errors = sum(len(errors) for errors in validation_errors.values())
    if total_errors > 0:
        logger.warning(f"Validation found {total_errors} errors across {len(validation_errors)} entity types")
        for entity_type, errors in validation_errors.items():
            logger.warning(f"{entity_type}: {len(errors)} errors")
    else:
        logger.info("Validation successful: no errors found")
    
    return validation_errors


def log_validation_errors(errors: Dict[str, List[str]]) -> None:
    """
    Log validation errors in a readable format.
    
    Args:
        errors (Dict[str, List[str]]): Dictionary of validation errors by entity type
    """
    if not errors:
        logger.info("No validation errors to log")
        return
    
    total_errors = sum(len(error_list) for error_list in errors.values())
    logger.error(f"Found {total_errors} validation errors:")
    
    for entity_type, error_list in errors.items():
        if error_list:
            logger.error(f"\n{entity_type} ({len(error_list)} errors):")
            for i, error in enumerate(error_list, 1):
                logger.error(f"  {i}. {error}")