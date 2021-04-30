import os
import logging
from google.cloud import storage
from google.auth import app_engine


DEBUG = False
#UPLOAD_FOLDER = 'appraisal_report_app/upload_folder/'
SECRET_KEY = os.getenv("SECRET_KEY") 
PUBLIC_IP_ADDRESS= os.getenv("PUBLIC_IP_ADDRESS")
DB_PASSWORD = os.getenv("DB_PASSWORD")
#ROOT_PASSWORD = os.getenv("ROOT_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
PROJECT_ID = "appraisal-report-app"
INSTANCE_NAME = os.getenv("INSTANCE_NAME")
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")
SQLALCHEMY_ECHO = False
#SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://Report_Generator_App:{DB_PASSWORD}@{PUBLIC_IP_ADDRESS}/{DB_NAME}?unix_socket=/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
SQLALCHEMY_DATABASE_URI = f"mysql+mysqldb://Report_Generator_App:{DB_PASSWORD}@/{DB_NAME}?unix_socket=/cloudsql/{INSTANCE_CONNECTION_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = True
CREDENTIALS = os.getenv("GA_CREDENTIALS")
client = storage.Client.from_service_account_json(CREDENTIALS)
bucket = client.get_bucket('upload_folder_appraisal_report_app')

