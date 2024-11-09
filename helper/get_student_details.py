import pandas as pd
import numpy as np

def get_student_details(data):
    try:
        required_cols = [
            'student_id', 'first_name', 'last_name', 'grade', 
            'performance_level', 'behavioral_notes', 'student_address',
            'parent_contact', 'interests', 'attendance'
        ]
        score_cols = ['Mathematics', 'Science', 'English']
        
        # Validate input data
        if not all(key in data for key in ['attendance_records', 'student_scores', 'Students']):
            raise ValueError("Missing required data frames")
            
        attendance = data['attendance_records'].copy()
        student_scores = data['student_scores'].copy()
        students = data['Students'].copy()
        
        # Ensure student_id exists in all DataFrames
        if not all('student_id' in df.columns for df in [attendance, student_scores, students]):
            raise ValueError("student_id missing in one or more DataFrames")
            
        # Process attendance
        attendance = attendance.replace({'P': 1, 'A': 0, np.nan: 0})
        attendance_cols = [col for col in attendance.columns if col.startswith('Day')]
        attendance['attendance'] = attendance[attendance_cols].mean(axis=1) if attendance_cols else 0
        
        # Perform merges with error handling
        try:
            final = students.merge(
                attendance[['student_id', 'attendance']], 
                on="student_id", 
                how='left'
            ).merge(
                student_scores,
                on="student_id",
                how='left'
            )
        except Exception as e:
            print(f"Merge error: {str(e)}")
            final = students.copy()
            
        # Fill missing values
        for col in required_cols + score_cols:
            if col not in final.columns:
                final[col] = 'Not specified' if col not in score_cols else 75
            elif col in score_cols:
                final[col] = final[col].fillna(75)
            else:
                final[col] = final[col].fillna('Not specified')
                
        return final
        
    except Exception as e:
        print(f"Error in get_student_details: {str(e)}")
        # Return empty DataFrame with required columns
        return pd.DataFrame(columns=required_cols + score_cols)