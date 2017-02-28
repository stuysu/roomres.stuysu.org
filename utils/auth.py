from sqlite3 import connect
from hashlib import sha1
from os import urandom
import random,string

f = "data/roomres.db"
db = connect(f)
c = db.cursor()

def login(email, password):
    db = connect(f)
    c = db.cursor()

    try:
        c.execute("SELECT * FROM USERS")
    except:
        c.execute("CREATE TABLE users (userID INT, email TEXT, osis INT, salt TEXT, password TEXT, club TEXT)")

    query = ("SELECT * FROM users WHERE email=?")
    info = c.execute(query,(email,))

    for record in info:
        password = sha1(password+record[3]).hexdigest() #record[3] is the salt
        if (password==record[4]):
            return ""#no error message
        else:
            return "User login has failed. Invalid password"#error message
        db.commit()
        db.close()
    return "Username does not exist"#error message

def register(club, osis, email, ps1, ps2):
    if not ps1 == ps2:
        return "Passwords not the same."
    #db = connect(f)
    #c = db.cursor()
    #try:
    #    c.execute("SELECT * FROM USERS")
    #except:
    #    c.execute("CREATE TABLE users (userID INT, email TEXT, osis INT, salt TEXT, password TEXT, club TEXT)")
    #    db.commit()
    #    db.close()
    return regMain(club, osis, email, ps1)#register helper

def getSize():
    db = connect(f)
    c = db.cursor()
    num = c.execute("SELECT COUNT(*) FROM USERS")
    size = 0
    for record in num:
        size = record[0]
    db.commit()
    db.close()
    return size

def regMain(club, osis, email, password):#register helper
    db = connect(f, timeout=10)
    c = db.cursor()
    reg = errorMsg(email, password)
    if reg == "": #if error message is blank then theres no problem, update database
        salt = urandom(10).encode('hex')
        #print salt
        query = ("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)")
        password = sha1(password + salt).hexdigest()
        userID = getSize()+1
        c.execute(query, (userID, email, int(osis), salt, password, club))
        db.commit()
        db.close()
        return "Account created!"
    db.commit()
    db.close()
    return reg

def changepwd(email,old,new,new2):
    if new != new2:
        return "New passwords are not identical"
    if len(new) < 8:
        return "Passwords must be greater than 8 characters"
    if old == new:
        return "Old and new passwords are the same"
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE email=?")
    sel = c.execute(query, (email,))
    for record in sel:
        print record
        oldP = sha1(old+record[3]).hexdigest() #record[3] is the salt
        if record[4] == oldP:
            salt = urandom(10).encode('hex')
            password = sha1(new + salt).hexdigest()
            
            query = ("UPDATE users SET password=?, salt=? WHERE email=?")
            c.execute(query, (password,salt,email))
            db.commit()
            db.close()
            return "Password successfully changed"
        
        return "Incorrect old password"
    return "unexpected error"

def errorMsg(email, password):      #error message generator
    if '@' not in email:
        return "Please enter a valid email."
    if duplicate(email):
        return "User account already exists"
    if " " in email or " " in password:
        return "Spaces not allowed in email or password"
    if len(password) < 8:
        return "Passwords must be greater than 8 characters"
    return ""

def duplicate(email):#checks if username already exists
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE email=?")
    sel = c.execute(query, (email,))
    value = False
    for record in sel:
        value = True
    db.commit()
    db.close()
    return value


def admin_resetpwd(email):
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE email=?")
    sel = c.execute(query, (email,))
    for record in sel:

        new = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        salt = urandom(10).encode('hex')
        password = sha1(new + salt).hexdigest()
        
        
        query = ("UPDATE users SET password=?, salt=? WHERE email=?")
        c.execute(query, (password,salt,email))
        db.commit()
        db.close()

        return new
    
    return "Email does not exist in database!"
