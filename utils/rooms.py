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
    l = cursorToList(c)
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
    l =  cursorToList(c)
    db.close()
    return l



def findUnbooked(field,value):
    print "check"
    print value
    db = connect(f)
    c = db.cursor()
    if type(value) is int:
        c.execute("SELECT * from rooms WHERE %s = %d AND club=\"\"" % (field,value))
    elif type(value) is str or type(value) is unicode:
        c.execute("SELECT * from rooms WHERE %s = \"%s\" AND club=\"\"" % (field,value))
    else:
        print "error: "
        print type(value)
        c.execute("SELECT * from rooms")
    l =  cursorToList(c)
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
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
    msg = "Sorry, " + str(room) + "  is booked on " + date
    if not booked(date, room):
         query = ("SELECT * from users WHERE email=?")
         print email
         print(query,(email))
         c.execute(query,(email,))
         club = c.fetchall()[0][5]
         
         now = datetime.datetime.now()
         time = now.strftime("%H:%M")
         weekday = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A')
         #print date
         #print time

         print "club:"
         print club
         print "email:"
         print email

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

    return day.day


def adminAddRooms(room, month, day):
    
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
        query = "DELETE FROM rooms WHERE date=? and room=?"
        c.execute(query, (date, room))
        msg =  str(room) + " is now available on " + date 
    db.commit()
    db.close()
    return msg

def changeBook(date,room,newr,club):
    db = connect(f)
    c = db.cursor()
    checkCreateTable()
    query = "UPDATE rooms SET room=? WHERE date=? and room=? and club=?"
    c.execute(query, (newr,date,room,club))
    db.commit()
    db.close()
    


####
#OLD MONGODB BASED FUNCTIONS
    
"""
Adds rooms to room list 5 at a time
Args:
  r<n>: room number
Return:
  True if succeded
  False if not
"""

'''

def add_room(l):
    for room in l:
        check = list(db.rooms.find({'room': room}))

        today = str(datetime.date.today())
        month = str(today.split('-')[1])
        year = str(today.split('-')[0])
        date = year + '-' + month + '-'
        month2 = str((int(month)+1)%12)
        if month=="12":
            year2=str(int(year)+1)
        date2 = year2 + '-' + month2 + '-'

        d = 1

        if  len(room)>2 and check == []:
            while d < 32:
                t = {'day': date + str(d) , 'room':room, 'club': ''}
                t2 = {'day': date2 + str(d) , 'room':room, 'club': ''}
                d+=1
                db.rooms.insert(t)
                db.rooms.insert(t2)

"""
adds club name to end of date-room-club
Args:
    d = date
    r = room #
    e = club name
Return:
  True if succeded
  False if not
"""
def book_room(d, r, e):
    check = list(db.rooms.find({'day': d}))
    email(e, "Room Booking", "You are now booked for " + str(r) + " on " + str(d) )
    if check != []:
        db.rooms.update(
            {
                'day': d,
                'room' : r
            },
            {'$set':
             {
                 "club": e
             }
         }
         )
        return True


"""
*admin usage only
change room number of a club
Args:
    d = date
    r = room #
    c = club number
    r2 = new room #
Return:
  True if succeded
  False if not
"""
def change_room(d, r, r2, c):
    #check = list(db.rooms.find({'day': d}))
    check = list(findP("day",d))
    if check != []:
        db.rooms.update(
            {
                'day': d,
                'club': c,
                'room': r
            },
            {'$set':
             {
                 'room' : r2
             }
         }
         )
        book_room(d, r, c)
        email(c, "Booking Changed", "Sorry for the inconvenience, but because of faculty requests, your room booking on " + d + " is now in room " + r2)
        return True



def del_room(d, r, c):
    #check = list(db.rooms.find({'day': d}))
    check = list(findP("day",d))
    if check != []:
        # Find entry with query of day = d and room = r
        # Of that entry, set club to ''
        db.rooms.update(
            {
                'day': d,
                'room' : r
            },
            {'$set':
             {
                 "club": ''
             }
         }
         )
        email(c, "Booking Cancelled", "Your room booking on " + d + " is now cancelled")
        return True



def takeoff_room(r):
    #check = list(db.rooms.find({'room': r}))
    check = list(findP("room",r))
    if check != []:
        collection.remove({'room' : r})
        return True
    return False



"""
Finds club name with email.
Args:
    email - club user email address
Returns:
    True if club exist
    False if club does not exist
"""
def find_club(email):
    #name =  list(db.users.find({'email':email}))
    name =  list(findP("email",email))
    if name != []:
        return name[0]['name']
    return False

db.commit()
db.close()
'''


if __name__=="__main__":
    addBook("test@example.com",  "2016-01-29", 235)

