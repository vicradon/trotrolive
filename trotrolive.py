from flask import Flask, render_template, flash, request, url_for, redirect, session, g
from flask_sqlalchemy import SQLAlchemy 
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
from flask_login import login_manager
from functools import wraps

old_email = ''

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trotrousers.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fares.db'
app.config['SQLALCHEMY_BINDS'] = {
    'User':      'sqlite:///trotrousers.db',
    'fares':      'sqlite:///fares.db',
    'userfares':  'sqlite:///userfares.db'
}
db = SQLAlchemy(app)
app.secret_key = 'secretkey'


class User(db.Model):
    __bind_key__ = 'User' 
    id = db.Column(db.Integer, unique=True, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    fname = db.Column(db.String(15), unique=False, nullable=False)
    lname = db.Column(db.String(15), unique=False, nullable=False)
    gender = db.Column(db.String(7), unique=False, nullable=False)
    dob = db.Column(db.String(10), unique=False, nullable=False)
    passhash = db.Column(db.String(180), unique=False, nullable=False)

    #def __repr__(self):
        #return 'User ' + str(self.id)

class fares(db.Model):
    __bind_key__ = 'fares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    srcdest = db.Column(db.String(50), unique=False, nullable=False)
    fare = db.Column(db.String(15), unique=False, nullable=False)
    transit = db.Column(db.String(15), unique=False, nullable=False)

class userfares(db.Model):
    __bind_key__ = 'userfares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    fullname = db.Column(db.String(50), unique=False, nullable=False)
    srcdest = db.Column(db.String(50), unique=False, nullable=False)
    fare = db.Column(db.String(15), unique=False, nullable=False)
    transit = db.Column(db.String(15), unique=False, nullable=False)

def __init__(fares, srcdest, fare):
    fares.srcdest = srcdest
    fares.fare = fare
    fares.transit = transit

def ensure_logged_in(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'):
            flash("Please log in first")
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.before_request
def before_request():
    if 'user_id' in session:
        user = User.query.filter_by(id = session['user_id']).first()
        g.userfname = user

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None

    if request.method == 'POST':
        new_email = request.form['email']
        new_fname = request.form['fname']
        new_lname = request.form['lname']
        new_gender = request.form['gender']
        new_dob = request.form['dob']
        new_pass = request.form['repassword']

        passcheck = request.form['password']
        user = User.query.filter_by(email=new_email).first()

        if user:
            error = 'Email already exists'
        elif new_email == '':
            error = 'Email cannot be blank!'
        elif new_fname == '':
            error = 'You must provide a first name!'
        elif new_lname == '':
            error = 'You must provide a Last name!'
        elif new_dob == '':
            error = 'Please Enter a Date of Birth!'
        elif new_pass != passcheck:
            error = 'Passwords do not match. Please try again!'
        else:
            hash_new_pass = generate_password_hash(new_pass, method='sha256')
            new_user = User(email=new_email, fname=new_fname, lname=new_lname, gender=new_gender, dob=new_dob, passhash=hash_new_pass)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created Successfully. You can login now')
            return redirect(url_for('login'))
    return render_template('signup.html', error = error)

@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        old_email = request.form['email']
        passcheck = request.form['password']
        email = User.query.filter_by(email = old_email).first()
        if not email or not check_password_hash(email.passhash, passcheck):
            flash('Please check your login details and try again.')
            return redirect(url_for('login'))
        else:
            session['user_id'] = email.id
            flash('Welcome '+ old_email+'!')
            return redirect(url_for('member'))

    return render_template('login.html')

@app.route('/search' , methods=['POST'])
def search():
    src = request.form['src']
    dest = request.form['dest']
    if src == dest:
        same = 'You chose the same location twice!'
        return render_template('index.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = fares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('index.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )

    else:
        srcdest = str(dest)+str(un)+str(src)
        check = fares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('index.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('index.html', same=same)

@app.route('/searchm' , methods=['POST'])
@ensure_logged_in
def searchm():
    src = request.form['src']
    dest = request.form['dest']
    if src == dest:
        same = 'You chose the same location twice!'
        return render_template('member.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = fares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('member.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
    #print(check)
    else:
        srcdest = str(dest)+str(un)+str(src)
        check = fares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('member.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('member.html', same=same)

@app.route('/member')
@ensure_logged_in
def member():
    return render_template('member.html')

@app.route('/company')
def company():
    return render_template('company.html')

@app.route('/report')
@ensure_logged_in
def report():
    return render_template('report.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/suggest', methods=['GET', 'POST'])
@ensure_logged_in
def suggest():
    if request.method == 'POST':
        fullname = request.form['fullname']
        src = request.form['src']
        dest = request.form['dest']
        fare = request.form['fare']
        transit = request.form['transit']
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        new_fare = userfares(fullname=fullname, srcdest=srcdest, fare=fare, transit=transit)
        db.session.add(new_fare)
        db.session.commit()
        flash('Your fare has been submitted and will be Reviewed!')
        return redirect(url_for('member'))
    return render_template('suggest.html')



@app.route('/logout')
@ensure_logged_in
def logout():
  session.pop('user_id', None)
  flash('You have been signed out.')
  return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)    
