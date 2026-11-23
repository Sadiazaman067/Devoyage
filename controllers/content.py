from exceptions import ValidationError
from models import db, career_paths, resources

#valid resource categories from spec
validCategories=("learning", "practice", "tools", "communities", "career")


#fetch all seeded career paths from db
def list_career_paths()->list:
    conn=db.get_connection()#get connection from sqlite
    try:
        return career_paths.list_career_paths(conn)
    finally:#close connection even if error is raised
        conn.close()


#fetch seeded resources from db, filter by category if passed
def list_resources(category:str=None)->list:
    if category is not None and category not in validCategories:
        raise ValidationError("Unknown resource category.")

    conn=db.get_connection()
    try:
        return resources.list_resources(conn, category=category)
    finally:
        conn.close()