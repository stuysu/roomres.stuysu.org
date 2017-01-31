from sqlite3 import connect
from hashlib import sha1
from os import urandom
from random import randrange
import datetime
import calendar
from calendar import monthrange


f = "data/roomres.db"

'''
---------------------------------------
Find list of values functions
----------------------------------------
'''


def cursorToList(c):
    items = c.fetchall()
    books = []
    for item in items:
        book = []
        for info in item:
            book.append(str(info))
        books.append(book)
    return books

def find():
    checkCreateTable()
    db = connect(f)
    c = db.cursor()
    c.execute("SELECT * from rooms")
    a = c
    l = cursorToList(a)
    db.close()
    return l

def findP(field,value):
    db = connect(f)
    c = db.cursor()
    if type(value) is int:
        c.execute("SELECT * from rooms WHERE %s = %d" % (field,value))
    elif type(value) is str or type(value) is unicode:
        c.execute("SELECT * from rooms WHERE %s = \"%s\"" % (field,value))
    else:
        print "error: "
        print type(value)
        c.execute("SELECT * from rooms")
    a = c
    l =  cursorToList(a)
    db.close()
    return l


def findBooked():
    db = connect(f)
    c = db.cursor()
    c.execute("SELECT * from rooms WHERE club!=\"\"")
    a = c
    l =  cursorToList(a)
    db.close()
    return l


def findUnbooked(field,value):
    db = connect(f)
    c = db.cursor()
    c.execute("SELECT * from rooms WHERE date = \"%s\" AND club=\"\"" % (value))
    a = c
    l = cursorToList(a)
    db.close()
    return l


'''
------------------------------
UPDATE DB FUNCTIONS
------------------------------
'''

def checkCreateTable():
    db = connect(f)
    c = db.cursor()
    try:
        c.execute("SELECT * FROM rooms")
    except:
        c.execute("CREATE TABLE rooms (club TEXT, email TEXT, room INT, date TEXT, weekday TEXT, time TEXT)");
    db.commit()
    db.close()

    
def booked(date, room):
    db = connect(f)
    c = db.cursor()
    query = "SELECT date, room FROM rooms WHERE date=? AND room=? AND club!=\"\""
    info = c.execute(query, (date, room))
    value = False
    for record in info:
         value = True
    db.commit()
    db.close()
    return value

def addBook(email, date, room):

    print "HEYYYY"
    print email,date,room
    
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
    msg = "Sorry, " + str(room) + "  is booked on " + date
    if not booked(date, room):

         try:
             query = ("SELECT * from users WHERE email=?")
             c.execute(query,(email,))
             club = c.fetchall()[0][5]
         except:
             club = "N/A"
             
         now = datetime.datetime.now()
         time = now.strftime("%H:%M")
         #weekday = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A')
         #print date
         #print time

         '''
         print "club:"
         print club
         print "email:"
         print email
         '''

         query = ("UPDATE rooms SET club=? , email=?, time=? WHERE room=? and date=?")
         c.execute(query, (club, email, time,room,date))
         
         msg =  (club + " has now booked " + str(room) + " on " + date)
    db.commit()
    db.close()
    return msg



def getFirstWeekdayDate(month, weekday):
    dayDict = {}
    dayDict["Monday"] = 0
    dayDict["Tuesday"] = 1
    dayDict["Wednesday"] = 2
    dayDict["Thursday"] = 3
    dayDict["Friday"] = 4
    dayDict["Saturday"] = 5
    dayDict["Sunday"] = 6

    cal = calendar.Calendar(0)
    mon = cal.monthdatescalendar(datetime.datetime.now().year,int(month))
    firstweek = mon[0]
    
    day = firstweek[dayDict[weekday]]
    if day.month != month:
        day = mon[1][dayDict[weekday]]
    
    return day.day


def adminAddRoom(room, month, day):

    
    if room == None or room == "":
        return "One or more fields was not filled"
    
    if int(room) < 101 or int(room) > 1030:
        return "Room does not exist!!!"

    month = int(month)
    
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
           
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")

    club = ""
    mDays = calendar.monthrange(2017,int(month))[1]
    fDay = getFirstWeekdayDate(month, day)

    monthStr = str(month)
    if month < 10:
        monthStr = "0" + monthStr

    print fDay, mDays
        
    while fDay <= mDays:
        fDayStr = str(fDay)
        if (fDay < 10):
            fDayStr = "0" + fDayStr
            
        date = str(now.year) + "-" + str(monthStr) + "-" + str(fDayStr)
        query = ("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?)")
        c.execute(query, (club, "admin", room, date, day, time))
        fDay+=7
         
    db.commit()
    db.close()
    return "Put room for booking up"


def removeBook(room, date):
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
    msg = str(room) + " is actually now booked on " + date
    if booked(date, room):
        query = "UPDATE rooms SET club=\"\", email=\"admin\" WHERE date=? and room=?"     
        c.execute(query, (date, room))
        msg =  str(room) + " is now available on " + date 
    db.commit()
    db.close()
    return msg

def changeBook(date,room,newr,club):

    if newr == "" or newr == None:
        return "new room empty"
    
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
    query = "UPDATE rooms SET room=? WHERE date=? and room=? and club=?"
    c.execute(query, (newr,date,room,club))
    db.commit()
    db.close()
    return "change success"
    
#change date to day and month
def adminRemoveRoom(room, month, day):
    
    if room == None or room == "":
        return "One or more fields was not filled"
    
    if int(room) < 101 or int(room) > 1030:
        return "Room does not exist!!!"

    month = int(month)
    
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
           
    now = datetime.datetime.now()
    time = now.strftime("%H:%M")

    mDays = calendar.monthrange(2017,int(month))[1]
    fDay = getFirstWeekdayDate(month, day)

    monthStr = str(month)
    if month < 10:
        monthStr = "0" + monthStr
             
    while fDay <= mDays:
        fDayStr = str(fDay)
        if (fDay < 10):
            fDayStr = "0" + fDayStr
            
        date = str(now.year) + "-" + str(monthStr) + "-" + str(fDayStr)

        query = "DELETE from rooms where date=? and room=?"
        c.execute(query,(date,room))
        
        fDay+=7
         
    db.commit()
    db.close()
    return "Remove room for booking"


if __name__=="__main__":
    print "check"
    #addBook("test@example.com",  "2016-01-29", 235)


    
