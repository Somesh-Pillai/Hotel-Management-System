from flask import Flask, request, make_response,session,abort,redirect,render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime
from datetime import timedelta
from flask_admin.menu import MenuLink
from flask_mail import Mail, Message
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hotel.db'
app.config['SECRET_KEY'] = 'abababab'
app.permanent_session_lifetime=timedelta(minutes=30)
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 465
app.config['MAIL_USERNAME']= '<yoursendingmailid>@gmail.com'
app.config['MAIL_PASSWORD']= '<mailidpassword>'
app.config['MAIL_USE_TLS']= False
app.config['MAIL_USE_SSL']= True

mail=Mail(app)

db = SQLAlchemy(app)

class Guests(db.Model):
    g_id = db.Column(db.Integer, primary_key=True)
    g_name = db.Column(db.String(20), unique=False, nullable=False)
    g_email = db.Column(db.String(120), unique=True, nullable=False)
    g_streetno = db.Column(db.String(120), unique=False, nullable=False)
    g_city = db.Column(db.String(120), unique=False, nullable=False)
    g_country = db.Column(db.String(120), unique=False, nullable=False)
    g_streetno = db.Column(db.String(120), unique=False, nullable=False)
    g_pincode = db.Column(db.String(10), unique=False, nullable=False)
    g_password = db.Column(db.String(20), unique=False, nullable=False)
    g_state = db.Column(db.String(12), unique=False, nullable=False)

class Type(db.Model):
    t_id = db.Column(db.Integer, primary_key=True)
    t_name = db.Column(db.String(20),nullable=False)
    t_cost = db.Column(db.Integer)
    t_img= db.Column(db.String(200))
class Rooms(db.Model):
        r_id = db.Column(db.Integer, primary_key=True)
        t_id = db.Column(db.Integer)
        r_number = db.Column(db.Integer)
        r_status = db.Column(db.String(20),nullable=False)

class Bookings(db.Model):
        b_id = db.Column(db.Integer, primary_key=True)
        r_number=db.Column(db.Integer)
        t_name = db.Column(db.String(120))
        g_id = db.Column(db.Integer, db.ForeignKey('guests.g_id'))
        name = db.Column(db.String(20), nullable=False)
        count = db.Column(db.Integer)
        email = db.Column(db.String(120), unique=False, nullable=False)
        sd = db.Column(db.DateTime)
        ed = db.Column(db.DateTime)  #yyyy-mm-dd   from datetime import datetime
        b_status = db.Column(db.String(20), default='Booking Pending')
        b_cost= db.Column(db.Integer)

### Admin Permissions

admin = Admin(app, template_mode='bootstrap4')
class SecureModelView(ModelView):
    def is_accessible(self):
        if "log" in session:
            return True
        else:
            abort(403)

admin.add_view(SecureModelView(Guests, db.session))
admin.add_view(SecureModelView(Type, db.session))
admin.add_view(SecureModelView(Rooms, db.session))
admin.add_view(SecureModelView(Bookings, db.session))
flag=0
@app.route("/alogin",methods=['GET','POST'])
def alogin():
    if request.method=='POST':
        if request.form.get('Username')== "<yourusername>" and request.form.get('Password')=='<yourpassword>':
            session['log']=True
            global flag
            if flag==0:
                admin.add_link(MenuLink(name='Logout', url=url_for('alogout')))
                flag=1
            return redirect("/admin")
        else:
            return render_template("/admin/alogin.html",failed="True")
    return render_template("/admin/alogin.html")

@app.route("/alogout")
def alogout():
    session.clear()
    return redirect("/alogin")

@app.route("/home")
@app.route("/")
def home():
    return render_template("tryhome.html")
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        session.permanent=True
        name = request.form.get('pname', None)
        if name is not None:
            pwd = request.form['pwd']
            name = request.form['pname']
            guest = Guests.query.filter_by(g_name=name, g_password=pwd).first()
            if guest:
                flash('Login successful!', 'success')
                print(guest.g_id)
                session['guest'] = guest.g_id
                return redirect(url_for('user'))
            else:
                flash('Invalid credentials', 'danger')
                return render_template('login.html')
    else:
        if "user" in session:    #if logged on no need to go to login page
          flash("Already Logged in!!",'success')
          return redirect(url_for("user"))
        return render_template("login.html")
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['gname']
        email = request.form['email']
        streetno = request.form['streetno']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        pincode = request.form['pincode']
        pwd = request.form['pwd']
        cnf_pwd = request.form['cnf_pwd']

        ob = Guests(g_name=name,g_password=pwd,g_email=email,g_streetno=streetno,g_city=city,g_state=state,g_country=country,g_pincode=pincode)

        if pwd == cnf_pwd:
            db.session.add(ob)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash("Passwords do not match! Please enter same password",'danger')
            return render_template('register.html')
    return render_template('register.html')
@app.route("/user")
def user():
    if "guest" in session:
      user=session["guest"]
      guest=Guests.query.get(user).g_name
      type=Type.query.all()
      return render_template('user.html',name=guest, type=type)
    else:
      flash(f"Your are not logged in!!")
      return redirect(url_for("login"))
@app.route('/booking', methods=['GET','POST'])
def booking():
    if request.method == 'POST':
        session.permanent=True
        name = request.form['bname']
        email = request.form['bemail']
        count = request.form['count']
        sd = request.form['sd']
        startdate=datetime.strptime(sd,'%Y-%m-%d').date()
        ed = request.form['ed']
        enddate=datetime.strptime(ed,'%Y-%m-%d').date()
        typename=request.form['type']
        id=session['guest']
        days=enddate-startdate
        t=Type.query.filter_by(t_name=typename).first()
        r=Rooms.query.filter_by(t_id=t.t_id,r_status='Booking Pending').first()
        r.r_status="Booking Confirmed"
        cost= t.t_cost * days.days
        obj = Bookings(name=name,email=email,count=count,g_id=id,t_name=typename,r_number=r.r_number,sd=startdate,ed=enddate,b_status="Booking Confirmed",b_cost=cost)
        db.session.add(obj)
        db.session.commit()
        print(name)
        msg="Booking successful!!\n\n\nBooking Details\n"+ "Name: " + name +"\nRoom Type: "+ typename + "\nStart Date: " + str(startdate) \
        + "\nEnd Date: " + str(enddate) +"\nCount: " + str(count) + "\nFinal Cost: " + str(cost) +"\n\n\nThank You for choosing us!\nWith Love!\nATLANTIS :)"

        subject="Booking Info"
        message=Message(subject=subject,sender="<yoursendingmailid>@gmail.com",recipients=[email])
        message.body=msg
        mail.send(message)
        flash(f"Booking Confirmation Sent To Mail!",'success')
        return redirect(url_for("user"))

    type_obj =Type.query.all()
    l=[]
    list1=[]
    for i in type_obj:
      l.append(i.t_id)
      print(l,"first")
    for i in l:
       r=Rooms.query.filter_by(t_id=i,r_status='Booking Pending').first()
       if r is not None:
         avail=Type.query.filter_by(t_id=r.t_id).first()
         list1.append(avail)
    return render_template('booking.html',type=list1)
@app.route('/history')
def history():
    if "guest" in session:
      user=session["guest"]
      d=Bookings.query.filter_by(g_id=user,b_status='Booking Confirmed').all()
      if len(d)==0:
          flash(f"No Previous History",'danger')
          return redirect(url_for("user"))
      for obj in d:
       edate=datetime.strptime(str(obj.ed),'%Y-%m-%d %H:%M:%S').date()
       #if datetime.now()>edate
       if date.today()>edate:
          obj.b_status="Booking Completed"
          db.session.commit()
      return render_template("history.html",values=Bookings.query.filter_by(g_id=user,b_status="Booking Completed").all(),enddate=edate)
@app.route("/logout")
def logout():
    if "guest" in session:  #if actual user has loggin in before
      user=session["guest"]
    session.pop("guest",None)
    flash("Not logged in",'info')
    return redirect(url_for("login"))
if __name__ == "__main__":
        db.create_all()
        app.run(debug=True)
