import pandas as pd



def get_reminders(data):
    return data['TeacherReminders']


file_descriptions = {
    "Subjects.csv": "List of academic subjects offered at the school.",
    "Curriculum_Table.csv": "Detailed syllabus for each subject across different grades.",
    "StudentExposureHistory.csv": "Records of students' engagement in extracurricular and career-related activities.",
    "student_scores.csv": "Academic scores and assessment results for individual students.",
    "teacher_reminders.csv": "Notifications and reminders set by teachers for upcoming tasks or events.",
    "CalendarEvents.csv": "School calendar with key dates, holidays, and special events.",
    "attendance_records.csv": "Attendance records tracking daily presence for each student.",
    "School_Info_Table.csv": "Information about the school, including address, contact, and administrative details.",
    "StudentProgress.csv": "Student performance records tracking academic and skill growth.",
    "Family.csv": "Family background and contact information for each student.",
    "Assignments.csv": "List of assignments assigned to students by teachers.",
    "SuggestedActivities.csv": "Recommended activities for students based on interests and curriculum goals.",
    "ExtraCurricularActivities.csv": "Catalog of extracurricular opportunities available to students.",
    "Class.csv": "Details about each class, including grade level and assigned teacher.",
    "Teachers.csv": "Directory of teachers with subject expertise and contact information.",
    "test.ipynb": "Jupyter Notebook for testing scripts and code related to the dataset.",
    "TeacherReminders.csv": "Duplicate file with reminders for teachers.",
    "Students.csv": "Student roster with personal and academic information."
    }

def add_file_description(filename: str, description: str):
    """Add or update a file description"""
    global file_descriptions
    file_descriptions[filename] = description
    return file_descriptions


def get_file_info():

    return file_descriptions