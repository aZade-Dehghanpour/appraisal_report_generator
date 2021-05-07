import pandas as pd
import numpy as np 
from datetime import datetime
from appraisal_report_app.models import Employee, PeopleLead, Appraisal, SkillScores
from appraisal_report_app import db

skills = ['Active Listening', 'Clean Code',
       'Collaboration for Designers', 'Content Operations',
       'Continuous Learning', 'Functional Testing', 'Giving Feedback', 'Java',
       'JavaScript', 'Knowing Our Users', 'Managing for Progress',
       'Prioritization', 'Problem Solving', 'Receiving Feedback',
       'Refactoring', 'Rust/SiGNAL', 'Stakeholder Engagement', 'Teamwork',
       'Technical Writing / Content Development', 'Test Automation',
       'Test Driven Development', 'Working with Unknown Code']
levels = ['Level 0', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']

def clean_sheet(excel_file_path, employee_name):
    excel_file = pd.read_excel(excel_file_path)
    csv_path = "gs://upload_folder_appraisal_report_app/upload_folder/"+employee_name+".csv"
    excel_file.to_csv(csv_path, index = 0, header=False)
    df_feedback = pd.DataFrame(pd.read_csv(csv_path))
    creator = df_feedback.iloc[0][1]
    #report_year = datetime.strptime(df_feedback.iloc[1][1],"%m/%d/%Y").year
    sheet = df_feedback.copy() 
    #employee_name = employee_name
    # Delete the first few rows that contain no useful data
    sheet.drop(sheet.index[0:3], axis=0, inplace= True)
    #delete the current column name row and replace it with the relevant column names
    sheet.rename(columns = sheet.iloc[0], inplace = True)
    sheet.drop(sheet.index[0], inplace = True)
    sheet.reset_index(drop=True, inplace= True)
    sheet.fillna('N/A', inplace = True)
    #delete columns that contain no useful information
    columns_to_keep_loc = []
    for c in sheet.columns:
        if(sheet[c].str.contains('Level', na=False).any()):
            column_location = sheet.columns.get_loc(c)
            columns_to_keep_loc.append(column_location)

    columns_to_keep_loc = np.append(np.arange(6),columns_to_keep_loc)
    sheet=sheet.iloc[:,np.r_[columns_to_keep_loc]]

    # for c in sheet.columns:
    #     if c.find('*')!= -1:
    #         sheet.rename(columns = {c: c[:-1].strip()}, inplace=True)

    return sheet     

def people_lead_record(sheet,people_lead_name):
    row_number = sheet[sheet['Responder Name'] == people_lead_name].index[0]
    first_name = people_lead_name.split(' ')[0]
    last_name = people_lead_name.split(' ')[1]
    email = sheet.iloc[row_number]['Responder Email']
    
    people_lead_to_create = PeopleLead(email = email, first_name = first_name, last_name= last_name)

    db.session.add(people_lead_to_create)
    db.session.commit()
   
    return people_lead_to_create


def employee_record(sheet, employee_name, people_lead):
    
    row_number = sheet[sheet['Responder Name'] == employee_name].index[0]
    first_name = employee_name.split(' ')[0]
    last_name = employee_name.split(' ')[1]
    department = sheet.iloc[row_number]['Responder Department(s)']
    email = sheet.iloc[row_number]['Responder Email']
    position =sheet.iloc[row_number]['Responder Position']
    manager_first_name= sheet.iloc[row_number]['Responder Manager'].split(' ')[0]
    manager_last_name = sheet.iloc[row_number]['Responder Manager'].split(' ')[1]
    manager_email = sheet.iloc[row_number]['Responder Manager Email']
    
    employee_to_create = Employee(email = email, first_name = first_name, last_name= last_name, 
    department= department, position = position,manager_email= manager_email, manager_first_name = manager_first_name,
    manager_last_name= manager_last_name, responsible_people_lead= people_lead)

    db.session.add(employee_to_create)
    db.session.commit()
    
    return employee_to_create


def appraisal_record(appraisal_year, appraisal_type, employee, people_lead):
    appraisal_to_create = Appraisal(appraisal_year = appraisal_year, appraisal_type = appraisal_type, assessed_employee=employee, appraisal_people_lead=people_lead)

    db.session.add(appraisal_to_create)
    db.session.commit()
    
    return appraisal_to_create

def skill_assessment_record(clean_report_data, employee_name,employee_appraisal):    
    skills_assessed = radar_chart_input(clean_report_data, employee_name,employee_appraisal)
    for skill in skills_assessed:
        db.session.add(skill)
        db.session.commit()
    return skills_assessed




def skills_weight_manual():
    path = "appraisal_report_app/Data/skills_manual.csv"
    df_skills_manual = pd.read_csv(path, sep = ';', index_col=0)
    dict_levels_importance_weigth = {}
    dict_skills_level_count = {}

    for i in df_skills_manual.index:
        if df_skills_manual.index.get_loc(i)>0 :
            dict_skills_level_count[i]={}
        for c in df_skills_manual.columns:
            if df_skills_manual.index.get_loc(i)==0:
                dict_levels_importance_weigth[c]=df_skills_manual.loc[i][c]
            else:
                dict_skills_level_count[i][c]= df_skills_manual.loc[i][c]

        
    return (dict_levels_importance_weigth, dict_skills_level_count)
        

def evaluate_skills(clean_report_data):
    """creates a dictionary where keys are the skills and values are dataframes that record evalution on that skill"""
    
    columns = clean_report_data.columns
    index = clean_report_data.index
    dict_individual_skill_evaluation = {}
    dict_all_skills_evaluation = {}

    for c in columns:
        if c.find('*')!=-1:
            c_new = c[:c.find('*')].strip()
            for i in index:
                content = clean_report_data.loc[i][c]
                level_count = []
                for level in levels:
                    level_count.append(content.count(level))
                dict_individual_skill_evaluation[clean_report_data.loc[i][0]] = pd.Series(data = level_count, index = levels) 
                df_skill_evaluation = pd.DataFrame(dict_individual_skill_evaluation).transpose()
                df_skill_evaluation = df_skill_evaluation[(df_skill_evaluation!=0).any(axis=1)].copy()
        
            dict_all_skills_evaluation[c_new]= df_skill_evaluation 

    return dict_all_skills_evaluation


def weigthed_skill_evaluation(clean_report_data, employee_name):
    dict_weigthed_skill_evaluation= {}

    skills_evaluation = evaluate_skills(clean_report_data)
    levels_importance_weigth , skills_level_count = skills_weight_manual()


    for se in skills_evaluation:
        skill = se
        df_weigthed_skill_evaluation= skills_evaluation[skill].copy()

        for i in df_weigthed_skill_evaluation.index:
            for c in df_weigthed_skill_evaluation.columns:
                df_weigthed_skill_evaluation.loc[i][c] = df_weigthed_skill_evaluation.loc[i][c]*levels_importance_weigth[c]
            
            df_self_assessment = df_weigthed_skill_evaluation.loc[employee_name].copy()
            self_assessment_score=df_self_assessment.sum()
            df_peer_assessment = df_weigthed_skill_evaluation.drop(employee_name, axis=0)
            peer_count = len(df_weigthed_skill_evaluation.index)-1
            peer_assessment_score_average = df_peer_assessment.sum().sum()/peer_count
            
            dict_weigthed_skill_evaluation[skill]=pd.Series(data = [df_weigthed_skill_evaluation.copy(),
            employee_name, self_assessment_score,peer_assessment_score_average], 
            index = ["weighted Evaluation", "Assessed Employee", "Self Assessment Score", 
            "Peer Assessment Score Average"])
            
            

    return dict_weigthed_skill_evaluation.copy()

    
def score_treshhold_by_skill(clean_report_data): #a dictionary for each skill {skill: {level1 : "", level 2: "", ...}}
        
    levels_importance_weigth , skills_level_count = skills_weight_manual()
    skills_evaluation = evaluate_skills(clean_report_data)
    dict_score_treshhold = {}

    for skill in skills_evaluation:
        levels_treshhold, i = [] , 0
        for level in skills_level_count[skill]:
            if i == 0:
                levels_treshhold.append(skills_level_count[skill][level]*levels_importance_weigth[level])
            else:
                levels_treshhold.append(skills_level_count[skill][level]*levels_importance_weigth[level]+levels_treshhold[i-1])
                    
            i= i+1
        dict_score_treshhold[skill] = pd.Series(data = levels_treshhold, index = ['Level 0', 'Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5'])
        
    return dict_score_treshhold

           
def radar_chart_input(clean_report_data, employee_name,employee_appraisal):
        

    levels_numeric_value = {'Level 0':0, 'Level 1':1, 'Level 2':2, 'Level 3':3, 'Level 4':4, 'Level 5':5}
    dict_radar_chart_input = {}
    all_skills_scores = []

    dict_weigthed_skill_evaluation = weigthed_skill_evaluation (clean_report_data, employee_name)
    dict_score_treshhold = score_treshhold_by_skill(clean_report_data)

    for skill in dict_weigthed_skill_evaluation:
        level_score = np.flip(dict_score_treshhold[skill].keys().values)
        for i, level in enumerate(level_score):
            if dict_weigthed_skill_evaluation[skill]["Self Assessment Score"] == dict_score_treshhold[skill][level]:
                self_assessed_level = levels_numeric_value[level]
                break
                    
            elif dict_score_treshhold[skill][level_score[i+1]] < dict_weigthed_skill_evaluation[skill]["Self Assessment Score"] < dict_score_treshhold[skill][level]:
                self_assessed_level = levels_numeric_value[level_score[i+1]]
                break

        for i, level in enumerate(level_score):
                
            if dict_weigthed_skill_evaluation[skill]["Peer Assessment Score Average"] == dict_score_treshhold[skill][level]:
                peer_assessed_level = levels_numeric_value[level]
                break
            elif dict_score_treshhold[skill][level_score[i+1]]<dict_weigthed_skill_evaluation[skill]["Peer Assessment Score Average"]< dict_score_treshhold[skill][level]:
                peer_assessed_level = levels_numeric_value[level_score[i+1]]
                break
        
        assessed_skill = SkillScores(skill_name = skill, self_assessed_level = self_assessed_level, peer_assessed_level = peer_assessed_level,
        employee_appraisal = employee_appraisal)
        

        all_skills_scores.append(assessed_skill)

        dict_radar_chart_input[skill] = pd.Series(data = [self_assessed_level,peer_assessed_level], index = ["Self Assessed Level", "Peer Assessed Level"])
            
    #return dict_radar_chart_input
    return all_skills_scores


        