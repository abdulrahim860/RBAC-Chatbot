# Function to assign access roles based on the file path
def assign_roles(file_path: str) -> dict:
    file_path = file_path.lower()
    
    # Default roles if no specific department is matched
    roles = ["general", "C_level", "employee"]

    # Assign specific roles based on keywords in the file path
    if "engineering" in file_path:
        roles = ["engineering", "C_level"]
    elif "hr" in file_path:
        roles = ["hr", "C_level"]
    elif "marketing" in file_path:
        roles = ["marketing", "C_level"]
    elif "finance" in file_path:
        roles = ["finance", "C_level"]

    return {f"role_{role}": True for role in roles}