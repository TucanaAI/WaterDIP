from flask import Blueprint
from itsdangerous import URLSafeTimedSerializer

#from website import app
from . import app

token = Blueprint('token', __name__) #Flask API Blueprint for the views (views.py) 

def generate_token(email):

    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

    #generate a signed token (string or bytes)
    return serializer.dumps(email, salt=app.config["SECURITY_PASSWORD_SALT"]) 


def confirm_token(token, expiration=259200): #3 days for expiration.
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    try:
        email = serializer.loads(
            token, salt=app.config["SECURITY_PASSWORD_SALT"], max_age=expiration #Seconds or Milliseconds?
        )
        return email
    except Exception:
        return False