from flask import Flask, render_template, request, session, redirect, url_for
from utils import auth, calendars, rooms
import json
import calendar
import datetime

app = Flask(__name__)
app.secret_key = 'dogsrcool'


# GIVES VALUE FOR INDEX.HTML TO USE
def userOut():
    if 'logged_in' in session:
        return False
    return True


'''
---------------------------
NOT LOGGED IN
---------------------------
'''

@app.route('/')
def root():
    if 'logged_in' in session:
        if session['type'] == 'club':
            return redirect(url_for("dashboard"))
        elif session['type'] == 'admin':
            return redirect(url_for("adview"))
        elif session['type'] == 'administrator':
            return redirect(url_for("administrationview"))
        else:
            print session['type']
            return "You broke the page!"
    return render_template("index.html",out=userOut())

@app.route("/signup", methods=["GET", "POST"])
def signup():
    print ("hello")
    if request.method == "POST":
        name = request.form['name']  #club name
        email = request.form["email"]
        pwd1 = request.form["pwd"]
        pwd2 = request.form["pwd2"]
        osis = request.form["osis"]
        msg = auth.register(name,osis,email,pwd1,pwd2)
        try:
            osis = int(osis)
        except:
            osis = None
        if msg == "Account created!":
            return redirect(url_for("login"))
        else:
            print "Message: " + msg
            return render_template("signup.html",message=msg,out=userOut())
    else:
        return render_template("signup.html",message="",out=userOut())


@app.route("/login", methods=["GET", "POST"])
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html",message="",out=userOut())
    else:
        email = request.form['email']
        pwd = request.form['pwd']
        msg = auth.login(email,pwd)
        if len(msg) == 0:
            session['logged_in'] = True
            session['email'] = email
            session['pwd'] = pwd
            session['type'] = 'club'
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html",message=msg,out=userOut())


@app.route("/changepwd", methods=["GET", "POST"])
@app.route("/changepwd/", methods=["GET", "POST"])
def changepwd():
    if request.method == "GET":
        return render_template("changepwd.html",out=userOut(),message="")
    else:
        old = request.form['old_pwd']
        new = request.form['new_pwd']
        new2 = request.form['new_pwd_2']
        msg = auth.changepwd(session['email'],old,new,new2)
        print msg
        return render_template("changepwd.html",message=msg)


@app.route("/logout", methods=["GET"])
@app.route("/logout/", methods=["GET"])
def logout():
    session['logged_in'] = False
    session.pop('email')
    session.pop('pwd')
    session.pop('logged_in')
    session.pop('type')
    return redirect(url_for("root"))


'''
------------------------------
USER LOGGED IN
------------------------------
'''

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for("root"))
    
    cal = calendars.calendardict(0)
    if request.method=="GET":
        return render_template("dashboard.html", L = cal, message=0,out=userOut(), G="")
    else:
        d = request.form["day"]
        if len(d)< 3:
            session['day'] = d
            today = datetime.date.today()
            month = today.month
            if month < 10:
                month = "0" + str(month)
            else:
                month = str(month)
            year = str(today.year)
                
            date =  year+"-" +month+'-'+d
            session['day'] = date
            check = rooms.findUnbooked("date",date)
            return render_template("dashboard.html", L = cal, G = check, message=0,out=userOut())
        else:
            r = request.form['room']
            rooms.addBook(session['email'],d,r)
            return redirect(url_for("view"))


@app.route("/dashnext", methods=["GET", "POST"])
def dashnext():
    if 'logged_in' not in session:
        return redirect(url_for("root"))
    cal = calendars.calendardict(1)
    if request.method=="GET":
        return render_template("dashboard.html", L = cal, message=1,out=userOut(), G="")
    else:
        d = request.form["day"]
        
        if len(d)< 3:
            today = datetime.date.today()
            month = today.month+1
            if month < 10:
                month = "0" + str(month)
            else:
                month = str(month)
            year = str(today.year)
                
            date =  year+"-" +month+'-'+d                   
            session['day'] = date
            check = rooms.findUnbooked("date",date)
            return render_template("dashboard.html", L = cal, message=1,out=userOut(),G=check)
        else:
            r = request.form['room']
            msg = rooms.addBook(session['email'],d,r)
            #Use jinja to add a message to show success
            return redirect(url_for("view"))
            #return "You've booked " + session['room'] + " for " + session['day'] + "!"


@app.route("/view", methods=["GET", "POST"])
def view():
    if 'logged_in' not in session:
        return redirect(url_for("root"))
    if request.method=="GET":
        check = rooms.findP("email",session["email"])
        today = str(datetime.date.today())
        month = str(today.split('-')[1])
        return render_template("view.html", L = check,out=userOut())
    else:
        info = request.form['del']
        day = info.split(',')[0]
        room = info.split(',')[1]
        club = info.split(',')[2]
        msg = rooms.removeBook(room,day)
        #message add
        return redirect(url_for("view"))



'''
-------------------------------------------
ADMIN ROUTES
-------------------------------------------
'''

@app.route("/adlogin", methods=["GET", "POST"])
@app.route("/adlogin/", methods=["GET", "POST"])
def adlogin():
    if request.method == "GET":
        return render_template("login.html",message="",out=userOut())
    else:
        email = request.form['email']
        pwd = request.form['pwd']

        if (email=="admin" or email=="administration") and pwd=="":
            session['logged_in'] = True
            session['email'] = email
            session['pwd'] = pwd
            if email=="admin":
                session['type'] = 'admin'
                return redirect(url_for("adview"))
            else:
                session['type'] = 'administration'
                return redirect(url_for("administrationview"))
        return render_template("login.html",message="Failed login",out=userOut())


@app.route("/adviewall", methods=['GET','POST'])
def adviewall():
    if request.method == "GET" and "type" in session and session["type"] == "admin":
        check = rooms.find()
        return render_template("adview.html", L = sorted(check, key=lambda k: k[4]),out=userOut())
    return redirect("/")

@app.route("/adview", methods=["GET", "POST"])
def adview():
    if 'logged_in' not in session:
        return redirect("/")
    if request.method=="POST":
        if "del" in request.form:
            info = request.form['del']
            day = info.split(',')[0]
            room = info.split(',')[1]
            club = info.split(',')[2]
            msg = rooms.removeBook(room, day)
        elif 'book' in request.form:
            rooms.addBook(request.form["email"],request.form["date"],request.form["room"])
            return redirect(url_for("adview"))
        else:
            info = request.form['change']
            day = info.split(',')[0]
            room = info.split(',')[1]
            club = info.split(',')[2]
            newr = request.form['newr']
            msg = rooms.changeBook(day, room, newr, club)
        #message add
        return redirect(url_for("adview"))
    if request.method == "GET":
        rooms.checkCreateTable()
        check = rooms.findBooked()
        return render_template("adview.html", L = sorted(check, key=lambda k: k[4]),out=userOut())
    

@app.route("/administrationview", methods=["GET"])
def administrationview():
    if 'logged_in' not in session:
        return redirect("/")
    check = rooms.findBooked()
    return render_template("damesek.html", L=sorted(check, key=lambda k: k[4]),out=userOut()) #k[4] is day

@app.route("/ad_resetpwd", methods=["GET","POST"])
@app.route("/ad_resetpwd/", methods=["GET","POST"])
def ad_changepwd():
    if request.method=="GET":
        return render_template("ad_resetpwd.html",message="")
    else:
        email = request.form["email"]
        temp_pass = auth.admin_resetpwd(email)
        good = True
        if temp_pass == "Email does not exist in database!":
            msg = "Password reset failed! " + temp_pass
            good = False
        else:
            msg = "Password for %s successfully changed! The new temporary password is:" % (email)
        return render_template("ad_resetpwd.html",message=msg,success = good,newP = temp_pass)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method=="GET":
        return render_template("add.html",out=userOut()) 
    else:
        
        choices = []
        choices.append(request.form["room1"]) 
        choices.append(request.form["room2"]) 
        choices.append(request.form["room3"])
        choices.append(request.form["room4"])
        choices.append(request.form["room5"]) 

        months = []
        months.append(request.form["month1"])
        months.append(request.form["month2"])
        months.append(request.form["month3"])
        months.append(request.form["month4"])
        months.append(request.form["month5"])
        
        days = []
        days.append(str(request.form["day1"]))
        days.append(str(request.form["day2"]))
        days.append(str(request.form["day3"]))
        days.append(str(request.form["day4"]))
        days.append(str(request.form["day5"]))

        
        i = 0
        while i < 5:
            if choices[i] != None and choices[i] != "":
                rooms.adminAddRoom(choices[i],months[i],days[i])
            i+=1

        #how do we handle multiple messages here?
        
        return redirect(url_for("add"))



@app.route("/del", methods=["GET", "POST"])
def dele():
    if request.method=="GET":
        return render_template("del.html",out=userOut())
    else:

        choices = []
        choices.append(request.form["room1"]) 
        choices.append(request.form["room2"]) 
        choices.append(request.form["room3"])
        choices.append(request.form["room4"])
        choices.append(request.form["room5"]) 

        months = []
        months.append(request.form["month1"])
        months.append(request.form["month2"])
        months.append(request.form["month3"])
        months.append(request.form["month4"])
        months.append(request.form["month5"])
        
        days = []
        days.append(str(request.form["day1"]))
        days.append(str(request.form["day2"]))
        days.append(str(request.form["day3"]))
        days.append(str(request.form["day4"]))
        days.append(str(request.form["day5"]))

        
        i = 0
        while i < 5:
            if choices[i] != None and choices[i] != "":
                rooms.adminRemoveRoom(choices[i],months[i],days[i])
            i+=1

        #how do we handle multiple messages here?
        
        return redirect(url_for("dele"))



if __name__ == '__main__':
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug=True
    app.run()
