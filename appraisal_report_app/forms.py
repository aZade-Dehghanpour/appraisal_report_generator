from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, RadioField
from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from appraisal_report_app.models import User


class RegisterForm(FlaskForm):
    def validate_username(self,username_to_check):
        user = User.query.filter_by(username = username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')
    
    first_name=StringField(label='First Name:', validators = [Length(min=2, max=30), DataRequired()])
    last_name=StringField(label='Last Name:', validators = [Length(min=2, max=30), DataRequired()])
    username= StringField(label='User Name:', validators = [Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    submit_button = SubmitField(label='Create Account')

class LoginForm(FlaskForm):
    username= StringField(label='User Name:', validators = [DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit_button = SubmitField(label='Sign In')

class UploadFileForm(FlaskForm):
    people_lead_first_name = StringField(label = "First Name ")
    people_lead_last_name = StringField(label = "Last Name ")
    employee_first_name = StringField(label = "First Name ")
    employee_last_name = StringField(label = "Last Name ")
    appraisal_year = SelectField("Appraisal Year", choices = [(0,'Choose Appraisal Year'),(2019,"2019"), (2020,"2020"), ( 2021, "2021")])
    appraisal_type = RadioField("Appraisal Type", choices = [('my','Mid Year  '),('ey', 'End of Year')])
    submit_button = SubmitField(label='Submit')

