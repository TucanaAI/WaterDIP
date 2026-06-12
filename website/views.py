from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import Note
from .models import User
import datetime
from . import db # import db from the __init__.py in the current directory
import os, glob
import sys
import subprocess
import time
import psutil
import httpx

views = Blueprint('views', __name__) #Flask API Blueprint for the views (views.py) 
FASTAPI_CHAT_URL = os.getenv("FASTAPI_CHAT_URL", "http://127.0.0.1:8080/chat")

#THESE MUST BE MANUALLY CHANGED WHEN SETUP ON A SERVER
######################################################
cust_name = "app"
cust_codenum = "llm" 

# cust_name = "app"
# cust_codenum = "llm"
#######################################################

# *********************************************************************************************************************
# ****************************** Global variables used to communicate between @views.route functions  *****************
# *********************************************************************************************************************
ready_for_upload = True
process_handle = None      # can hold an object which gives state of julia-running sub-process


# ***********************************************************************************************************************
# ******************** Set paths to julia executable, home directory & programme path (../genai_microservice/app/main.py)
# ***********************************************************************************************************************
python = ""
home_user = os.path.expanduser('~')
if '/bin' in os.path.dirname(sys.executable): #if the system sees the python3 binary from '/bin' (the symbolic directory for binaries), then program runs from linux or wsl
    print("Setting julia path from Ubuntu OS (or WSL distro)", flush=True) # you may also like to know that the version currently in wsl is v1.9.4
    if os.path.exists("/proc/sys/fs/binfmt_misc/WSLInterop"): #if running on WSL, assign home user from developer's WSL , else use value defined in outer scope to get that of server's (Linux).
        home_user = "/home/Harrison.Obidinnu"  #home_user = "/home/tx"       
    python = home_user + "/Documents/Documents/HARRISON/LLM/flask-venv/Scripts/python.exe" # C:/Users/Harrison.Obidinnu/Documents/Documents/HARRISON/LLM/flask-venv/Scripts/python.exe
    
else: #it is from Windows.
    print("Windows automatically sets python path. ", flush=True) # NB: Make sure you have no python path explicitly set in your environment variable.?
    
home_directory_path = os.path.dirname(__file__) #The directory ("website") of the running file (views.py)

vllm_backend_programme = home_directory_path + '../genai_microservice/app/main.py' #website/../genai_microservice/app/main.py   

print('finished setting project and python paths', flush=True) 


# *********************************************************************************************************************
# ******************** The root domain which notifies the user to enter their customer full address path **************
# *********************************************************************************************************************
@views.route('/') 
def notmain():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    path = request.path

    print('notmain path is '+path)
    print('while the built url (url_for()) is ')
    print(url_for('views.notmain'))
    return render_template("full_address.html", user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size=num_users, url_path=path)


# *********************************************************************************************************************
# ************************************** Displays the demo LLM page for user prompt queries ***************************
# **************************************    Will apply rate limiting of 15 chats per session **************************
# *********************************************************************************************************************
print('/' + cust_name +'/' + cust_codenum, flush=True) # for debug, including on Gunicorn (journalctl)
@views.route('/' + cust_name +'/' + cust_codenum, methods = ['GET','POST'])
def demo():  
    print('running LLM demo page')
    print('root path is ...'+views.root_path)
    print('current working directory is '+os.getcwd())

    global ready_for_upload 
    print(ready_for_upload)
    
    llm_response = None

    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    if ready_for_upload: 
        print("I'm in ready_for_upload")
        if request.method == "POST":
            prompt = request.form.get("prompt","").strip()
            
            if prompt:
                try:
                    payload = {
                        "prompt": prompt,
                        "max_tokens":300
                    }

                    response = httpx.post(
                        FASTAPI_CHAT_URL,
                        json=payload,
                        timeout=60.0
                    )
                    response.raise_for_status()

                    data = response.json()
                    llm_response = data.get("text", "No response returned from FASTAPI")
                except httpx.TimeoutException:
                    pass
                    llm_response = "Flask's request to the FASTAPI Backend timed out"
                except httpx.HTTPStatusError as e:
                    llm_response = f"FastAPI returned HTTP {e.response.status_code}: {e.response.text}"
                except Exception as e:
                    llm_response = f"Error contacting backend: {str(e)}"

        return render_template("demo.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users, llm_response=llm_response) # form to enter filename
    else:  
        return render_template("website_not_ready.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users, llm_response=llm_response)

# # *********************************************************************************************************************
# # ************************************** Displays the upload page for job input ***************************************
# # ************************************** Normal entry point for user            ***************************************
# # *********************************************************************************************************************
# print('/' + cust_name +'/' + cust_codenum, flush=True) # for debug, including on Gunicorn (journalctl)
# @views.route('/' + cust_name +'/' + cust_codenum)
# @login_required
# def home():  
#     print('running homepage')
#     print('root path is ...'+views.root_path)
#     print('current working directory is '+os.getcwd())

#     global ready_for_upload 

#     num_users = len(User.query.all())
#     print('The number of users in the database is ' + str(num_users))

#     if ready_for_upload: 
#         return render_template("home.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users) # form to enter filename
#     else:  
#         return render_template("website_not_ready.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users)


# # *********************************************************************************************************************
# # ********** When user enters filename and clicks 'Upload field data' this function is run                *************
# # *** It receives the input job name from the Web form and opens up a subprocess to run TXArray with julia  ***********
# # ********************************************************************************************************************* 
# @views.route('/' + cust_name + '/success' + cust_codenum, methods = ['POST']) 
# def success():   
#     global process_handle
#     global ready_for_upload #now false 
#     global home_directory_path
    
#     if request.method == 'POST':   
#         if request.form['submit_button'] == 'Upload Field Data':

#             os.chdir(home_directory_path) # just in case working directory ("website") has been fiddled with elsewhere

#             # go through input files; save each into home directory (the directory ...WebApp where this .py file lives)
#             # also populate file_names --- list of input .xlsx files
#             # TODO: filter files not ending in .xlsx
#             files = request.files.getlist("files")
#             file_names = []
#             for file in files:
#                 if file.filename != '':
#                     file.save("../input/"+file.filename) #goes to the input directory which lives outside of "website", the current working directory
#                     file_names.append(file.filename)
#                 else:
#                     process_handle = None
#                     ready_for_upload = True
#                     return redirect(url_for('views.home')) #home()
            
#             print('The current working directory is '+os.getcwd())
#             # ensure that /static exists and is empty
#             if os.path.isdir("./static"):
#                 #delete_files_by_cmd("static")
#                 if os.path.isdir("./static/Optimisation_Results"):
#                     delete_files_in_dir("static/Optimisation_Results")
#                 else:
#                     os.chdir("./static")
#                     os.mkdir("./Optimisation_Results")
#                 os.chdir(home_directory_path) #return to home directory - the earlier working directory
#             else:
#                 os.mkdir("./static")
#                 os.chdir("./static")
#                 os.mkdir("./Optimisation_Results")
#                 os.chdir(home_directory_path)

#             # ensure that /lib/Output exists and is empty       
#             if os.path.isdir("./lib/Output"):
#                 os.chdir("./lib")
#                 #delete_files_by_cmd("Output")
#                 delete_files_in_dir("Output")
#                 os.chdir(home_directory_path) #return to home directory - the earlier working directory
#             else:
#                 os.mkdir("./lib/Output")
#                 os.chdir(home_directory_path)

#             if not current_user.is_anonymous:
#                 print('current user is ' + current_user.first_name, flush = True)

#                 if not "website" in os.getcwd(): #initial start of program when running first job, getcwd() is at "TXArray_Web_App"
#                     print('for user_email.txt and first_name.txt, current working directory is at \n:', flush=True)
#                     print(os.getcwd())

#                     with open("./website/user_email.txt", "w") as file:
#                         file.write(current_user.email)

#                     with open("./website/first_name.txt", "w") as file:
#                         file.write(current_user.first_name)

#                 else: #When uploading a new file at the end of first job, getcwd() is at "website"

#                     print('for user_email.txt and first_name.txt, current working directory is at \n:', flush=True)
#                     print(os.getcwd())

#                     with open("./user_email.txt", "w") as file:
#                         file.write(current_user.email)
                    
#                     with open("./first_name.txt", "w") as file:
#                         file.write(current_user.first_name)

#             else:
#                 print('current user is anonymous', flush = True)

#             # create new process and run command equivalent to a shell command that looks like: julia TXArray.jl file1.xlsx file2.xlsx
#             # julia => path to the julia compiler/runtime executable file
#             # juliaprogramme => path to TXArray.jl
#             # "file_names" variable must be unpacked from list: if file_names = ["file1.xlsx", "file2.xlsx"] then *file_names is equivalent to typing file1.xlsx, file2.xlsx
#             # these file_names end up in the ARGS global constant in Julia
#             process_handle = subprocess.Popen([python, vllm_backend_programme, *file_names])  
            
#             ready_for_upload = False
#             return render_template("acknowledgement.html", files = files,  cust_name=cust_name, cust_codenum=cust_codenum, user = current_user) 

# # *********************************************************************************************************************
# # ****************** gets the current output files while TXArray is still running *************************************
# # ****************** or (if run completed) then redirect to results_table function below ******************************
# # *********************************************************************************************************************
# # clicking the refresh button calls this function
# @views.route('/' + cust_name + '/success/running/current_response/'+cust_codenum+'', methods = ['POST', 'GET']) 
# def current_files_table(): 
#     global process_handle
#     global home_directory_path

#     # pressing refresh is a POST action; typing url in address bar is a GET action. Both are valid
#     if request.method == 'POST' or request.method == 'GET': 
#         status = process_handle.poll() # get process return code; None => process has not completed

#         # if process has not completed then display latest output files
#         if status == None: 
#             os.chdir(home_directory_path) # made the project directory.
#             os.chdir("./lib/Output") 

#             file_names_list = os.listdir()

#             # if len(file_names_list) > 0:
#             #     to_be_removed = file_names_list[0]
#             #     file_names_list.remove(to_be_removed)
#             #     print('There was no error in the removal\n')
            
#             files = {} # dictionary with keys=filenames, values=last-modified-time
#             for i in range(0, len(file_names_list)):

#                 path = file_names_list[i]

#                 # if i == 0:
#                 #     if os.path.exists(to_be_removed): #path removal (in the write_to_shapefile() function) could have occured (by a julia parallel process), at the instant you click the REFRESH button
#                 #         lastmod_time = time.ctime(os.path.getmtime(to_be_removed)) # time.ctime converts to "human readable" form.
#                 #         print('Adding back the removed data...\n')
#                 #         file_names_list.insert(i,to_be_removed)
#                 #         files[file_names_list[i]] = lastmod_time
                
#                 try: #path removal (in the write_to_shapefile() function) could have occured (by a julia parallel process), at the instant you click the REFRESH button
#                     lastmod_time = time.ctime(os.path.getmtime(path)) # time.ctime converts to "human readable" form.
#                     files[file_names_list[i]] = lastmod_time
#                 except Exception:
#                     continue #should not assign a now non-existent path to the files-display dictionary. continue to the next filepath name.
                    
#             files = dict(sorted(files.items(), key = lambda item: item[1])) #sort dictionary by value (i.e. last modified time) 
#             files_list2 = []
#             files_list2.append(files) # convert dictionary to list of (filename, time) tuples

#             return render_template("current_files.html", files_list2 = files_list2,  cust_name=cust_name, cust_codenum=cust_codenum, user = current_user)
#         # if the julia process has completed then re-route to results_table() fuction below
#         else:
#             return redirect(url_for('views.results_table')) #url_for had.. 'results_table'

# # *********************************************************************************************************************
# # ********************displays the completed output files after TXArray is done running *******************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/success/running/'+cust_codenum+'', methods = ['POST', 'GET']) 
# def results_table(): 
#     global ready_for_upload
#     global process_handle
#     global home_directory_path

#     num_users = len(User.query.all())
#     print('The number of users in the database is ' + str(num_users))

#     # should normally be called from current_files_table(), but need to guard as user can input any url at any time 
#     if request.method == 'POST' or request.method == 'GET':
#         status = process_handle.poll()
#         if status == None: 
#             return render_template("website_not_ready.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users)  #if status check serves as a guard for displaying results.
#         elif status != None: 
            
#             ready_for_upload = True
#             current_directory = os.getcwd() #assumed to be currently pointing at project directory 

#             #home_directory_path = os.path.dirname(__file__) #The project directory of the running file (main.py)
#             # TODO --- apply changes as in current_files_table()
#             # TODO --- extract similar code from this and current_files_table()

#             if current_directory != home_directory_path:
#                 os.chdir(home_directory_path) # made the project directory.
#                 if os.path.isdir("./static/Optimisation_Results"):
#                     os.chdir("./static/Optimisation_Results")
#             elif current_directory == home_directory_path:
#                 if os.path.isdir("./static/Optimisation_Results"):
#                     os.chdir("./static/Optimisation_Results")
#                 else:
#                     return render_template("website_not_ready.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user, user_size = num_users) #Just in case there is no Optimisation_Results folder existing. Consider removing later. 

#             # results = os.listdir() # get the list of result files in Optimisation_Results directory

#             ## result_folder = list(filter(lambda result:  ".zip" not in result, results))[0] # exclude zip files from list, keep results folder (assumed to be first item remaining)
#             ## os.chdir(result_folder) #change directory to the result folder.

#             file_names_list = os.listdir()
#             #print(file_names_list)

#             files = {}
#             for i in range(0, len(file_names_list)):
#                 path = file_names_list[i]
#                 ti_c = os.path.getmtime(path)
#                 c_ti = time.ctime(ti_c)

#                 files[file_names_list[i]] = c_ti

#             files = dict(sorted(files.items(), key = lambda item: item[1])) #sort by time
            
#             files_list1 = []
#             files_list1.append(files)
#             # print(files_list1)
            
#             os.chdir(home_directory_path) 

#             return render_template('output_files.html', files_list1 = files_list1,  cust_name=cust_name, cust_codenum=cust_codenum, user = current_user)


@views.route('/' + cust_name +'/' + cust_codenum + '/about') #user does not need to be logged in to view the about page
def about():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))
    return render_template('about.html', user=current_user,cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)

@views.route('/' + cust_name +'/' + cust_codenum + '/get_help')  #contact us
def get_help():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))
    return render_template('get_help.html', user = current_user,cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)
 
@views.route('/' + cust_name +'/' + cust_codenum + '/training_and_consultancy')  #changed from get_educated()
def training_and_consultancy():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))
    return render_template('training_and_consultancy.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)

@views.route('/' + cust_name +'/' + cust_codenum + '/community', methods = ['GET', 'POST'])
def community():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    if request.method == "POST":
        note = request.form.get('note')
        if len('note') < 1: #empty note
            flash("note is too short!", category='error')
        else: #there data in the note
            #new_note = Note(data = note, date = datetime.datetime.now(), user_id = current_user.id)
            new_note = Note(data = note, date = datetime.datetime.now())
            db.session.add(new_note)
            db.session.commit()
            flash("note added!", category='success')
    return render_template('community.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)

@views.route('/' + cust_name +'/' + cust_codenum + '/events')
def events():
    num_users = len(User.query.all())
    print('The number of users in the database is ' + str(num_users))

    return render_template('events.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, user_size = num_users)

# @views.route('/' + cust_name +'/' + cust_codenum + '/users-list')
# @login_required
# def users_list():
#     registered_users = User.query.all()

#     print('registered users are ')
#     registered_users
    
#     user_size = len(registered_users)

#     admins = User.query.filter_by(is_admin=True).all()

#     print("admins are ...")
#     admins

#     return render_template('users_list.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum, registered_users = registered_users, user_size = user_size)


# @views.route('/' + cust_name +'/' + cust_codenum + '/user_profile/')
# @login_required
# def user_profile():

#     return render_template('user_profile.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum)

# # @views.route('/' + cust_name +'/' + cust_codenum + '/user_profile/<user_id>')
# # @login_required
# # def change_password(user_id):
# #     user = User.query.filter_by(id=user_id).first()
# #     return render_template('change_password.html', user = current_user, cust_name=cust_name, cust_codenum=cust_codenum)

# # *********************************************************************************************************************
# # ********* Triggered when Download button is pressed                **************************************************
# # *********************************************************************************************************************
# # Note: can't do download straight from HTML download page: need to go via Python to check url contains correct customer name, number
# @views.route('/' + cust_name + '/download/'+cust_codenum+'', methods = ['POST']) 
# def send_results():

#     if request.method == 'POST': 
#         print("The download function pwd is at :"+os.getcwd()) #The website directory is the directoty just above the static folder, not the project version.
#         os.chdir("./static")
        

#         results = os.listdir()
       
#         zip_result = list(filter(lambda result:  ".zip" in result, results))[0] #should be just one item
#         os.chdir("..") #changed back one step to website directory.

#         directory = "./static"
#         return send_from_directory(directory, zip_result) # send file to user's browser

# # *********************************************************************************************************************
# # ********* route for tx web browser icon       ***********************************************************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/'+cust_codenum+'/txicon.ico')
# def txicon():
#     return send_from_directory(os.path.join(views.root_path, 'static'), 'txicon.ico')

# # *********************************************************************************************************************
# # ******************************* Cancels a running job and kills any julia process ***********************************
# # ************ Cancel-job buttons exists in BOTH acknowledgement.html and current_files.html **************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/success/running/current_files/'+cust_codenum+'/stop_job', methods = ['POST']) 
# def cancel_job():
#     global process_handle
#     global ready_for_upload

#     if request.method == 'POST': 
#         should_stop = request.form.get("userInput") # this is the output "are you sure?" dialogue box 
#         if should_stop == "True":
#             for proc in psutil.process_iter():
#                 # check whether the process name matches
#                 if proc.name() == "julia":
#                     proc.kill() #Kills the julia sub-process
#             ready_for_upload = True
#             #return render_template("upload_file.html", cust_name=cust_name, cust_codenum=cust_codenum, user = current_user) # back to entry page
#             return redirect(url_for('views.home'))
#         else:
#             return redirect(url_for('views.current_files_table'))#current_files_table() #not cancelled - take the user to the list of generated files.


# # *********************************************************************************************************************
# # ******************************* makes a user an admin ***************************************************************
# # *********************************************************************************************************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/'+cust_codenum+'/make_admin'+'/<users_id>', methods = ['POST', 'GET']) 
# def make_admin(users_id):

#     if request.method == 'POST': 

#         selected_user_id = int(users_id)
#         print(type(selected_user_id))
#         print('The returned value from make_admin is ...'+str(selected_user_id)) 

#         if current_user.is_admin:

#             user = User.query.get(selected_user_id)

#             user.is_admin = True

#             print(user.is_admin)

#             #create a database session (edit session)
#             db.session.add(user)

#             #update the database (flush any previously uncommited session and commit this current session.)
#             db.session.commit()

#             return redirect(url_for('views.users_list'))#re-take the user to the list of generated files to ensure to ensure the new admin status reflects.
#         else:
#             return redirect(url_for('views.home'))#current_files_table() #not cancelled - take the user to the list of generated files.

# # *********************************************************************************************************************
# # ******************************* removes a user an admin ***************************************************************
# # *********************************************************************************************************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/'+cust_codenum+'/remove_admin'+'/<users_id>', methods = ['POST', 'GET']) 
# def remove_admin(users_id):

#     if request.method == 'POST': 

#         selected_user_id = int(users_id)
#         print(type(selected_user_id))
#         print('The returned value from remove_admin is ...'+str(selected_user_id)) 
         
#         if current_user.is_admin:

#             user = User.query.get(selected_user_id)

#             if user.id is not current_user.id:# An admin user must not remove himself. The organisation could potentially be locked out of their application.

#                 user.is_admin = False

#                 print(user.is_admin)

#                 #create a database session (edit session)
#                 db.session.add(user)

#                 #update the database (flush any previously uncommited session and commit this current session).
#                 db.session.commit()
#                 return redirect(url_for('views.users_list'))#re-take the user to the list of generated files to ensure to ensure the new admin status reflects.
            
#             return redirect(url_for('views.home'))
#         else:
            
#             return redirect(url_for('views.home'))

# # *********************************************************************************************************************
# # ******************************* deletes a user  *********************************************************************
# # *********************************************************************************************************************
# # *********************************************************************************************************************
# @views.route('/' + cust_name + '/'+cust_codenum+'/delete_user'+'/<users_id>', methods = ['POST', 'GET']) 
# def delete_user(users_id):

#     if request.method == 'POST': 

#         selected_user_id = int(users_id)
#         print(type(selected_user_id))
#         print('The returned value from remove_admin is ...'+str(selected_user_id)) 
         
#         if current_user.is_admin:

#             user = User.query.get(selected_user_id)

#             if user.id is not current_user.id:# An admin user must not delete himself. The organisation could potentially be locked out of their application.

#                 user.is_admin = False

#                 print(user.is_admin)

#                 #create a database session (edit session)
#                 db.session.delete(user)

#                 #update the database (flush any previously uncommited session and commit this current session).
#                 db.session.commit()
#                 return redirect(url_for('views.users_list'))#re-take the user to the list of generated files to ensure to ensure the new admin status reflects.
            
#             return redirect(url_for('views.home'))
#         else:
            
#             return redirect(url_for('views.home'))
        
# # *********************************************************************************************************************
# # ******************************* Deletes **everything** in a directory  **********************************************
# # *********************************************************************************************************************
# def delete_files_in_dir(directory):
#     current_path = os.getcwd()

#     print('The current path is: ' + current_path)
#     path_to_directory = current_path + '/' + directory
#     print('The current directory is: '+path_to_directory)
#     files = glob.glob( path_to_directory + '/*')
#     print('files found in static before 1st glob removal are: /n')
#     print(files)
#     for f in files:
#         os.remove(f)

#     if directory == "static/Optimisation_Results":
#         os.chdir("./static")
#         results = os.listdir()

#         print('number of items in static before deletion is: ' + str(len(results)))
#         if len(results) > 1  : #at least a zip (empty) should exist.
#             empty_zips = list(filter(lambda result:  ".zip" in result, results)) #should be just one item
#             for zp in empty_zips:
#                 os.remove(zp)
        
#         results = os.listdir()

#         print('number of items in static directory after deletion is: ' + str(len(os.listdir())))
#         os.chdir("..")


# # When calling the current directory (pwd) should be one level above the directory being emptied
# # the argument "directory" is the name of the directory to be emptied by a shell cmd.
# def delete_files_by_cmd(directory):
#     if os.path.isdir("./"+directory):  # check the target directory actually exists
#         try:
#             subprocess.Popen(["rm", "-rf", directory]) # is *supposed to* forcefully remove the directory & contents
#             if os.path.isdir("./"+directory):   
#                 print('number of items in directory after 1st failed deletion attempt (python file) is: '+str(len(os.listdir(directory))))
#         finally: # Mop up deletion. Will forcefully remove the directory if it still exists.
#             if os.path.isdir("./"+directory): # if directory still exists...
#                 subprocess.Popen(["rm", "-rf", directory]) # second attempt to delete (seems to work even if 1st attempt didn't)
#             if os.path.isdir("./"+directory):   
#                 print('number of items in directory after 2nd failed deletion attempt (python file) is: '+str(len(os.listdir(directory))))
#         if not os.path.isdir("./"+directory): # ensure the directory passed in still exists.
#             os.mkdir("./"+directory) 