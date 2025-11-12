"""
Utility functions for role-based access control (RBAC) and data management.
"""
import pandas as pd
import os


def load_student_data(data_path="data/students_data.csv"):
    """
    Load student data from CSV file.
    
    Args:
        data_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded student data
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    df = pd.read_csv(data_path)
    # Convert date column to datetime for easier filtering
    df['date'] = pd.to_datetime(df['date'])
    return df


def get_filtered_data(user_role, data_path="data/students_data.csv"):
    """
    Filter student data based on user role (RBAC).
    
    Admins can only see data from their assigned class and region.
    
    Args:
        user_role (dict): Dictionary containing user role information
            Expected keys: 'username', 'assigned_class', 'region'
        data_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Filtered dataframe based on user permissions
        
    Example:
        user_role = {
            "username": "Roshni_Admin",
            "assigned_class": 8,
            "region": "North"
        }
    """
    # Load the full dataset
    df = load_student_data(data_path)
    
    # Extract user permissions
    assigned_class = user_role.get('assigned_class')
    region = user_role.get('region')
    
    # Apply role-based filtering
    if assigned_class is not None and region is not None:
        # Filter by both class and region
        filtered_df = df[(df['class'] == assigned_class) & (df['region'] == region)]
    elif assigned_class is not None:
        # Filter by class only
        filtered_df = df[df['class'] == assigned_class]
    elif region is not None:
        # Filter by region only
        filtered_df = df[df['region'] == region]
    else:
        # Super admin - no filtering (can see all data)
        filtered_df = df
    
    return filtered_df


def validate_user_role(user_role):
    """
    Validate that user role dictionary has required fields.
    
    Args:
        user_role (dict): User role dictionary to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(user_role, dict):
        return False, "User role must be a dictionary"
    
    if 'username' not in user_role:
        return False, "User role must contain 'username'"
    
    # At least one permission field should be present
    if 'assigned_class' not in user_role and 'region' not in user_role:
        return False, "User role must contain at least 'assigned_class' or 'region'"
    
    return True, None


def get_available_classes(data_path="data/students_data.csv"):
    """
    Get list of unique classes from the dataset.
    
    Returns:
        list: Sorted list of unique class values
    """
    df = load_student_data(data_path)
    return sorted(df['class'].unique().tolist())


def get_available_regions(data_path="data/students_data.csv"):
    """
    Get list of unique regions from the dataset.
    
    Returns:
        list: Sorted list of unique region values
    """
    df = load_student_data(data_path)
    return sorted(df['region'].unique().tolist())
