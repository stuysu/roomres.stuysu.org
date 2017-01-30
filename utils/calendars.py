from random import randrange
import datetime
from calendar import monthrange


"""
Makes a calendar - dictionary
Args:
    day - day of the week
    date - date of the month
    num - 0 = current; 1 = next moneth
Returns:
    dictionary in day: [dates] format
"""
def calendardict(i):
    d={}
    today = str(datetime.date.today())
    month = int(today.split('-')[1])
    year = int(today.split('-')[0])
    if i == 0:
        now = list(monthrange(year, month)) # returns [weekday of first day, number of days]
    if i == 1:
        if month == 12:
            year +=1
            month = 1
        else:
            month += 1
        now = list(monthrange(year, month))
    currPos = 0
    date = 1
    L = []
    tempL = []
    if now[0] != currPos:
        while currPos < 7:
            if date < 2 and now[0] != currPos:
                tempL += [0]
            else:
                if date < 10:
                    dat = " " + str(date)
                    tempL += [dat]
                else:
                    tempL += [date]  
                date += 1
            currPos += 1
        L += [tempL]

    tempL = []
    while date < now[1] + 1:
        if len(tempL) == 7:
            L += [tempL]
            tempL = []
        else:
            print "date: "
            if date < 10:
                dat = " " + str(date)
                tempL += [dat]
            else:
                tempL += [date]
            date +=1
    L += [tempL]
    print L
    return L

