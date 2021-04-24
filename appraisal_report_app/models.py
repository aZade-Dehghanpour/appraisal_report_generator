from appraisal_report_app import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), unique = True, nullable = False, primary_key= True)
    first_name= db.Column(db.String(30),  nullable = False)
    last_name = db.Column(db.String(30),  nullable = False)
    username = db.Column(db.String(length=50), unique=True, nullable= False) #use the email as username
    password_hash = db.Column(db.String(length=60), nullable=False)

    @property
    def password(self):
        return self.password
    @password.setter
    def password(self,value):
        self.password_hash = bcrypt.generate_password_hash(value).decode('utf8')

    def check_password(self,attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class PeopleLead(db.Model):
    id= db.Column(db.Integer(), unique = True, nullable = False, primary_key= True)
    email = db.Column(db.String(100), nullable = False)
    first_name= db.Column(db.String(30),  nullable = False)
    last_name = db.Column(db.String(30),  nullable = False)  
    appraisal = db.relationship('Appraisal', backref='appraisal_people_lead', lazy=True)
    employee = db.relationship('Employee', backref='responsible_people_lead', lazy=True)


class Appraisal(db.Model):
    id = db.Column(db.Integer(), unique = True, nullable = False, primary_key= True)
    appraisal_year = db.Column(db.Integer(),  nullable = False)
    appraisal_type = db.Column(db.String(10),  nullable = False) # Mid vs End
    employee = db.Column(db.Integer(), db.ForeignKey('employee.id'))
    people_lead = db.Column(db.Integer(), db.ForeignKey(PeopleLead.id))
    #chart_input = db.relationship('ChartInput', backref='relevant_chart', lazy=True)
    skill_scores = db.relationship('SkillScores', backref='employee_appraisal',lazy=True)


class Employee(db.Model):
    id= db.Column(db.Integer(), unique = True, nullable = False, primary_key= True)
    email = db.Column(db.String(100), nullable = False)
    first_name= db.Column(db.String(30),  nullable = False)
    last_name = db.Column(db.String(30),  nullable = False)    
    department =  db.Column(db.String(20),  nullable = False)
    position =  db.Column(db.String(15),  nullable = False)
    manager_email = db.Column(db.String(100), nullable = False)
    manager_first_name= db.Column(db.String(30),  nullable = False)
    manager_last_name = db.Column(db.String(30),  nullable = False)      
    people_lead = db.Column(db.Integer(), db.ForeignKey(PeopleLead.id))
    appraisal = db.relationship('Appraisal', backref='assessed_employee', lazy=True)


class SkillScores(db.Model):
    id = db.Column(db.Integer(), nullable=False, unique=True, primary_key=True)
    skill_name = db.Column(db.String(30),  nullable = False)
    self_assessed_level = db.Column(db.Integer(), nullable=False)
    peer_assessed_level = db.Column(db.Integer(), nullable=False)
    appraisal = db.Column(db.Integer(),db.ForeignKey('appraisal.id'))
    #skill_scores = db.relationship('SkillLevelScore', backref='assessment_chart',lazy=True)
    