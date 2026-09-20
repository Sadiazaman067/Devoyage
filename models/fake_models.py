#fake database for testing later

users_db={} #main db storing {int id: user({int id, email, password...})- JSON format
next_id=1 #id is linear/consecutive for fake db, increases by one for each new user

def getUser_by_email(email:str): #checks only existing user by email
    #scan dict for existing user from the given email
    global users_db

    for uid, user in users_db.items():
        if user["email"]==email:
            return user
    return None

def createUser(email: str, password_hashed:str)->int: #inserts new record in database
    global users_db
    global next_id

    userRecord={
        "id": next_id,
        "email": email,
        "password_hash": password_hashed}
    
    users_db[next_id]=userRecord
    next_id+=1

    return userRecord

def reset_db():
    """Clear in-memory storage for clean test runs."""
    global users_db, next_id
    users_db = {}
    next_id = 1
