from passlib.context import CryptContext
from controllers.exceptions import authError, validationError
from models import db, users
import sqlite3

#cryptcontext configured to bcrypt
pwdContext=CryptContext(schemes=["bcrypt"], deprecated="auto")

#session tracker, stores logged in user id
currentUser=None

#hash password with bcrypt; salt is generated automatically
def hashPassword(password:str)->str:
    return pwdContext.hash(password)

#verify if bcrypt(hashed+salt) password works
def verifyPassword(plainPassword:str, hashedPassword:str)->bool:
    return pwdContext.verify(plainPassword,hashedPassword)

#check duplicate entry 
def checkDuplicateEmail(conn:sqlite3.connection, email: str) -> None:
    existingUser = users.get_user_by_email(conn, email)

    if existingUser is not None:
        raise authError(f"User with email {email} already exists")

#basic signup prompt
def sign_up(email:str, password:str)-> int:

    global currentUser

    #frontend prompt logic
    if not email or "@" not in email: 
        raise validationError("Email address required")

    if not password or len(password)<8:
        raise validationError("Password must be atleast 8 characters long")

    #change email to lowercase and remove whitespaces to store same format in db
    normalizedEmail=email.strip().lower()

    conn=db.get_connection()#get connection from sqlite
    
    try:
        #check if the user already exists
        checkDuplicateEmail(conn, normalizedEmail)

        #hash current password, and create new user, storing it in the db
        hashed=hashPassword(password)
        currentUser=users.create_user(conn, email=normalizedEmail, password_hash=hashed)

        return currentUser
    
    finally: #close connection #use finally so that it still executes after error is raised
        conn.close()


#basic login prompt
def log_in(email: str, password: str)->int:
    global currentUser

    if not email or not password:
        raise validationError("Email and password cannot be empty")

    normalized_email= email.strip().lower()

    conn=db.get_connection()
    try:
        existingUser= users.get_user_by_email(conn,normalized_email)
        if existingUser is None:
            raise authError("Invalid email or password.")

        # verify bcrypt hash
        if not verifyPassword(password, existingUser["password_hash"]):
            raise authError("Invalid email or password")

        #update session
        currentUser = existingUser["id"]
        return currentUser
    
    finally:
        conn.close()


#basic logout prompt
def logout()-> None:
    global currentUser

    currentUser=None

#getter for current user
def getCurrentuser():
    return currentUser