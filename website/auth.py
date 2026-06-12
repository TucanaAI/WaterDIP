from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from . import db
from  werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_user, logout_user, login_required, current_user

import smtplib
from email.message import EmailMessage

from .token import generate_token, confirm_token
import platform

#from website import password_copy
from . import password_copy



auth = Blueprint('auth', __name__)


#THESE MUST BE MANUALLY CHANGED WHEN SETUP ON A SERVER
######################################################
cust_name = "app"
cust_codenum = "vllm" 

# cust_name = "app"
# cust_codenum = "vllm"
#######################################################
@auth.route('/' + cust_name +'/' + cust_codenum + '/login', methods = ["GET", "POST"])
def login():

    if request.method == 'POST':

        userName_or_email = request.form.get('userName')
        password = request.form.get('password')

        #note that it is expected to have only one user with the specified username (that is, if it exists)
        #since usernames are unique. 
        user = User.query.filter_by(username=userName_or_email).first()

        #TODO if a username was not found, check if email can be used to login!
        if user is None: #
            user = User.query.filter_by(email=userName_or_email).first() #filter the email records based on the email entered in the username login section.
        
        if user and user.is_confirmed: #if username exist
            #if the  user's password hash (from the user table - which gives the user's raw password), matches the incoming password
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category = 'success')
                login_user(user, remember=True) #flask_login, logs them into the home page (views.home)
                print('Is user authenticated? ....'+ str(user.is_authenticated))

                print('Is user an admin? ....'+ str(user.is_admin))

                print('Is user email confirmed? ....'+ str(user.is_confirmed))
                return redirect(url_for('views.home')) #url_for() takes the blueprint function. It is better than using url path in redirect().
            else:
                flash('Incorrect password! try again.', category = 'error')
        else: #username does not exist
            flash('Either your username (or email) does not exist, or you have not verified your account!', category='error')

    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    if not current_user.is_anonymous:
        print('current user is ' + current_user.first_name, flush = True)
    else:
        print('current user is anonymous', flush = True)
        
    return render_template('login.html', user=current_user, cust_name=cust_name, cust_codenum=cust_codenum,user_size = num_users)

@auth.route('/' + cust_name +'/' + cust_codenum + '/logout', methods = ["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/' + cust_name +'/' + cust_codenum + '/sign-up', methods = ["GET", "POST"])
def sign_up():

    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    if num_users == 0:
        logout_user() #logs out any previously-cached user's details from any previous subscription (if it exists) 

    global password_copy
    
    if request.method == "POST":
        userName = request.form.get('userName')
        email = request.form.get('email')
        email_tokens = email.split('@')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        is_admin = request.form.get('is_admin')
        # address = request.form.get('address')
        #check that the username and email does not appear in the database

        #filter user table based on email.
        user_by_email_exist =  User.query.filter_by(email=email).first()

        #filter user table based on username
        user_by_username_exist =  User.query.filter_by(username=userName).first() 

        #check email / username is unique in the user table.
        if user_by_email_exist:
            flash('Sorry, this email already exist...', category = 'error')
        elif user_by_username_exist:
            flash('Sorry, this username already exist...', category= 'error')
        elif len(userName) < 2:
            flash('Your username has to be at least two (2) characters...', category='error')
        elif '@' not in email or ('@' not in email and '.' not in email_tokens[-1]):
            flash('Oops!! your entry: '+email+' is not a valid email address...', category='error')
        elif len(firstName) < 2:
            flash('Your first name has to be at least two (2) characters...', category='error')
        elif len(lastName) < 2:
            flash('Your last name has to be at least two (2) characters...', category='error')
        elif password1 != password2:
            flash('Your passwords don\'t match...', category='error')
        elif len(password1) < 7:
            flash('Your password must be at least seven (7) characters...', category='error')
        # elif len(address) < 2:
        #     flash('Your address has to be at least two (2) characters...', category='error')
        else:
            
            password_copy = password1
            if num_users == 0: #First user / owner must be an admin. Also, first admin do not need to verify his account?
                #create a new user. Note that password must be stored as a hash and not the password itself.
                new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = True, is_confirmed = False)
                print('The new_user admin status after user creation is ...' + str(new_user.is_admin))
                
            else:
                #Decide if to make a user an admin during account creation.
                if is_admin == 'Yes':
                    #create a new user. Note that password must be stored as a hash and not the password itself.
                    new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = True, is_confirmed = False) 
                    print('The new_user admin status after user creation is ...' + str(new_user.is_admin))
                    
                else:
                    #create a new user. Note that password must be stored as a hash and not the password itself.
                    new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = False, is_confirmed = False)
                    print('The new_user admin status after user creation is ...' + str(new_user.is_admin))

            #create a database session (edit session)
            db.session.add(new_user)

            #update the database (flush any previously uncommited session and commit this current session, pending email verification)
            db.session.commit()

            token = generate_token(new_user.email) #generate a signed token (string) for email verification.

            if num_users == 0: #At sign up #Note: to use 0,you must have not done any new len(User.query.all()) for num_users after last commit.
                print('uv1')
                user_verification_request(new_user,token, new_user.id, 0)
            else:
                print('uv2')
                user_verification_request(new_user,token, new_user.id, current_user.id)

            return render_template('verify_user.html', user=current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)
    
    return render_template('sign_up.html', user=current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)


@auth.route('/'+ cust_name +'/' + cust_codenum + '/sign-up/confirm/<account_creator_id>/<user_id>/<token>', methods = ["GET", "POST"])
def confirm_email(account_creator_id, user_id, token):

    user_id = int(user_id)
    account_creator_id = int(account_creator_id)
    
    print('Got into the confirm email function', flush=True)
    global password_copy
    print('password_copy is '+ password_copy, flush=True)
    #Clicking on your verification link by the new user, starts a new vllm application session. Therefore, current_user has no attribute as this is an anonymous user (not logged in).
    #Therefore the user id must be shipped with the token.

    new_user = User.query.filter_by(id=user_id).first_or_404()
    print('new_user id '+ str(new_user.id), flush=True)

    print('type of account creator id is ..')
    print(type(account_creator_id))

    how_many = len(User.query.all())

    print('how many is '+ str(how_many))
    
    if account_creator_id == 0:
        account_creator = User.query.filter_by(id=1).first_or_404() #At sign-up stage, 1 is used to fetch the already-created user object (of the account creator) 
    else:
        account_creator = User.query.filter_by(id=account_creator_id).first_or_404() #At any other point, the admin id is gotten from the current_user.


    print('created the account_creator object', flush=True)

    if new_user.is_confirmed: #the account owner is the current user clicking via his email at this point
        flash("Account already confirmed.", "success")
        return redirect(url_for("views.home"))
    
    same_email = confirm_token(token)

    print('current user is ...' + new_user.first_name, flush=True)

    if new_user.email == same_email: #email is the same and will be marked as verified (is_confirmed = True)
        new_user.is_confirmed = True
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been verified. Thanks!", "success")
        num_users = len(User.query.all())

        password1 = password_copy
        #**************implement email notification for user creation*************************# (will be dependent on implementation of new user email verification)
        user_creation_notice(account_creator, new_user, password1, num_users)

        #send email address and password to the new user as well as the account creator
        if num_users == 1 and new_user.is_confirmed: #The application owner must be confirmed before being allowed to login

            flash('Congratulations...your vllm account has been created...', category='success')
            login_user(new_user, remember=True)#flask_login, automatically logs them in to the home page (views.home)
            #
        else: 
            #flash a message that says that account details has been sent to user's email
            flash('Congratulations...an account has been created and details sent to the new user...', category='success')

        #######################################################################################
        return redirect(url_for('views.home')) #url_for() takes the blueprint function. It is better than using url path in redirect().
    else: #email is different and will be removed or link is invalid or has expired. Hence temporarily added user will be deleted.

        db.session.delete(new_user)
        db.session.commit()

        flash("The confirmation link is invalid or has expired. Please contact your admin.", "danger")
        return redirect(url_for("auth.login"))

@auth.route('/' + cust_name +'/' + cust_codenum + '/user_profile/<user_id>', methods = ["GET", "POST"])
def change_password(user_id):
    user = User.query.get(user_id) #the the user whose password will be changed.

    num_users = len(User.query.all())
    print('The number of users in the database before password change is ' + str(num_users))

    if request.method == "POST":

        new_password1 = request.form.get('new_password1')
        new_password2 = request.form.get('new_password2')

        if new_password1 != new_password2:
            flash('Your new passwords don\'t match...', category='error')
        elif len(new_password1) < 7:
            flash('Your new password must be at least seven (7) characters...', category='error')
        else:
            
            # if num_users == 0: #First user / owner must be an admin
            #     #create a new user. Note that password must be stored as a hash and not the password itself.
            #     new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = True)
            #     print('The new_user admin status after user creation is ...' + str(new_user.is_admin))
            # else:
            #     #Decide if to make a user an admin during account creation.
            #     if is_admin == 'Yes':
            #         #create a new user. Note that password must be stored as a hash and not the password itself.
            #         new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = True)
            #         print('The new_user admin status after user creation is ...' + str(new_user.is_admin))
            #     else:
            #         #create a new user. Note that password must be stored as a hash and not the password itself.
            #         new_user = User(username = userName, email=email, password = generate_password_hash(password1, method = 'pbkdf2:sha256'), first_name=firstName, last_name=lastName, is_admin = False)
            #         print('The new_user admin status after user creation is ...' + str(new_user.is_admin))
            
            #generate a password hash for the new password.
            user.password = generate_password_hash(new_password1, method = 'pbkdf2:sha256')
            
            #create a database session (edit session)
            db.session.add(user)

            #update the database (flush any previously uncommited session and commit this current session.)
            db.session.commit()
            
            #**************implement email notification for password change*************************#
            password_change_notice(user, new_password1)

            flash('Congratulations...your password has been changed successfully...', category='success')
            login_user(user, remember=True)#flask_login, automatically logs them in to the home page (views.home)
    
            #######################################################################################
            return redirect(url_for('views.home')) #url_for() takes the blueprint function. It is better than using url path in redirect().
    

    return render_template('change_password.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)


@auth.route('/' + cust_name +'/' + cust_codenum + '/forgot-password', methods = ["GET", "POST"])
def forgot_your_password():

    if request.method == "POST":
        email = request.form.get('email')
        user_by_email_exist =  User.query.filter_by(email=email).first()

        if user_by_email_exist is not None and user_by_email_exist.is_confirmed: #user exists in the database (was created by an admin) and user is confirmed.
            print('got into forgot your password post')
            return redirect(url_for('auth.change_password',user_id = user_by_email_exist.id))
        elif user_by_email_exist is not None and not user_by_email_exist.is_confirmed: #user exist but has not verified his account.

            flash('You have not verified your account!', category='error')
            return redirect(url_for('auth.login'))
        else: #user is None and therefore does not exist

            flash('Your email does not exist', category='error')
            return redirect(url_for('auth.login'))

    num_users = len(User.query.all())
    print('The number of users in the database as at forgot your password is ' + str(num_users))
    return render_template('forgot_your_password.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size=num_users)

def user_verification_request(new_user,token, user_id, account_creator_id): #if account creator id is 0, we are at the sign up stage.

    EMAIL_ADDRESS = 'harrisonobidinnu@gmail.com'

    #generated app password after creating tx_server app name...
    EMAIL_PASSWORD = 'hana ujuu suzy ngoz' #.................... on our email server gmail account (txarray@gmail.com)

    #*********************************account receiver's message***************************************************#
    RECEIVERS_EMAIL_ADDRESS = new_user.email
    receiver_msg = EmailMessage()
    
    #The subject for a successful user account creation. A successful user account creation should not have any error message.
    receiver_msg['Subject'] = 'vllm - Account verification'
    
    receiver_msg['From'] = EMAIL_ADDRESS 
    receiver_msg['To'] = RECEIVERS_EMAIL_ADDRESS 


    # receiver_msg.set_content('''
    # Hello '''+new_user.first_name+''',

    # testing

    # ''')

    if platform.node() != 'CCLNG-14062129': #if they are servers

        receiver_msg.add_alternative(f"""\
        <html>
        <body>

            <p>Hello {new_user.first_name}<p>  
                                    
            <br><br>                   
            <p>An account is about to be created for you in the vllm Software<p>

            <br><br>       

            <p>To complete your account creation, please verify your email: <a href="https://www.harrisonobidinnu.com/{cust_name}/{cust_codenum}/sign-up/confirm/{account_creator_id}/{user_id}/{token}">verify here</a>.</p>

            <br><br>
            <br><br>

            <p>Best Regards<p>
            <p>vllm team<p>

        </body>
        </html>
        """, subtype='html')
    else: #it's the developer machine (CCLNG-14062129)
        receiver_msg.add_alternative(f"""\
        <html>
        <body>

            <p>Hello {new_user.first_name}<p>  
                                    
            <br><br>                   
            <p>An account is about to be created for you in the vllm Software<p>

            <br><br>       

            <p>To complete your account creation, please verify your email: <a href="http://127.0.0.1:5000/{cust_name}/{cust_codenum}/sign-up/confirm/{account_creator_id}/{user_id}/{token}">verify here</a>.</p>

            <br><br>
            <br><br>

            <p>Best Regards<p>
            <p>vllm team<p>

        </body>
        </html>
        """, subtype='html')


    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 
        # if num_users > 0: #default admin can only send account creation notice to others and not to self
        #     smtp.send_message(sender_msg)
        smtp.send_message(receiver_msg)


def user_creation_notice(account_creator, new_user, password1, num_users):

    EMAIL_ADDRESS = 'harrisonobidinnu@gmail.com'

    #generated app password after creating vllm_server app name...
    EMAIL_PASSWORD = 'hana ujuu suzy ngoz' #.................... on our email server gmail account (txarray@gmail.com)

    # print(password1)
    # print(new_user.email)
    # print(current_user.email)

    if num_users > 1:
        #*********************************account creator's message***************************************************#
        ACCOUNT_CREATOR_EMAIL = account_creator.email #account creator email only exists when an admin exists in the database
        sender_msg = EmailMessage()
        
        #The subject for a successful user account creation. A successful user account creation should not have any error message.
        sender_msg['Subject'] = 'vllm - new user added'
        
        sender_msg['From'] = EMAIL_ADDRESS 
        sender_msg['To'] = ACCOUNT_CREATOR_EMAIL
        
        sender_msg.set_content('''
        Hi '''+account_creator.first_name+''',

        You have created an account for '''+new_user.first_name+''' '''+new_user.last_name+'''.

        The login details below have been sent to the new user's email address:

        username(or email): '''+new_user.username+ ''' (or '''+new_user.email+''') 
        password: '''+password1+'''

        It is recommended that the new user changes this password after first login

        Best regards,
        vllm team.
        ''')


    #*********************************account receiver's message***************************************************#
    RECEIVERS_EMAIL_ADDRESS = new_user.email
    receiver_msg = EmailMessage()
    
    #The subject for a successful user account creation. A successful user account creation should not have any error message.
    receiver_msg['Subject'] = 'vllm - user account created'
    

    receiver_msg['From'] = EMAIL_ADDRESS
    receiver_msg['To'] = RECEIVERS_EMAIL_ADDRESS


    receiver_msg.set_content('''
    Hello '''+new_user.first_name+''',

    An account has been created for you in the vllm Software.

    Your login details are shown below:

    username(or email): '''+new_user.username+ ''' (or '''+new_user.email+''') 
    password: '''+password1+'''

    It is recommended that you change your password after your first login.

    Best regards,
    vllm team.
    ''')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 
        if num_users > 1: #default admin can only send account creation notice to others and not to self
            smtp.send_message(sender_msg)
        smtp.send_message(receiver_msg)


def password_change_notice(user, new_password1):

    EMAIL_ADDRESS = 'harrisonobidinnu@gmail.com'

    #generated app password after creating tx_server app name...
    EMAIL_PASSWORD = 'hana ujuu suzy ngoz' #.................... on our email server gmail account (txarray@gmail.com)

    #*********************************account receiver's message***************************************************#
    RECEIVERS_EMAIL_ADDRESS = user.email
    receiver_msg = EmailMessage()
    
    #The subject for a successful user account creation. A successful user account creation should not have any error message.
    receiver_msg['Subject'] = 'vllm - password changed'
    
    receiver_msg['From'] = EMAIL_ADDRESS 
    receiver_msg['To'] = RECEIVERS_EMAIL_ADDRESS 

    receiver_msg.set_content('''
    Hello '''+user.first_name+''',

    This is to inform you that your password has been changed in the vllm Software.

    Your new login details are shown below:

    username(or email): '''+user.username+ ''' (or '''+user.email+''') 
    password: '''+new_password1+'''

    Best regards,
    vllm team.
    ''')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD) 
        smtp.send_message(receiver_msg)