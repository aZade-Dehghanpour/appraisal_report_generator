import os

DEBUG = False
UPLOAD_FOLDER = "/Users/az_dnpr/CODE/CODE Spring20/SE and web/se-foundation-final-project/appraisal_report_generator/appraisal_report_app/upload_folder"
SECRET_KEY = os.environ["SECRET_KEY"]   
PUBLIC_IP_ADDRESS= os.environ["PUBLIC_IP_ADDRESS"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]
PROJECT_ID = os.environ["PROJECT_ID"]
INSTANCE_NAME = os.environ["INSTANCE_NAME"]
SQLALCHEMY_ECHO = False
SQLALCHEMY_DATABASE_URI = f"mysql + mysqldb://root:{DB_PASSWORD}@{PUBLIC_IP_ADDRESS}/{DB_NAME}?unix_socket =/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
SQLALCHEMY_TRACK_MODIFICATIONS = True

