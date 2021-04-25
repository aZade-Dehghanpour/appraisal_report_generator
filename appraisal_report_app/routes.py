import os
from werkzeug.utils import secure_filename
from appraisal_report_app import app
from flask import render_template, redirect, url_for, flash, request, send_file
from appraisal_report_app.controllers.excel_sheet import clean_sheet,people_lead_record,employee_record,appraisal_record, skill_assessment_record
from appraisal_report_app.forms import RegisterForm, LoginForm, UploadFileForm
from appraisal_report_app.models import User, SkillScores
from appraisal_report_app import db
from flask_login import login_user, logout_user, login_required
from appraisal_report_app.controllers.record_logs import record_log


@app.route('/', methods=["GET","POST"])
def greet():
    return render_template('greet_page.html')

@app.route('/home', methods=["GET","POST"])
def home_page():
    return render_template('home.html')

@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
def upload_file():

    form = UploadFileForm()

    if form.validate_on_submit():
        if request.method =='POST':
            if request.files:
                excel_file = request.files["excel_file"]
                excel_file_name = secure_filename(excel_file.filename)
                excel_file_path = os.path.join(app.config['UPLOAD_FOLDER'], excel_file_name)
                excel_file.save(excel_file_path)
                flash('successfully uploaded', category = 'success')

                employee_name = form.employee_first_name.data+" "+form.employee_last_name.data
                people_lead_name = form.people_lead_first_name.data+" "+form.people_lead_last_name.data
                appraisal_year = form.appraisal_year.data
                appraisal_type = form.appraisal_type.data

                #clean up the data in excel file
                sheet = clean_sheet(excel_file_path = excel_file_path, employee_name = employee_name)
                #create a record for responsible People Lead in Database
                create_people_lead = people_lead_record(sheet = sheet, people_lead_name = people_lead_name)
                #create record for assessed employee in Database
                create_employee = employee_record(sheet= sheet,employee_name = employee_name, people_lead = create_people_lead)
                #create record for appraisal in Database
                create_appraisal = appraisal_record(appraisal_year=appraisal_year, appraisal_type=appraisal_type,employee = create_employee, people_lead= create_people_lead)
                skill_level_scores = skill_assessment_record (clean_report_data= sheet, employee_name = employee_name, employee_appraisal= create_appraisal)

                return redirect(url_for('create_reports', name = employee_name, year = appraisal_year, appraisal_type = appraisal_type, appraisal=create_appraisal.id))
            else:
                flash('File was not uploaded.', category = 'danger')
                return redirect(url_for('home_page'))

        
    return render_template('upload.html', form = form)
            
@app.route("/reports", methods=['GET', 'POST'])
@login_required
def create_reports():

    name = request.args['name']
    appraisal_id = request.args['appraisal']
    chart_data = SkillScores.query.filter_by(appraisal = appraisal_id).all() #will retun list of objects: list of records
    self_scores = []
    peer_scores = []
    for entry in chart_data:
        self_scores.append((entry.skill_name, entry.self_assessed_level))
        peer_scores.append((entry.skill_name, entry.peer_assessed_level))

        self_labels = [row[0] for row in self_scores]
        self_data = [row[1] for row in self_scores]
        peer_labels = [row[0] for row in peer_scores]
        peer_data = [row[1] for row in peer_scores]

    return render_template("reports.html",name = name, appraisal_id = appraisal_id, 
        self_labels = self_labels,self_data = self_data, peer_labels = peer_labels, peer_data = peer_data )


@app.route('/create_account', methods=["POST","GET"])
def create_account():
    
    form = RegisterForm()
    try:
        
        if form.validate_on_submit():
            try: 
                user_to_create = User(first_name = form.first_name.data, last_name = form.last_name.data, username=form.username.data, 
                password=form.password1.data)
                db.session.add(user_to_create)
                db.session.commit()
                login_user(user_to_create)
                flash(f"Account was successfully created! You are now logged in as:{user_to_create.first_name} {user_to_create.last_name}", category = 'success')
                return redirect(url_for('home_page'))
            except Exception as error_message:
                record_log('ca 1', error_message)
        
        if form.errors !={}:
            try:
                for error_msg in form.errors.values(): #this can be logged
                    flash(f'There was an error with creating a user: {error_msg}', category = 'danger')
                return render_template('create_account.html', form = form)
            except Exception as error_message:
                record_log('ca 2', error_message)

    except Exception as error_message:
        record_log('ca 3', error_message)


@app.route('/login', methods = ['GET','POST'])
def login_page():
    try:
        
        form = LoginForm()
        if form.validate_on_submit():
            try:
                attempted_user = User.query.filter_by(username = form.username.data).first()
                if attempted_user and attempted_user.check_password(attempted_password = form.password.data):
                    login_user(attempted_user)
                    flash(f"You are successfully logged in as:{attempted_user.first_name} {attempted_user.last_name}", category = 'success')
                    return redirect(url_for('home_page'))
            except Exception as error_message:
                record_log('lo 1', error_message)
           
        else:
            try:
                flash('Username and password are not a match. Please try again', category = 'danger')
            except Exception as error_message:
                record_log('lo 2', error_message)
    except Exception as error_message:
        record_log('lo 3', error_message)
    #if form.errors != {}:
    
    return render_template('login_page.html', form=form)
@app.route('/logout', methods=['GET'])
def logout_page():
    logout_user()
    flash('You are logged out.', category = 'info')
    return redirect(url_for('greet'))
