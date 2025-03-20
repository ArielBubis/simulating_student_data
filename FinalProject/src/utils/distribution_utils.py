"""
Distribution utilities for generating realistic educational data.
This module provides functions for creating realistic score distributions
that mimic real-world educational grading patterns.
"""
import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple, Union


def generate_skewed_normal(
    mean: float, 
    std_dev: float, 
    skewness: float, 
    min_val: float = 0, 
    max_val: float = 100
) -> float:
    """
    Generate a random value from a skewed normal distribution.
    
    Args:
        mean (float): The mean of the distribution
        std_dev (float): The standard deviation of the distribution
        skewness (float): The skewness parameter (negative for left skew, positive for right skew)
        min_val (float): Minimum allowed value (default: 0)
        max_val (float): Maximum allowed value (default: 100)
        
    Returns:
        float: A random value from the skewed distribution, clipped to the range [min_val, max_val]
    """
    # Generate a normal random value
    normal_value = np.random.normal(0, 1)
    
    # Apply skewness using the sinh-arcsinh transformation
    if skewness != 0:
        normal_value = np.sinh(skewness * np.arcsinh(normal_value))
    
    # Scale and shift to the desired mean and standard deviation
    value = mean + std_dev * normal_value
    
    # Clip to the allowed range
    value = max(min_val, min(max_val, value))
    
    return value


def generate_realistic_grades(
    count: int,
    mean: float = 75.0,
    std_dev: float = 12.0,
    skewness: float = -0.5,
    min_val: float = 0,
    max_val: float = 100
) -> List[float]:
    """
    Generate a list of realistic grades following an educational distribution.
    
    In educational settings, grade distributions often follow a bell curve with
    a slight negative skew (tail toward lower grades).
    
    Args:
        count (int): Number of grades to generate
        mean (float): The average grade (default: 75.0)
        std_dev (float): Standard deviation (default: 12.0)
        skewness (float): Skewness parameter, negative for left skew (default: -0.5)
        min_val (float): Minimum allowed grade (default: 0)
        max_val (float): Maximum allowed grade (default: 100)
        
    Returns:
        List[float]: A list of realistic grades
    """
    return [round(generate_skewed_normal(mean, std_dev, skewness, min_val, max_val), 1) 
            for _ in range(count)]


def generate_consistent_student_performance(
    assignment_count: int,
    base_performance: float,
    consistency: float,
    difficulty_factors: Optional[List[float]] = None,
    mean: float = 75.0,
    std_dev: float = 12.0,
    skewness: float = -0.5
) -> List[float]:
    """
    Generate consistent performance scores for a student across multiple assignments.
    
    This ensures that a student's performance is relatively consistent (with some
    natural variation) across assignments, rather than completely random.
    
    Args:
        assignment_count (int): Number of assignments to generate scores for
        base_performance (float): The student's base performance level (0-100)
        consistency (float): How consistent the student is (0-1), higher means more consistent
        difficulty_factors (Optional[List[float]]): Adjustment factors for assignment difficulty
        mean (float): Base mean for the grade distribution
        std_dev (float): Base standard deviation for the grade distribution
        skewness (float): Base skewness for the grade distribution
        
    Returns:
        List[float]: List of consistent scores for the student
    """
    # If no difficulty factors provided, assume all assignments equal difficulty
    if difficulty_factors is None:
        difficulty_factors = [1.0] * assignment_count
    
    # Ensure we have enough difficulty factors
    difficulty_factors = difficulty_factors[:assignment_count]
    while len(difficulty_factors) < assignment_count:
        difficulty_factors.append(1.0)
    
    # Calculate adjusted mean based on student's base performance
    # This shifts the mean of the distribution based on student ability
    adjusted_mean = mean + (base_performance - 75)
    
    # Generate scores
    scores = []
    for i in range(assignment_count):
        # Adjust standard deviation based on consistency
        # More consistent students have lower standard deviation
        adjusted_std_dev = std_dev * (1 - (consistency / 2))
        
        # Apply difficulty factor to the mean
        # Harder assignments (lower difficulty_factor) result in lower mean
        assignment_mean = adjusted_mean * difficulty_factors[i]
        
        # Generate score
        score = generate_skewed_normal(
            assignment_mean, adjusted_std_dev, skewness, 0, 100
        )
        scores.append(round(score, 1))
    
    return scores


def generate_correlated_subject_performance(
    base_performance: float,
    subject_correlation: float,
    randomness: float = 0.3
) -> float:
    """
    Generate a correlated performance level for a related subject.
    
    Students who are good at one subject are often good at related subjects.
    This function generates a performance level for a related subject
    based on the student's performance in a primary subject.
    
    Args:
        base_performance (float): The student's base performance in the primary subject (0-100)
        subject_correlation (float): Correlation strength between subjects (0-1)
        randomness (float): Amount of random variation to apply (0-1)
        
    Returns:
        float: Correlated performance level for the related subject (0-100)
    """
    # Start with the base performance
    correlated_performance = base_performance
    
    # Add random variation, reduced by the correlation factor
    random_component = (random.random() * 40 - 20) * (1 - subject_correlation) * randomness
    
    # Apply the variation
    correlated_performance += random_component
    
    # Ensure the result is within bounds
    correlated_performance = max(0, min(100, correlated_performance))
    
    return correlated_performance


def calculate_weighted_score(
    scores: List[float],
    weights: Optional[List[float]] = None
) -> float:
    """
    Calculate a weighted average score from individual scores and weights.
    
    Args:
        scores (List[float]): List of individual scores
        weights (Optional[List[float]]): List of weights for each score (must sum to 1.0)
                                        If None, equal weights are used
        
    Returns:
        float: Weighted average score
    """
    if not scores:
        return 0.0
    
    # If no weights provided, use equal weights
    if weights is None:
        weights = [1.0 / len(scores)] * len(scores)
    
    # Ensure we have enough weights
    weights = weights[:len(scores)]
    while len(weights) < len(scores):
        weights.append(0.0)
    
    # Normalize weights to sum to 1.0
    weight_sum = sum(weights)
    if weight_sum > 0:
        weights = [w / weight_sum for w in weights]
    else:
        weights = [1.0 / len(scores)] * len(scores)
    
    # Calculate weighted average
    weighted_sum = sum(score * weight for score, weight in zip(scores, weights))
    
    return round(weighted_sum, 1)


def generate_realistic_time_spent(
    base_time: float,
    student_efficiency: float,
    variability: float = 0.3,
    min_multiplier: float = 0.5,
    max_multiplier: float = 2.0
) -> float:
    """
    Generate a realistic time spent value for a student on an assignment.
    
    Args:
        base_time (float): Base time for the assignment (in minutes)
        student_efficiency (float): Student's efficiency factor (0-1), higher means more efficient
        variability (float): Random variability factor (0-1)
        min_multiplier (float): Minimum time multiplier
        max_multiplier (float): Maximum time multiplier
        
    Returns:
        float: Realistic time spent in minutes
    """
    # Calculate efficiency multiplier (more efficient students take less time)
    efficiency_multiplier = 2.0 - student_efficiency
    
    # Add random variability
    random_factor = 1.0 + (random.random() * 2 - 1) * variability
    
    # Calculate adjusted time
    adjusted_time = base_time * efficiency_multiplier * random_factor
    
    # Ensure time is within reasonable bounds
    adjusted_time = max(base_time * min_multiplier, min(base_time * max_multiplier, adjusted_time))
    
    return round(adjusted_time, 0)


def analyze_grade_distribution(scores: List[float]) -> Dict[str, Any]:
    """
    Analyze a set of scores and return statistics about the distribution.
    
    Args:
        scores (List[float]): List of scores to analyze
        
    Returns:
        Dict[str, Any]: Dictionary containing distribution statistics
    """
    if not scores:
        return {
            "count": 0,
            "mean": 0,
            "median": 0,
            "mode": 0,
            "std_dev": 0,
            "min": 0,
            "max": 0,
            "score_ranges": {}
        }
    
    # Basic statistics
    count = len(scores)
    mean = sum(scores) / count
    median = sorted(scores)[count // 2]
    min_score = min(scores)
    max_score = max(scores)
    
    # Calculate standard deviation
    variance = sum((x - mean) ** 2 for x in scores) / count
    std_dev = variance ** 0.5
    
    # Calculate mode (most common score)
    score_counts = {}
    for score in scores:
        rounded_score = round(score)
        if rounded_score not in score_counts:
            score_counts[rounded_score] = 0
        score_counts[rounded_score] += 1
    
    mode = max(score_counts, key=score_counts.get) if score_counts else 0
    
    # Count scores by range
    score_ranges = {
        "90-100": 0,
        "80-89": 0,
        "70-79": 0,
        "60-69": 0,
        "0-59": 0
    }
    
    for score in scores:
        if score >= 90:
            score_ranges["90-100"] += 1
        elif score >= 80:
            score_ranges["80-89"] += 1
        elif score >= 70:
            score_ranges["70-79"] += 1
        elif score >= 60:
            score_ranges["60-69"] += 1
        else:
            score_ranges["0-59"] += 1
    
    return {
        "count": count,
        "mean": round(mean, 2),
        "median": median,
        "mode": mode,
        "std_dev": round(std_dev, 2),
        "min": min_score,
        "max": max_score,
        "score_ranges": score_ranges
    }