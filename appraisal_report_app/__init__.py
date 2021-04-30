from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import logging
from gcloud import storage

app = Flask(__name__,instance_relative_config= True)
app.config.from_object('config')
#app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = 'info'
#logging.basicConfig(filename = "/tmp/log.txt", filemode = "w", level= logging.DEBUG, format= "%(asctime)s - %(levelname)s - %(message)s")
client = storage.Client(project = 'appraisal-report-app')
bucket = client.get_bucket('upload_folder_appraisal_report_app')
from appraisal_report_app import routes