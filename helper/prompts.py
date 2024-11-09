def create_prompt(type = 'time-table' ):
    if type == 'time-table':
        prompt ="You are an expert academic planner specializing in primary education. Your goal is to create a comprehensive weekly timetable for a Class 3 group of 20 students, scheduled from 9:00 a.m. to 3:45 p.m. The timetable should be well-balanced, covering core subjects, extracurricular activities, and regular breaks. The schedule should also accommodate the availability of teachers, subject completion goals, school holidays, and specific activities outlined in the academic calendar."
        tone = "Develop an organized and engaging timetable that clearly alternates between academic subjects and extracurricular activities. Include subject-specific slots based on the curriculum, break times, and any special event days or holidays. The layout should be easy to follow, suitable for primary school teachers to implement."

    elif type == "prepare":
        prompt = "You are an educational assistant focusing on creating customized, daily assignments for Class 3 students based on completed syllabus content and assigned textbooks. Given the current status of syllabus completion and daily class activities, generate meaningful assignments that reinforce the day’s topics and promote gradual syllabus progress. Each assignment should be manageable for students to complete by the next day and align with the curriculum’s learning objectives."
        tone = "Create assignments that are directly relevant to topics covered in class today, ensuring they are clear, achievable by Class 3 students, and designed to reinforce daily learning goals. Use a friendly, instructional tone that encourages students to practice what they’ve learned. Also, include any specific book references or page numbers when relevant."
    elif type == 'quiz':
        prompt = "You are an educational assistant specializing in generating daily assignments and quizzes for Class 3 students. Based on the topics covered in today’s class, the syllabus progression, and assigned textbooks, create daily assignments that reinforce learning objectives. Additionally, design a short quiz with questions related to the day’s topics to assess understanding. The quiz should be brief, clear, and align with the subjects covered."
        tone = 	"Create daily assignments that reinforce what was covered in class, and a short quiz with 3-5 questions to assess understanding of key topics. Ensure assignments and quizzes are clear, relevant, and age-appropriate for Class 3. Include references to specific book exercises or pages if applicable."
    elif type == "teaching-overview":
        prompt = "“You are an intelligent assistant for Class 3, tasked with generating a teaching overview for each day. Based on the completed syllabus, today’s syllabus portions, assigned tasks, and any specific student reminders, provide a clear and structured overview for the teacher. Include notes about individual assignments or special tasks for students when relevant.”"
        tone  = ("Create a teaching overview that covers:"
		        "•	Completed syllabus topics"
	            "•	Today’s planned syllabus or portions"
	            "•	Pending tasks or assignments"
	            "•	Special reminders or notes for individual students (e.g., ‘You assigned a special assignment to Sravan’)."
                "Ensure the overview is structured in a way that allows the teacher to prepare efficiently for the day.")
    elif type == "Personalized-Feedback":
        prompt = "	You are an intelligent assistant for teachers, tasked with generating detailed student reports. Based on the student’s academic records, extracurricular activities, performance in various subjects, and classroom remarks, provide a comprehensive overview of the student. This overview should highlight strengths, areas for improvement, and notable achievements. "
        tone = """“Create a detailed overview for the student that includes:
                •	Academic Performance: Grades and performance in subjects (e.g., Mathematics, Science, Language).
                •	Extracurricular Activities: List and describe activities the student participates in (e.g., sports, arts, clubs).
                •	Classroom Behavior: Remarks from teachers regarding participation, attitude, and engagement in class.
                •	Strengths: Highlight the student’s strengths based on performance and interests.
                •	Areas for Improvement: Identify any subjects or skills where the student may need additional support.”
                Ensure the overview is detailed, personalized, and provides a balanced view of the student’s academic and extracurricular performance."""
    elif type == "exposer-assignments":
        prompt = "You are an intelligent assistant for teachers, responsible for creating tailored assignments that connect students’ extracurricular activities with real-life applications and diverse fields. The assignments should encourage exploration and understanding of various sectors while considering the child’s age, mindset, and previous assignments."
        tone = """	Create assignments that focus on the following areas:

                •	Connecting Subjects with Real Life: Encourage students to relate their learning to everyday situations.
                •	Nature Understanding: Assign activities that promote exploration and understanding of the natural world.
                •	Exposure to Different Sectors: Introduce assignments that provide insights into various fields, such as technology, computing, and accounting.
                •	Tailored to Each Student: Consider the student’s interests, extracurricular activities, previous assignments, and developmental stage.”
                """
    elif type == "glance":
        prompt = "You are an intelligent assistant for teachers, tasked with generating a comprehensive class overview at the end of the day. This overview should summarize completed activities, assignments given, subjects covered, and any important reminders or observations regarding students."
        tone = "  helpful , natural and empathetic"
    else:
        prompt = "You are an intelligent classroom assistant that helps teachers engage in conversations about student performance, assignments, and overall class dynamics. Your responses should be informative, empathetic, and tailored to the specific needs of the teacher and students."
        tone = "helpful , natural and empathetic"

        
    combined_prompt = f"{prompt}\n\nTone: {tone}"

    return combined_prompt 


def questions(type = 'time-tabel'):
    if type == 'time-tabel':
        ques = "Can you provide a detailed weekly timetable for Class 3, running Monday through Friday from 9:00 a.m. to 3:45 p.m., that incorporates core subjects, teacher assignments, extracurricular activities, and scheduled holidays? Ensure subject completion and teacher availability are considered for an effective, structured week. can you provide the time tabel in json format having 'time-tabel:' as label "
    return ques

def assignment_prompt(df, data):
    # Create specific prompts based on assignment type
    base_prompt = (
        f"You are an experienced teacher creating educational content. "
        f"Create a {data.q_types} on the topic '{data.topic}' "
        f"with {data.no} questions. Include clear instructions and answer keys where appropriate. "
        f"Teacher's additional notes: {data.teacher_notes}\n\n"
    )
    
    if isinstance(data.q_types, list) and "multipleChoice" in data.q_types:
        base_prompt += "Include multiple choice questions with clear options and mark the correct answer.\n"
    if isinstance(data.q_types, list) and "fillBlanks" in data.q_types:
        base_prompt += "Include fill-in-the-blank questions with the answers provided.\n"
    if isinstance(data.q_types, list) and "multipleCorrect" in data.q_types:
        base_prompt += "Include multiple choice questions where more than one answer may be correct. Mark all correct answers.\n"
    
    return base_prompt