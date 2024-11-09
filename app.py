from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from helper import dash_board , upload_files , Bot ,load_data , prompts , get_student_details , teacher_dashboard
import json
import os
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime, timedelta
import uuid
from helper import time_tabel_help

uploaded_ids = [
 'files/l15ouwfs2c79',
 'files/ab5tuykcu7vw',
 'files/qh3reuofe4zi',
 'files/15vz1zkw54nn',
 'files/33u35bztzsnw',
 'files/ylothjvklins',
 'files/3rk6h1ebnq4e',
 'files/mk3n5cjohs5o',
 'files/3be8h2qyr74w',
 'files/77y54gm68bil',
 'files/a7l029nex97j',
 'files/dtpvdkloljhr',
 'files/c8do90cllba3',
 'files/liiknctv0tl5',
 'files/ouoiyb24qm02',
 'files/wjdop2jhdq1o',
 'files/vi269vnqq23w',
 'files/peirhymf1z4z',
 'files/dxeo4jo79sd',
 'files/z0tbskqh0tp3',
 'files/gmf7x6dk9m7l']

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "supports_credentials": True
    }
})

UPLOAD_FOLDER = 'school_data_csv'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'csv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

## Load data

updated_db = load_data.load_data('school_data_csv'  )

u_files = upload_files.get_files(uploaded_ids)

#bots preparation
bots = { "time-tabel": Bot.get_bot(files = u_files , system_prompt=prompts.create_prompt(type = 'time-table'))}

# Add a general chat bot instance
general_chat_bot = Bot.get_bot( files=u_files ,  system_prompt="You are a helpful AI assistant for teachers, specializing in education and assignment creation.")

# Add timetable bot instance


# Add after other bot initializations

def log_activity(activity_type, description, user_type="teacher"):
    try:
        activities_file = 'school_data_csv/activities.csv'
        
        # Create activities file if it doesn't exist
        if not os.path.exists(activities_file):
            pd.DataFrame({
                'timestamp': [],
                'activity_type': [],
                'description': [],
                'user_type': []
            }).to_csv(activities_file, index=False)
        
        activities_df = pd.read_csv(activities_file)
        
        new_activity = pd.DataFrame([{
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'activity_type': activity_type,
            'description': description,
            'user_type': user_type
        }])
        
        activities_df = pd.concat([activities_df, new_activity], ignore_index=True)
        activities_df.to_csv(activities_file, index=False)
        
    except Exception as e:
        print(f"Error logging activity: {str(e)}")

@app.route('/')
def home():
    db = load_data.load_data('school_data_csv' , load_json = True)
    return jsonify(db)

@app.route('/dashboard/progress_overview')
def progress_overview():
    try:
        data = dash_board.progress_overview(updated_db)
        # Convert to dictionary first
        data_dict = data.to_dict()
        # Transform into the format needed by the chart
        formatted_data = [
            {
                "subject": subject,
                "score": float(score),
                "average": 75.0  # You can adjust this or get real average
            }
            for subject, score in data_dict.items()
        ]
        return jsonify(formatted_data)
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard/attendance_overview')
def attendance_overview():
    try:
        data = dash_board.attendance_overview(updated_db)
        
        # Parse the JSON strings within the data
        class_attendance = json.loads(data['avg_class_attendance'])
        student_attendance = json.loads(data['avg_stud_attendece'])
        
        # Format the data for the frontend
        formatted_data = []
        days = sorted(class_attendance.keys())  # Sort days to ensure correct order
        
        for i, day in enumerate(days):
            try:
                class_avg = float(class_attendance[day])
                student_avg = float(student_attendance[str(i)])
                
                formatted_data.append({
                    "label": day,
                    "classAverage": round(class_avg * 100, 2),
                    "attendance": round(student_avg * 100, 2)
                })
            except (ValueError, TypeError) as e:
                print(f"Error processing day {day}: {str(e)}")
                formatted_data.append({
                    "label": day,
                    "classAverage": 0,
                    "attendance": 0
                })
        
        return jsonify(formatted_data)
    except Exception as e:
        print(f"Error in attendance_overview: {str(e)}")
        # Return default data structure
        return jsonify([
            {"label": f"Day {i+1}", "classAverage": 0, "attendance": 0}
            for i in range(20)
        ])

@app.route('/dashboard/overall')
def assignment_completion():
    return jsonify({
        "curriculum_progress": 75.0,  # You can modify these values based on your actual data
        "assignment_completion": dash_board.assignment_completion(updated_db),
        "grade_average": round(dash_board.grade_distribution(updated_db) , 2)
    })

@app.route('/dashboard/current_assignments')
def current_assignments():
    try:
        df = dash_board.current_assignments(updated_db)
        
        # Convert DataFrame to records format
        assignments = df.to_dict('records')
        
        # Ensure boolean values are properly formatted
        for assignment in assignments:
            assignment['completed'] = bool(assignment['completed'])
            
        return jsonify(assignments)
    except Exception as e:
        print(f"Error in current_assignments: {str(e)}")
        return jsonify([]), 500

@app.route('/dashboard/recent_activity')
def recent_activity():
    try:
        activities_file = 'school_data_csv/activities.csv'
        if not os.path.exists(activities_file):
            return jsonify([])
            
        activities_df = pd.read_csv(activities_file)
        activities_df = activities_df.sort_values('timestamp', ascending=False).head(10)
        
        return jsonify(activities_df.to_dict('records'))
    except Exception as e:
        print(f"Error fetching recent activities: {str(e)}")
        return jsonify([])

def get_json(data):

    start = data.find('{')
    end = data.rfind('}')
    return json.dumps(data[start:end+1])
@app.route('/time_tabel')
def time_tabrl():
    ques = prompts.questions(type = 'time-tabel')
    bot= bots["time-tabel"]
    print(ques)
    result = bot.send_message(ques)
    return get_json( result.text)

@app.route('/students', methods=['GET'])
def get_students():
    try:
        # Get student data from the database
        student_df = pd.read_csv('school_data_csv/Students.csv')
        
        # Format the response data
        students = []
        for _, row in student_df.iterrows():
            students.append({
                'student_id': int(row['student_id']),
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'grade': str(row['grade']),
                'performance_level': row['performance_level']
            })
        
        return jsonify(students)
    except Exception as e:
        print(f"Error fetching students: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/students', methods=['POST'])
def students():
    if request.method == 'GET':
        return get_student_details.get_student_details(updated_db).to_json()
    elif request.method == 'POST':
        try:
            data = request.json
            # Read existing student data
            df = updated_db['student_details'].copy()
            
            # Generate new student ID
            new_id = df['student_id'].max() + 1
            
            # Create new student entry
            new_student = {
                'student_id': new_id,
                'first_name': data['name'].split()[0],
                'last_name': data['name'].split()[-1] if len(data['name'].split()) > 1 else '',
                'grade': int(data['class'].replace('Grade ', '')),
                'performance_level': data['performanceLevel'],
                'behavioral_notes': data.get('lastRemark', 'New student'),
                'student_address': data.get('address', 'Not provided'),
                'parent_contact': data.get('contactNumber', '0'),
                'interests': ', '.join(data.get('interests', [])),
                'attendance': 1.0,  # Initial attendance
            }
            
            # Add academic scores (initialize with average values)
            for subject in ['Mathematics', 'Science', 'English']:
                new_student[subject] = 75  # Default score
            
            # Append to dataframe
            df.loc[len(df)] = new_student
            
            # Update the database
            updated_db['student_details'] = df
            
            # Also create attendance record
            attendance_df = pd.read_csv('school_data_csv/attendance_records.csv')
            new_attendance = pd.DataFrame([{'student_id': new_id, **{f'Day {i+1}': 'P' for i in range(20)}}])
            attendance_df = pd.concat([attendance_df, new_attendance], ignore_index=True)
            attendance_df.to_csv('school_data_csv/attendance_records.csv', index=False)
            
            # Log the activity
            log_activity(
                'student_added',
                f"New student {data['name']} added to Grade {data['class']}"
            )
            
            return jsonify({'success': True, 'student_id': new_id})
            
        except Exception as e:
            print(f"Error adding student: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/t_d/documents')
def documents():
    return json.dumps(teacher_dashboard.get_file_info())

@app.route('/t_d/get_reminders')
def get_reminders():
    return teacher_dashboard.get_reminders(updated_db).to_json()
    
@app.route('/t_d/upload_document', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            description = request.form.get('description', '')
            
            # Save file
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # Update file descriptions
            teacher_dashboard.add_file_description(filename, description)
            
            # Log activity
            log_activity(
                'file_uploaded',
                f"New file '{filename}' uploaded with description: {description}"
            )
            
            return jsonify({
                'message': 'File uploaded successfully',
                'filename': filename,
                'description': description
            })
            
        return jsonify({'error': 'File type not allowed'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/t_d/preview_document/<filename>')
def preview_document(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
            
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            preview_data = {
                'type': 'csv',
                'headers': df.columns.tolist(),
                'rows': df.head().to_dict('records')
            }
        else:
            with open(file_path, 'r') as file:
                content = file.read()
                preview_data = {
                    'type': 'text',
                    'content': content
                }
                
        return jsonify(preview_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/t_d/calendar_events')
def calendar_events():
    try:
        df = pd.read_csv('school_data_csv/CalendarEvents.csv')
        events = df.to_dict('records')
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/assignment', methods=['POST'])
def assignment():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['type', 'topic', 'teacherNotes']
        if not all(key in data for key in required_fields):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Get student information if personalized
        student_info = ""
        if data.get('studentIds') and data['studentIds'] != "all":
            try:
                student_df = pd.read_csv('school_data_csv/Students.csv')
                selected_students = student_df[student_df['student_id'].isin(data['studentIds'])]
                
                student_info = "\nPersonalized for students:\n"
                for _, student in selected_students.iterrows():
                    student_info += f"- {student['first_name']} {student['last_name']}: Grade {student['grade']}, Performance Level: {student['performance_level']}\n"
            except Exception as e:
                print(f"Error getting student info: {str(e)}")
                student_info = "\nNote: Student information could not be loaded."

        # Format question types for the prompt
        question_types = data.get('questionTypes', [])
        if isinstance(question_types, list):
            question_types = ', '.join(question_types)

        # Create base prompt
        base_prompt = f"""Create a {data['type']} for students on the topic: {data['topic']}.
            Additional requirements:
            - Question count: {data.get('questionCount', '5')}
            - Question types: {question_types}
            - Teacher's notes: {data.get('teacherNotes', '')}
            - Schema: {data.get('schema', 'standard')}
            {student_info}

            Please format the {data['type'].lower()} with clear sections, questions, and if applicable, answers.
            If this is a personalized assignment, tailor the difficulty and content based on the students' grade levels and performance."""

        # Get or create a bot for this type of assignment
        bot_key = f"{data['type'].lower()}_bot"
        if bot_key not in bots:
            bots[bot_key] = Bot.get_bot(files=u_files)
        
        # Generate the content
        result = bots[bot_key].send_message(base_prompt)
        
        if not result or not result.text:
            return jsonify({
                'success': False,
                'error': 'Failed to generate content'
            }), 500

        # Log activity
        log_activity(
            'assignment_created',
            f"New {data['type']} assignment created on topic: {data['topic']}"
        )

        return jsonify({
            'success': True,
            'content': result.text
        })

    except Exception as e:
        print(f"Error creating assignment: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def update_curriculum_progress(curriculum_df, topic):
    # Find matching curriculum items and update progress
    mask = curriculum_df['topic'].str.contains(topic, case=False, na=False)
    if mask.any():
        curriculum_df.loc[mask, 'status'] = 'In Progress'
        curriculum_df.loc[mask, 'last_updated'] = datetime.now().strftime('%Y-%m-%d')
    return curriculum_df

@app.route('/t_d/add_reminder', methods=['POST'])
def add_reminder():
    try:
        data = request.json
        df = pd.read_csv('school_data_csv/TeacherReminders.csv')
        
        new_id = int(df['reminder_id'].max() + 1) if not df.empty else 1
        new_reminder = pd.DataFrame([{
            'reminder_id': new_id,
            'teacher_id': 1,
            'reminder_text': data['title'],
            'reminder_date': data['date'],
            'priority_level': data.get('priority', 'Medium'),
            'activity': 'Custom Reminder',
            'learning_materials': ''
        }])
        
        df = pd.concat([df, new_reminder], ignore_index=True)
        df.to_csv('school_data_csv/TeacherReminders.csv', index=False)
        
        # Log activity
        log_activity(
            'reminder_added',
            f"New reminder added: {data['title']} for {data['date']}"
        )

        return jsonify({
            'message': 'Reminder added successfully',
            'reminder': {
                'reminder_id': new_id,
                'reminder_text': data['title'],
                'reminder_date': data['date'],
                'priority_level': data.get('priority', 'Medium')
            }
        })
    except Exception as e:
        print(f"Error adding reminder: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/t_d/edit_reminder', methods=['PUT'])
def edit_reminder():
    try:
        data = request.json
        df = pd.read_csv('school_data_csv/TeacherReminders.csv')
        
        mask = df['reminder_id'] == data['id']
        if not mask.any():
            return jsonify({'error': 'Reminder not found'}), 404
            
        df.loc[mask, 'reminder_text'] = data['title']
        df.loc[mask, 'reminder_date'] = data['date']
        df.loc[mask, 'priority_level'] = data.get('priority', 'Medium')
        
        df.to_csv('school_data_csv/TeacherReminders.csv', index=False)
        
        return jsonify({'message': 'Reminder updated successfully'})
    except Exception as e:
        print(f"Error updating reminder: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/t_d/delete_reminder/<int:reminder_id>', methods=['DELETE'])
def delete_reminder(reminder_id):
    try:
        df = pd.read_csv('school_data_csv/TeacherReminders.csv')
        if reminder_id not in df['reminder_id'].values:
            return jsonify({'error': 'Reminder not found'}), 404
            
        df = df[df['reminder_id'] != reminder_id]
        df.to_csv('school_data_csv/TeacherReminders.csv', index=False)
        
        return jsonify({'message': 'Reminder deleted successfully'})
    except Exception as e:
        print(f"Error deleting reminder: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/attendance/<int:student_id>', methods=['PUT'])
def update_attendance(student_id):
    try:
        data = request.json
        attendance_df = pd.read_csv('school_data_csv/attendance_records.csv')
        student_df = pd.read_csv('school_data_csv/Students.csv')
        
        # Ensure student_id exists in both dataframes
        if student_id not in student_df['student_id'].values:
            return jsonify({'error': 'Student not found'}), 404
            
        if student_id not in attendance_df['student_id'].values:
            # Create new attendance record if it doesn't exist
            new_attendance = pd.DataFrame([{
                'student_id': student_id,
                **{f'Day {i+1}': 'P' for i in range(20)}
            }])
            attendance_df = pd.concat([attendance_df, new_attendance], ignore_index=True)
        
        student_name = f"{student_df[student_df['student_id'] == student_id]['first_name'].iloc[0]} {student_df[student_df['student_id'] == student_id]['last_name'].iloc[0]}"
        
        # Update attendance for the specific student
        student_row = attendance_df['student_id'] == student_id
        changes_made = []
        
        for day, value in enumerate(data['attendance'], 1):
            day_col = f'Day {day}'
            if day_col in attendance_df.columns:
                old_value = attendance_df.loc[student_row, day_col].iloc[0]
                new_value = 'P' if value else 'A'
                if old_value != new_value:
                    changes_made.append(f"Day {day}: {old_value} → {new_value}")
                attendance_df.loc[student_row, day_col] = new_value

        if changes_made:
            log_activity(
                'attendance_updated',
                f"Updated attendance for {student_name}: {', '.join(changes_made)}"
            )
        
        # Calculate and update overall attendance
        present_days = sum(1 for value in data['attendance'] if value)
        total_days = len(data['attendance'])
        overall_attendance = present_days / total_days if total_days > 0 else 0
        
        # Update overall attendance in student details
        student_df.loc[student_df['student_id'] == student_id, 'attendance'] = overall_attendance
        
        # Save both files
        attendance_df.to_csv('school_data_csv/attendance_records.csv', index=False)
        student_df.to_csv('school_data_csv/Students.csv', index=False)
        
        return jsonify({
            'success': True,
            'attendance': overall_attendance
        })
        
    except Exception as e:
        print(f"Error updating attendance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/performance/<int:student_id>', methods=['PUT'])
def update_performance(student_id):
    try:
        data = request.json
        df = pd.read_csv('school_data_csv/Students.csv')
        
        student_name = f"{df[df['student_id'] == student_id]['first_name'].iloc[0]} {df[df['student_id'] == student_id]['last_name'].iloc[0]}"
        old_level = df.loc[df['student_id'] == student_id, 'performance_level'].iloc[0]
        
        # Update performance level
        df.loc[df['student_id'] == student_id, 'performance_level'] = data['level']
        
        # Log activity
        log_activity(
            'performance_updated',
            f"Performance level updated for {student_name}: {old_level} → {data['level']}"
        )
        
        updated_db['Students'] = df
        df.to_csv('school_data_csv/Students.csv', index=False)
        
        return jsonify({'success': True})
        
    except Exception as e:
        print(f"Error updating performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/remarks/<int:student_id>', methods=['GET', 'POST'])
def handle_remarks(student_id):
    try:
        remarks_file = 'school_data_csv/student_remarks.csv'
        
        # Create remarks file if it doesn't exist
        if not os.path.exists(remarks_file):
            pd.DataFrame({
                'student_id': [],
                'remark_text': [],
                'date': [],
                'time': []
            }).to_csv(remarks_file, index=False)
        
        remarks_df = pd.read_csv(remarks_file)
        
        if request.method == 'GET':
            student_remarks = remarks_df[remarks_df['student_id'] == student_id].to_dict('records')
            return jsonify(student_remarks)
            
        elif request.method == 'POST':
            data = request.json
            new_remark = pd.DataFrame([{
                'student_id': student_id,
                'remark_text': data['text'],
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': datetime.now().strftime('%H:%M')
            }])
            
            remarks_df = pd.concat([remarks_df, new_remark], ignore_index=True)
            remarks_df.to_csv(remarks_file, index=False)
            
            # Update last remark in student details
            student_df = pd.read_csv('school_data_csv/Students.csv')
            student_df.loc[student_df['student_id'] == student_id, 'behavioral_notes'] = data['text']
            student_df.to_csv('school_data_csv/Students.csv', index=False)

            student_name = f"{student_df[student_df['student_id'] == student_id]['first_name'].iloc[0]} {student_df[student_df['student_id'] == student_id]['last_name'].iloc[0]}"
            
            # Log activity
            log_activity(
                'remark_added',
                f"New remark added for {student_name}: {data['text'][:50]}..."
            )

            return jsonify({'success': True})
            
    except Exception as e:
        print(f"Error handling remarks: {str(e)}")
        return jsonify({'error': str(e)}), 500

def analyze_timetable(timetable_data):
    """Analyze timetable for workload balance and generate suggestions"""
    try:
        workload = {}
        subjects_per_day = {}
        
        for day, periods in timetable_data.items():
            subjects_per_day[day] = len([p for p in periods if p])
            for subject in periods:
                if subject:
                    workload[subject] = workload.get(subject, 0) + 1
        
        # Calculate balance metrics
        avg_subjects_per_day = sum(subjects_per_day.values()) / len(subjects_per_day) if subjects_per_day else 0
        workload_variance = statistics.variance(workload.values()) if workload else 0
        
        # Generate suggestions
        suggestions = []
        if workload_variance > 2:
            suggestions.append("Consider redistributing subjects more evenly across the week")
        if any(count > 6 for count in workload.values()):
            suggestions.append("Some subjects may have too many periods per week")
        if avg_subjects_per_day < 4:
            suggestions.append("Consider adding more subjects per day for better engagement")
            
        return {
            "workload": workload,
            "balance": {
                "avg_subjects_per_day": avg_subjects_per_day,
                "workload_variance": workload_variance
            },
            "suggestions": suggestions
        }
    except Exception as e:
        print(f"Error analyzing timetable: {str(e)}")
        return None

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        timetable_data = data.get('timetableData')
        chat_type = data.get('type')

        if not messages:
            return jsonify({'error': 'No messages provided'}), 400

        last_message = messages[-1]['text']
        
        # Use specific prompt based on chat type
        if chat_type == 'timetable':
            context = f"""You are a helpful AI assistant specializing in school timetable management.
            Current timetable: {json.dumps(timetable_data)}
            Please help with: {last_message}"""
        else:
            context = f"You are a helpful teaching assistant. Query: {last_message}"

        response = general_chat_bot.send_message(context)
        
        # Save chat history
        save_chat_history(messages + [{
            'text': response.text,
            'sender': 'bot',
            'time': datetime.now().isoformat()
        }])

        return jsonify({
            'response': response.text,
            'role': 'ai'
        })
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def save_chat_history(messages):
    """Save chat history to a file"""
    try:
        chat_file = 'school_data_csv/chat_history.json'
        existing_chats = []
        
        if os.path.exists(chat_file):
            with open(chat_file, 'r') as f:
                existing_chats = json.load(f)
                
        existing_chats.append({
            'timestamp': datetime.now().isoformat(),
            'messages': messages
        })
        
        # Keep only last 100 chats
        existing_chats = existing_chats[-100:]
        
        with open(chat_file, 'w') as f:
            json.dump(existing_chats, f)
            
    except Exception as e:
        print(f"Error saving chat history: {str(e)}")

@app.route('/chat/<int:student_id>', methods = ['POST'])
def student_chat(student_id):
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        student = updated_db['Students']
        student = student[student['student_id'] == student_id]
        if student.empty:
            return jsonify({'error': 'Student not found'}), 404
        # Get student context
        context = f"""
            You are a helpful personalized assistent , where you are giving answrers to a teacher
            think you are a personal mentee for the studnet
            and you are  hear to help with the teacher and gave monitering to the student 
            with id == {student_id} and {student}
            based on the avaible data answer to the following question to the teacher in a polite way .
            {message}
        """
        print(context)
        # Use the bot with student context
        response = general_chat_bot.send_message(context)
        
        return jsonify({
            'response': response.text,
            'role': 'ai'
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        # First check if student exists in the database
        student_df = pd.read_csv('school_data_csv/Students.csv')  # Changed from student_details.csv
        student_mask = student_df['student_id'] == student_id
        
        if not student_mask.any():
            return jsonify({'error': 'Student not found'}), 404
            
        # Get student name for logging before deletion
        student_name = f"{student_df.loc[student_mask, 'first_name'].iloc[0]} {student_df.loc[student_mask, 'last_name'].iloc[0]}"
        
        # Remove student from the main database
        student_df = student_df[~student_mask]
        
        # Save to CSV
        student_df.to_csv('school_data_csv/Students.csv', index=False)  # Changed from student_details.csv
        
        # Update attendance records if they exist
        try:
            attendance_df = pd.read_csv('school_data_csv/attendance_records.csv')
            attendance_df = attendance_df[attendance_df['student_id'] != student_id]
            attendance_df.to_csv('school_data_csv/attendance_records.csv', index=False)
        except Exception as e:
            print(f"Warning: Could not update attendance records: {str(e)}")
        
        # Update remarks if they exist
        try:
            remarks_file = 'school_data_csv/student_remarks.csv'
            if os.path.exists(remarks_file):
                remarks_df = pd.read_csv(remarks_file)
                remarks_df = remarks_df[remarks_df['student_id'] != student_id]
                remarks_df.to_csv(remarks_file, index=False)
        except Exception as e:
            print(f"Warning: Could not update remarks: {str(e)}")
        
        # Update the in-memory database
        updated_db['Students'] = student_df  # Changed from student_details
        
        # Log the deletion
        log_activity(
            'student_deleted',
            f"Student {student_name} (ID: {student_id}) has been removed"
        )
            
        return jsonify({
            'success': True,
            'message': f'Successfully deleted student {student_name}'
        })
        
    except Exception as e:
        print(f"Error deleting student: {str(e)}")
        return jsonify({
            'error': f'Failed to delete student: {str(e)}'
        }), 500

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        data = request.json
        student_df = pd.read_csv('school_data_csv/Students.csv')
        
        student_mask = student_df['student_id'] == student_id
        old_name = f"{student_df.loc[student_mask, 'first_name'].iloc[0]} {student_df.loc[student_mask, 'last_name'].iloc[0]}"
        old_grade = f"Grade {student_df.loc[student_mask, 'grade'].iloc[0]}"
        
        changes = []
        
        # Update student info
        if 'name' in data:
            first_name, last_name = data['name'].split(' ', 1)
            student_df.loc[student_mask, 'first_name'] = first_name
            student_df.loc[student_mask, 'last_name'] = last_name
            changes.append(f"name changed from '{old_name}' to '{data['name']}'")
        
        if 'class' in data:
            new_grade = int(data['class'].replace('Grade ', ''))
            student_df.loc[student_mask, 'grade'] = new_grade
            changes.append(f"class changed from '{old_grade}' to '{data['class']}'")
            
        if changes:
            log_activity(
                'student_updated',
                f"Student details updated: {'; '.join(changes)}"
            )
            
        student_df.to_csv('school_data_csv/Students.csv', index=False)
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error updating student: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/timetable', methods=['GET'])
def get_timetable():
    try:
        timetable_data = time_tabel_help.load_timetable()
        if not timetable_data:
            return jsonify({'error': 'Failed to load timetable data'}), 500
        return jsonify(timetable_data)
    except Exception as e:
        print(f"Error loading timetable: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/timetable', methods=['PUT']) 
def update_timetable():
    try:
        data = request.json
        if not data or not isinstance(data, dict):
            return jsonify({'error': 'Invalid data format'}), 400
            
        # Validate required fields
        required_fields = ['timeSlots', 'weekDays', 'subjects', 'subjectColors', 'timetableData']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
            
        success = time_tabel_help.save_timetable(data)
        if not success:
            return jsonify({'error': 'Failed to save timetable'}), 500
            
        # Log activity
        log_activity(
            'timetable_updated',
            f"Timetable has been updated"
        )
        
        # Return the updated data along with success status
        return jsonify({
            'success': True,
            'timetableData': data['timetableData'],
            'subjects': data['subjects'],
            'timeSlots': data['timeSlots'],
            'weekDays': data['weekDays'],
            'subjectColors': data['subjectColors']
        })
    except Exception as e:
        print(f"Error updating timetable: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add new routes
@app.route('/timetable/ai/assist', methods=['POST'])
def timetable_ai_assist():
    try:
        data = request.json
        query = data.get('query')
        current_timetable = data.get('currentTimetable', {})
        request_type = data.get('requestType')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
            
        # Create bot instance
        timetable_bot = time_tabel_help.create_timetable_bot(query, current_timetable, files=u_files)
        
        if request_type == 'suggest_changes':
            suggested_changes, message = time_tabel_help.suggest_timetable_changes(query, current_timetable)
            return jsonify({
                'response': message,
                'suggestedChanges': suggested_changes,
                'analysis': time_tabel_help.analyze_timetable(current_timetable)
            })
        else:
            # Regular analysis
            response = timetable_bot.send_message(query)
            return jsonify({
                'response': response.text,
                'analysis': time_tabel_help.analyze_timetable(current_timetable)
            })
            
    except Exception as e:
        print(f"Error in timetable AI assist: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/timetable/update', methods=['POST'])
def update_timetable_with_changes():
    try:
        data = request.json
        changes = data.get('changes', [])
        
        # Load current timetable
        current_timetable = time_tabel_help.load_timetable()
        
        # Validate and apply changes
        is_valid, result = time_tabel_help.validate_timetable_changes(changes, current_timetable)
        
        if not is_valid:
            return jsonify({'error': result}), 400
            
        # Save updated timetable
        if time_tabel_help.save_timetable(result):
            return jsonify({
                'success': True,
                'updatedTimetable': result
            })
        else:
            return jsonify({'error': 'Failed to save timetable'}), 500
    except Exception as e:
        print(f"Error updating timetable: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/students/attendance/<int:student_id>', methods=['GET'])
def get_student_attendance(student_id):
    try:
        attendance_df = pd.read_csv('school_data_csv/attendance_records.csv')
        student_attendance = attendance_df[attendance_df['student_id'] == student_id]
        
        if student_attendance.empty:
            return jsonify({
                'attendance': [True] * 20  # Default to all present if no record found
            })
            
        # Convert attendance records to boolean array
        attendance_days = [f'Day {i+1}' for i in range(20)]
        attendance_array = [
            student_attendance[day].iloc[0] == 'P' 
            for day in attendance_days 
            if day in student_attendance.columns
        ]
        
        return jsonify({
            'attendance': attendance_array
        })
        
    except Exception as e:
        print(f"Error fetching student attendance: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
