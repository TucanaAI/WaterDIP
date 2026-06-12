from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from os import path
from flask_login import LoginManager
from flask_migrate import Migrate
import platform

db = None # creates a global db variable, will configure the operating engine later.
migrate = None # creates a global migrate variable, will configure the migration engine later.
app = None #creates a global flask app, that can be accessed by token.py file.
password_copy = None

def create_app():
    global db
    global migrate
    global app

    app = Flask(__name__, instance_relative_config=True)
    import os
    os.makedirs(app.instance_path, exist_ok=True)
    print("instance path is ... " + app.instance_path)
    app.config['SECRET_KEY'] = 'romeo'
    DB_NAME = "vLLM_App.db"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, DB_NAME)}"
    app.config['SECURITY_PASSWORD_SALT'] = 'xxabczzz'
    
    db = SQLAlchemy(app) #creates the .db file and creates the operating engine inside of the db
    
    if platform.node() != 'CCLNG-14062129': #if node is not development server (that is, if it is production server)
        migrate = Migrate(app, db)  #creates the db migration engine

    # db.init_app(app) #initialises a database instance (for TXArray_Web_App.db) with our application (TXArray_Web_App!)
    # migrate.init_app(app,db) #initialises a migration instance (for TXArray_Web_App.db) with our application (TXArray_Web_App!)
    #print('created the database engine inside of '+DB_NAME + ', (no table schemas yet...)')

    from .views import views
    from .auth import auth
    from .token import token
    from .models import User
    from .models import Note
    

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth,  url_prefix='/')
    app.register_blueprint(token,  url_prefix='/')

    print('platform name is ... '+platform.node())
    
    #if platform.node() == 'CCLNG-14062129':  # development machine
        
    with app.app_context():
        db.create_all()
        print('ensured database tables exist in ' + DB_NAME)

        has_user_table = db.engine.dialect.has_table(db.engine.connect(), 'user')
        print('has_user_table is ...' + str(has_user_table))

        has_note_table = db.engine.dialect.has_table(db.engine.connect(), 'Note')
        print('has_note_table is ...' + str(has_note_table))
    # if platform.node() == 'CCLNG-14062129': # if node is development server (CCL Laptop)
        
    #     with app.app_context():
    #         if path.exists('instance/'+DB_NAME):
                
    #             #Temporarily create all tables in the database.
    #             #This is required for testing on development machine 
    #             has_user_table = db.engine.dialect.has_table(db.engine.connect(), 'user')
    #             has_note_table = db.engine.dialect.has_table(db.engine.connect(), 'Note')

    #             if not has_user_table and not has_note_table: #only create the table if it does not exist
    #                 db.create_all() 
    #                 print('created database tables in '+DB_NAME)      
    
    #         has_user_table = db.engine.dialect.has_table(db.engine.connect(), 'user')
    #         print('has_user_table is ...'+str(has_user_table))

    #         has_note_table = db.engine.dialect.has_table(db.engine.connect(), 'Note')
    #         print('has_note_table is ...'+str(has_note_table))

    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    
    #make sure you have instantiated the flask migrate db.
    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
        
    
    return app
