from flask import Flask, render_template, flash, request, url_for, redirect, session, g, jsonify
from flask_sqlalchemy import SQLAlchemy 
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, logout_user, current_user, login_user
from flask_login import login_manager
from functools import wraps
import json
from authlib.integrations.flask_client import OAuth


old_email = ''

app = Flask(__name__)



#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trotrousers.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fares.db'
app.config['SQLALCHEMY_BINDS'] = {
    'User':      'sqlite:///trotrousers.db',
    'fares':      'sqlite:///fares.db',
    'userfares':  'sqlite:///userfares.db',
    'kumasifares':  'sqlite:///KumasiFaresdb.db',
    'obuasifares':  'sqlite:///ObuasiFaresdb.db',
    'accrafares':  'sqlite:///AccraFaresdb.db',
    'sefwifares':  'sqlite:///SefwiFaresdb.db'
}
db = SQLAlchemy(app)
app.secret_key = 'secretkey'
oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='0HQbdZewdUuIHCBfLqPxtHnk5JxVXmbl',
    client_secret='pKLSq8968hvDSgZN0MM_mZ-5PmjzEsdwzmnUpM4drLzbfz7DlmbCpLvLawQ-dw55',
    api_base_url='https://111uuuccciii.us.auth0.com',
    access_token_url='https://111uuuccciii.us.auth0.com/oauth/token',
    authorize_url='https://111uuuccciii.us.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)


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

class kumasifares(db.Model):
    __bind_key__ = 'kumasifares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    srcdest = db.Column(db.String(50), unique=False, nullable=False)
    fare = db.Column(db.String(15), unique=False, nullable=False)
    transit = db.Column(db.String(15), unique=False, nullable=False)

class sefwifares(db.Model):
    __bind_key__ = 'sefwifares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    srcdest = db.Column(db.String(50), unique=False, nullable=False)
    fare = db.Column(db.String(15), unique=False, nullable=False)
    transit = db.Column(db.String(15), unique=False, nullable=False)

class obuasifares(db.Model):
    __bind_key__ = 'obuasifares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
    srcdest = db.Column(db.String(50), unique=False, nullable=False)
    fare = db.Column(db.String(15), unique=False, nullable=False)
    transit = db.Column(db.String(15), unique=False, nullable=False)

class accrafares(db.Model):
    __bind_key__ = 'accrafares'
    id = db.Column(db.Integer, unique=True, primary_key=True)
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
        if not (session.get('user_id') or session.get('profile')):
            flash("Please log in first")
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.before_request
def before_request():
    if 'user_id' in session:
        user = User.query.filter_by(id = session['user_id']).first()
        g.userfname = user
    elif 'profile' in session:
        user = session['profile']
        g.username = user

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/kumasi')
def kumasi():
    return render_template('kumasi.html')

@app.route('/sefwi')
def sefwi():
    return render_template('sefwi.html')

@app.route('/obuasi')
def obuasi():
    return render_template('obuasi.html')

@app.route('/accra')
def accra():
    return render_template('accra.html')


@app.route('/selectcity' , methods=['POST'])
def selectcity():
    city = request.form['city']
    city = str(city)
    if city == 'kumasi':
        return redirect(url_for('kumasi'))
    elif city == 'sefwi':
        return redirect(url_for('sefwi'))
    elif city == 'obuasi':
        return redirect(url_for('obuasi'))
    elif city == 'accra':
        return redirect(url_for('accra'))
        



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
        session.pop('profile', None)
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
        return render_template('kumasi.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = kumasifares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('kumasi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )

    else:
        srcdest = str(dest)+str(un)+str(src)
        check = kumasifares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('kumasi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('kumasi.html', same=same)


@app.route('/searchsefwi' , methods=['POST'])
def searchsefwi():
    src = request.form['src']
    dest = request.form['dest']
    if src == dest:
        same = 'You chose the same location twice!'
        return render_template('sefwi.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = sefwifares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('sefwi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )

    else:
        srcdest = str(dest)+str(un)+str(src)
        check = sefwifares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('sefwi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('sefwi.html', same=same)


@app.route('/searchobuasi' , methods=['POST'])
def searchobuasi():
    src = request.form['src']
    dest = request.form['dest']
    if src == dest:
        same = 'You chose the same location twice!'
        return render_template('obuasi.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = obuasifares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('obuasi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )

    else:
        srcdest = str(dest)+str(un)+str(src)
        check = obuasifares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('obuasi.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('obuasi.html', same=same)


@app.route('/searchaccra' , methods=['POST'])
def searchaccra():
    src = request.form['src']
    dest = request.form['dest']
    if src == dest:
        same = 'You chose the same location twice!'
        return render_template('accra.html', same=same)
    else:
        un = str('_')
        srcdest = str(src)+str(un)+str(dest)
        check = accrafares.query.filter_by(srcdest = srcdest).all()

    if check != []:
        return render_template('accra.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )

    else:
        srcdest = str(dest)+str(un)+str(src)
        check = accrafares.query.filter_by(srcdest = srcdest).all()
        if check != []:
            return render_template('accra.html', 
                                            singlefare = check , 
                                            src=src, 
                                            dest=dest )
        else:
            same = 'Sorry, the fare you are looking for cannot be found'
            return render_template('accra.html', same=same)
        

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
    email = dict(session).get('email', None)
    return render_template('member.html', email=email)

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
  session.pop('profile', None)
  flash('You have been signed out.')
  return redirect(url_for('login'))

@app.route('/loginG')
def loginG():
    session.pop('user_id', None)
    session.pop('profile', None)
    return auth0.authorize_redirect(redirect_uri='https://trotrolive.herokuapp.com/authorize')

@app.route('/authorize')
def authorize():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    session['jwt_payload'] = userinfo
    session['profile'] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/member')



if __name__ == "__main__":
    app.run(debug=False)    
