from sqlite3 import connect
from hashlib import sha1
from os import urandom
from random import randrange
import datetime
from calendar import monthrange


f = "../data/roomres.db"
db = connect(f)
c = db.cursor()

'''
---------------------------------------
Find list of values functions
----------------------------------------
'''

def find():
    checkCreateTable()
    return c.fetchall()

def findP(field,value):
    if type(value) is int:
        c.execute("SELECT * from rooms WHERE %s = %d" % (field,value))
    elif type(value) is str:
        c.execute("SELECT * from rooms WHERE %s = \"%s\"" % (field,value))
    else:
        c.execute("SELECT * from rooms")
    return c.fetchall()


'''
------------------------------
UPDATE DB FUNCTIONS
------------------------------
'''

#queries is a dictionary or list?

def updateDB(queries,parameter,newEntry):
    return None

def checkCreateTable():
     db = connect(f)
     c = db.cursor()
     try:
          c.execute("SELECT * FROM rooms")
     except:
          c.execute("CREATE TABLE rooms (club TEXT, email TEXT, room INT, data TEXT, time TEXT)");
     db.commit()
     db.close()

def booked(email, room):
     db = connect(f)
     c = db.cursor()
     query = "SELECT email, room FROM rooms WHERE email=? and room=?"
     info = c.execute(query, (email, room))
     value = False
     for record in info:
          value = True
     db.commit()
     db.close()
     return value

def bookRoom(club, email, room):
     db = connect(f)
     c = db.cursor()
     checkCreateTable()
     if not booked(email, room):
         now = datetime.datetime.now()
         date = now.strftime("%Y-%m-%d")
         time = now.strftime("%H:%M")
         #print date
         #print time
         query = ("INSERT INTO rooms VALUES (?, ?, ?, ?, ?)")
         c.execute(query, (club, email, room, date, time))
     db.commit()
     db.close()



"""
Adds rooms to room list 5 at a time
Args:
  r<n>: room number
Return:
  True if succeded
  False if not
"""

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

if __name__=="__main__":
    bookRoom("RoadRunners", "test@example.com", 235)
