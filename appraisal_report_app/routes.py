from flask import Flask
from flask import render_template
from appraisal_report_app import app

# configure Flask using environment variables


@app.route('/')
def index():
    return render_template('index.html', page_title="My great website")

