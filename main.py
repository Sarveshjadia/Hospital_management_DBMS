from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, logout_user, LoginManager, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
#                       APP SETUP
# ---------------------------------------------------------
app = Flask(__name__)
app.secret_key = "hmsprojects"

# ---------- DATABASE CONFIG ----------
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@localhost/hospital_managementdbms"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------- LOGIN MANAGER ----------
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------------------------------------------------
#                     USER LOADER
# ---------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------
#                     DATABASE MODELS
# ---------------------------------------------------------
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    usertype = db.Column(db.String(50))  # Admin/Doctor/Patient
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))

class Patients(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    gender = db.Column(db.String(50))
    slot = db.Column(db.String(50))
    disease = db.Column(db.String(50))
    time = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    dept = db.Column(db.String(50))
    number = db.Column(db.String(50))

class Doctors(db.Model):
    did = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50))
    doctorname = db.Column(db.String(50))
    dept = db.Column(db.String(50))

class Trigr(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))
    action = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))


# -------------- Create Tables Once -----------------
with app.app_context():
    db.create_all()


# ---------------------------------------------------------
#                        ROUTES
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


# ------------------- Doctors -------------------
@app.route('/doctors', methods=['POST', 'GET'])
def doctors():
    if request.method == "POST":
        query = Doctors(email=request.form['email'], doctorname=request.form['doctorname'], dept=request.form['dept'])
        db.session.add(query)
        db.session.commit()
        flash("Doctor Added Successfully!", "primary")
    return render_template('doctor.html')


# ------------------- Patients -------------------
@app.route('/patients', methods=['POST', 'GET'])
@login_required
def patient():
    doct = Doctors.query.all()
    if request.method == "POST":
        if len(request.form['number']) != 10:
            flash("Number must be 10 digits!", "danger")
            return render_template('patient.html', doct=doct)

        query = Patients(**request.form)
        db.session.add(query)
        db.session.commit()
        flash("Appointment Booked Successfully!", "success")

    return render_template('patient.html', doct=doct)


# ------------------- BOOKINGS (FIXED) -------------------
@app.route('/bookings')
@login_required
def bookings():

    # ADMIN → See ALL bookings
    if current_user.usertype.lower() == "admin":
        query = Patients.query.all()

    # DOCTOR → Only same dept patients
    elif current_user.usertype.lower() == "doctor":
        doc = Doctors.query.filter_by(email=current_user.email).first()
        if doc:
            query = Patients.query.filter_by(dept=doc.dept).all()
        else:
            query = []

    # NORMAL USER → Only their bookings
    else:
        query = Patients.query.filter_by(email=current_user.email).all()

    return render_template("booking.html", query=query)



# ------------------- Signup -------------------
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        if User.query.filter_by(email=request.form['email']).first():
            flash("Email Already Exists!", "warning")
            return render_template('signup.html')

        new_user = User(
            username=request.form['username'],
            usertype=request.form['usertype'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password'])
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Signup Successful, Please Login!", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')



# ------------------- Login -------------------
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash("Login Successful!", "primary")
            return redirect(url_for('index'))

        flash("Invalid Credentials!", "danger")

    return render_template('login.html')



# ------------------- Logout -------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged Out Successfully!", "info")
    return redirect(url_for('login'))



# ------------------- RUN APP -------------------
if __name__ == "__main__":
    app.run(debug=True)
