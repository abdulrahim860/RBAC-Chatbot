def assign_roles(file_path: str) -> dict:
    file_path = file_path.lower()

    roles = ["general", "C_level", "employee"]

    if "engineering" in file_path:
        roles = ["engineering", "C_level"]
    elif "hr" in file_path:
        roles = ["hr", "C_level"]
    elif "marketing" in file_path:
        roles = ["marketing", "C_level"]
    elif "finance" in file_path:
        roles = ["finance", "C_level"]

    return {f"role_{role}": True for role in roles}
