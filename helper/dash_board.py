import pandas as pd
import numpy as np
import json

def progress_overview(data):
    try:
        if 'student_scores' not in data or data['student_scores'].empty:
            return pd.Series()
        
        scores_df = data['student_scores'].copy()
        # Remove any non-numeric columns
        numeric_cols = scores_df.select_dtypes(include=[np.number]).columns
        mean_values = scores_df[numeric_cols].mean()
        return mean_values[1:] if len(mean_values) > 1 else mean_values
    except Exception as e:
        print(f"Error in progress_overview: {str(e)}")
        return pd.Series()
    

def attendance_overview(db):
    try:
        # Read attendance records
        attendance_df = pd.read_csv('school_data_csv/attendance_records.csv')
        
        # Calculate attendance metrics
        day_columns = [f'Day {i}' for i in range(1, 21)]
        class_attendance = {}
        student_attendance = {}
        
        for day in day_columns:
            # Convert P/A to 1/0 and calculate mean for the day
            day_attendance = (attendance_df[day] == 'P').astype(float)
            class_attendance[day] = float(day_attendance.mean())
            student_attendance[day] = float(day_attendance.mean())  # Use same value for now

        # Format the response
        return {
            'avg_class_attendance': json.dumps(class_attendance),
            'avg_stud_attendece': json.dumps(
                {str(i): v for i, v in enumerate(student_attendance.values())}
            )
        }
        
    except Exception as e:
        print(f"Error in attendance_overview calculation: {str(e)}")
        raise

def assignment_completion(df):
    try:
        if "Assignments" not in df or df["Assignments"].empty:
            return 0
            
        assignments_df = df["Assignments"].copy()
        if "completed" not in assignments_df.columns:
            return 0
            
        completed = assignments_df["completed"].fillna(False)
        total = len(completed)
        if total == 0:
            return 0
            
        return (completed == True).sum() / total
    except Exception as e:
        print(f"Error in assignment_completion: {str(e)}")
        return 0

def grade_distribution(df):
    try:
        subj_marks = progress_overview(df)
        if subj_marks.empty:
            return 0
        return subj_marks.mean() if not pd.isna(subj_marks.mean()) else 0
    except Exception as e:
        print(f"Error in grade_distribution: {str(e)}")
        return 0

def current_assignments(data):
    try:
        if "Assignments" not in data or data["Assignments"].empty:
            return pd.DataFrame()
            
        assignments = data["Assignments"].copy()
        if "due_date" not in assignments.columns:
            return pd.DataFrame()
            
        # Convert due_date to datetime
        assignments['due_date'] = pd.to_datetime(assignments['due_date'], errors='coerce')
        assignments = assignments.dropna(subset=['due_date'])
        
        assignments = assignments.sort_values(by="due_date", ascending=True)
        ass = assignments.tail(5).copy()
        ass = ass.reset_index(drop=True)
        ass['assignment_id'] = range(1, len(ass) + 1)
        return ass
    except Exception as e:
        print(f"Error in current_assignments: {str(e)}")
        return pd.DataFrame()
