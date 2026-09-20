from passlib.context import CryptContext
from controllers.exceptions import authError, validationError
from models.fake_models import getUser_by_email, createUser

#cryptcontext configured to bcrypt
pwdContext=CryptContext(schemes=["bcrypt"], deprecated="auto")

#session tracker, user dict
currentUser=None

#hash function with automatic salt generation (necessary for password encryption)
def hashPassword(password:str)->str:
    return pwdContext.hash(password)

#verify if bcrypt(hashed+salt) password works
def verifyPassword(plainPassword:str, hashedPassword:str)->bool:
    return pwdContext.verify(plainPassword,hashedPassword)

#basic signup prompt
def sign_up(email:str, password:str)-> dict:
    global currentUser #saves the user 

    #frontend prompt logic
    if not email or "@" not in email: 
        raise validationError("Email address required")

    if not password or len(password)<8:
        raise validationError("Password must be atleast 8 characters long")

    #change email to lowercase and remove whitespaces to store same format in db
    normalizedEmail=email.strip().lower()

    #check if the user already exists
    existingUser=getUser_by_email(normalizedEmail)
    if existingUser is not None:
        raise authError(f"User with email {normalizedEmail} already exists")

    #hash current password, and create new user, storing it in the db
    hashed=hashPassword(password)
    currentUser=createUser(email=normalizedEmail, password_hashed=hashed)

    return currentUser


#basic login prompt
def log_in(email: str, password: str)->dict:
    global currentUser

    if not email or not password:
        raise validationError("Email and password cannot be empty")

    normalized_email= email.strip().lower()

    existingUser= getUser_by_email(normalized_email)
    if existingUser is None:
        raise authError("Invalid email or password.")

    # verify bcrypt hash
    if not verifyPassword(password, existingUser["password_hash"]):
        raise authError("Invalid email or password")

    #update session
    currentUser= existingUser
    return existingUser


#basic logout prompt
def logout()-> None:
    global currentUser

    currentUser=None

#getter for current user
def getCurrentuser():
    return currentUser