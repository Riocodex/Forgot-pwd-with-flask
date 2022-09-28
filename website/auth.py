from flask import Blueprint , render_template , request , flash , redirect , url_for 

from .models import User , Books , ResetRequestForm , ResetPasswordForm
from . import db , mail 
from werkzeug.security import generate_password_hash , check_password_hash
from flask_login import login_user , login_required , logout_user , current_user
from flask_mail import Message

auth = Blueprint('auth' , __name__)

@auth.route('/login' , methods = ['GET' , 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in succesfuly' , category='success')
                login_user(user , remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password , try again. ' , category='error')
        else:
            flash('Email does not exist' , category='error')
            
    return render_template("login.html" , user = current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up' , methods = ['GET' , 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        
        user = User.query.filter_by(email = email).first()
        if user:
            flash('Email already exists.', category= 'error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters. ' , category='error')
        elif len(first_name) < 2: 
            flash('First name must be greater than 1 character', category ='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category ='error')
        elif len(password1) < 7:
            flash('password must be atleast 7 characters', category ='error')
        else:
            #add user to database
            new_user = User(email = email , first_name = first_name , password = generate_password_hash(password1 , method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            # login_user(user , remember=True)#the remeber=true here is to ensure the user doesnt need to login all the time
            flash('Account created!' , category='success')
            return redirect(url_for('views.home'))
            pass
    return render_template("sign-up.html" , user=current_user)
@auth.route('/booking-history')
@login_required
#defining function that will be returned when root is called
def booking_history():
    #returning the webpage to be displayed
    return render_template("booking_history.html" , user=current_user)

@auth.route('/dashboard' , methods=['GET' , 'POST'])
@login_required
#defining function that will be returned when root is called
def dashboard():
    if request.method == 'POST':
        carBrand = request.form.get('carBrand')
        seats = request.form.get('seats')
        costs = request.form.get('costs')
        if len(carBrand) < 2:
            flash('Car brand name too small' , category='error')
        elif len(seats) < 1:
            flash('input number of seats' , category='error')
        else:
            new_book = Books(carBrand = carBrand , numberOfSeats = seats , costs = costs , user_id=current_user.id)
            db.session.add(new_book)
            db.session.commit()
            flash('car Booked!' , category='success')
    return render_template("admin_dashboard.html" , user=current_user)

def send_mail(user):
    token = user.get_token()
    msg = Message('Password Reset Request' , recipients = [user.email] , sender='onwukachibike@gmail.com')
    msg.body = f''' To reset your password. Plese follow the link below
     
    {url_for(reset_token , token = token , _external =True)}
    
    If you didnt send a password reset request. Please ignore this message.
    
    '''

@auth.route('/reset_password' , methods=['GET' , 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data)
        if user:
            send_mail(user)
            flash('Reset request sent. Check your email' , 'success')
            return redirect(url_for('login'))
    return render_template('reset_request.html' , title='Reset Request' , form = form , user=current_user , legend = 'Reset Password') 

@auth.route('/reset_password/<token>' , methods = ['GET' , 'POST'])
def reset_token(token):
    user = User.verify_token(token)
    if user is None:
        flash('That is invalid token or expired. Please try again.' , 'warning')
        return redirect(url_for('reset_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
         hashed_password = generate_password_hash(form.password.data , method='sha256')
         user.password = hashed_password
         db.session.commit()
         flash('password changed! please Login!' , 'success')
         return redirect(url_for('login'))
     
    return render_template('changepassword.html' , title='ChangePassword' , legend='change Password' , form = form)