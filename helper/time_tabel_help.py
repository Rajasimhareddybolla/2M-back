from .Bot import get_bot
import pandas as pd
import json
import os

DEFAULT_TIMETABLE = {
    "timeSlots": [
        "9:00 AM", "9:45 AM", "10:30 AM", "11:15 AM", "11:30 AM", "12:15 PM",
        "1:00 PM", "1:45 PM", "2:30 PM", "3:15 PM"
    ],
    "weekDays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    "subjects": [
        {"name": "Mathematics", "teacher": "Mr. Smith", "room": "101"},
        {"name": "English", "teacher": "Ms. Johnson", "room": "102"},
        {"name": "Science", "teacher": "Dr. Brown", "room": "103"},
        {"name": "History", "teacher": "Mrs. Davis", "room": "104"},
        {"name": "Geography", "teacher": "Mr. Wilson", "room": "105"},
        {"name": "P.E.", "teacher": "Coach Thompson", "room": "Gym"},
        {"name": "Art", "teacher": "Ms. Lee", "room": "106"},
        {"name": "Music", "teacher": "Mr. Garcia", "room": "107"},
        {"name": "Lunch", "teacher": "", "room": "Cafeteria"},
        {"name": "Break", "teacher": "", "room": ""},
        {"name": "Free Period", "teacher": "", "room": ""}
    ],
    "subjectColors": {
        "Mathematics": "bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800",
        "English": "bg-gradient-to-r from-green-100 to-green-200 text-green-800",
        "Science": "bg-gradient-to-r from-purple-100 to-purple-200 text-purple-800",
        "History": "bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-800",
        "Geography": "bg-gradient-to-r from-pink-100 to-pink-200 text-pink-800",
        "P.E.": "bg-gradient-to-r from-red-100 to-red-200 text-red-800",
        "Art": "bg-gradient-to-r from-indigo-100 to-indigo-200 text-indigo-800",
        "Music": "bg-gradient-to-r from-teal-100 to-teal-200 text-teal-800",
        "Lunch": "bg-gradient-to-r from-orange-100 to-orange-200 text-orange-800",
        "Break": "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800",
        "Free Period": "bg-gradient-to-r from-gray-100 to-gray-200 text-gray-800"
    },
    "timetableData": {
        "Mon": ["Mathematics", "English", "Science", "Break", "History", "Geography", "Lunch", "P.E.", "Art", "Music"],
        "Tue": ["Science", "Mathematics", "English", "Break", "Geography", "History", "Lunch", "Art", "Music", "P.E."],
        "Wed": ["History", "Science", "Mathematics", "Break", "English", "Geography", "Lunch", "Music", "Art", "P.E."],
        "Thu": ["Geography", "History", "Science", "Break", "Mathematics", "English", "Lunch", "P.E.", "Music", "Art"],
        "Fri": ["English", "Geography", "History", "Break", "Science", "Mathematics", "Lunch", "Art", "P.E.", "Music"],
        "Sat": ["Mathematics", "English", "Science", "Break", "Free Period", "Free Period", "Free Period", "Free Period", "Free Period", "Free Period"]
    }
}

def create_timetable_bot(query, timetable_data, files=None):
    """Create a specialized prompt for timetable analysis"""
    try:
        if not isinstance(timetable_data, dict):
            raise ValueError("Invalid timetable data format")
            
        system_prompt = f"""You are a specialized AI assistant for school timetable management.
        Current Timetable Structure:
        - Days: {', '.join(timetable_data.keys())}
        - Periods per day: {len(next(iter(timetable_data.values())))}
        
        Please analyze the following aspects:
        1. Subject distribution
        2. Daily workload balance
        3. Break placement
        4. Teacher allocation
        5. Student engagement patterns
        
        User Query: {query}
        
        Current Timetable Data:
        {json.dumps(timetable_data, indent=2)}
        
        Provide specific, actionable insights and recommendations.
        """
        return get_bot(files=files, system_prompt=system_prompt)
        
    except Exception as e:
        print(f"Error creating timetable bot: {str(e)}")
        raise

def load_timetable():
    try:
        filepath = 'school_data_csv/timeTabel.jsonl'
        if not os.path.exists(filepath):
            save_timetable(DEFAULT_TIMETABLE)
            return DEFAULT_TIMETABLE
            
        with open(filepath, 'r') as f:
            data = json.load(f)
            # Validate data structure
            if not all(key in data for key in ['timeSlots', 'weekDays', 'subjects', 'subjectColors', 'timetableData']):
                return DEFAULT_TIMETABLE
            return data
    except Exception as e:
        print(f"Error loading timetable: {str(e)}")
        return DEFAULT_TIMETABLE

def save_timetable(data):
    try:
        with open('school_data_csv/timeTabel.jsonl', 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving timetable: {str(e)}")
        return False

def analyze_timetable(timetable_data):
    """Enhanced timetable analysis"""
    analysis = {
        "workload_distribution": {},
        "daily_patterns": {},
        "potential_issues": [],
        "suggestions": [],
        "metrics": {}
    }
    
    try:
        # Analyze subject distribution
        subject_count = {}
        consecutive_subjects = []
        heavy_subjects = ["Mathematics", "Science", "English"]
        
        for day, periods in timetable_data.items():
            daily_heavy = 0
            analysis["daily_patterns"][day] = {"morning": [], "afternoon": []}
            
            for i, subject in enumerate(periods):
                if not subject: continue
                
                # Count subjects
                subject_count[subject] = subject_count.get(subject, 0) + 1
                
                # Check consecutive subjects
                if i > 0 and subject == periods[i-1]:
                    consecutive_subjects.append(f"{subject} on {day}")
                
                # Track heavy subjects
                if subject in heavy_subjects:
                    daily_heavy += 1
                    period_type = "morning" if i < len(periods)/2 else "afternoon"
                    analysis["daily_patterns"][day][period_type].append(subject)
            
            if daily_heavy > 4:
                analysis["potential_issues"].append(f"High concentration of major subjects on {day}")
        
        # Generate metrics
        analysis["metrics"] = {
            "subject_balance": calculate_distribution_score(subject_count),
            "daily_load": calculate_daily_load_score(timetable_data),
            "break_distribution": calculate_break_score(timetable_data)
        }
        
        # Generate suggestions
        if consecutive_subjects:
            analysis["suggestions"].append("Consider spreading out consecutive subjects")
        
        for day, patterns in analysis["daily_patterns"].items():
            if len(patterns["morning"]) > 3:
                analysis["suggestions"].append(f"Consider redistributing heavy subjects on {day} morning")
        
        return analysis
        
    except Exception as e:
        print(f"Error in timetable analysis: {str(e)}")
        return None

def calculate_distribution_score(subject_count):
    """Calculate how well subjects are distributed"""
    if not subject_count: return 0
    values = list(subject_count.values())
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return round(100 / (1 + variance), 2)

def calculate_daily_load_score(timetable_data):
    """Calculate how well the daily workload is balanced"""
    heavy_subjects = {"Mathematics", "Science", "English"}
    daily_loads = []
    
    for day, periods in timetable_data.items():
        heavy_count = sum(1 for subject in periods if subject in heavy_subjects)
        daily_loads.append(heavy_count)
    
    mean = sum(daily_loads) / len(daily_loads)
    variance = sum((x - mean) ** 2 for x in daily_loads) / len(daily_loads)
    return round(100 / (1 + variance), 2)

def calculate_break_score(timetable_data):
    """Calculate how well breaks are distributed"""
    break_score = 100
    for day, periods in timetable_data.items():
        last_break = -1
        for i, subject in enumerate(periods):
            if subject in ["Break", "Lunch"]:
                if last_break != -1 and (i - last_break < 2 or i - last_break > 4):
                    break_score -= 10
                last_break = i
    return max(0, break_score)

def validate_timetable_changes(changes, current_timetable):
    """Validate proposed timetable changes"""
    try:
        # Deep copy current timetable
        proposed_timetable = json.loads(json.dumps(current_timetable))
        
        for change in changes:
            day = change.get('day')
            period = change.get('period')
            new_subject = change.get('subject')
            
            if not all([day, period is not None, new_subject]):
                return False, "Invalid change format"
            
            # Apply change to proposed timetable
            if day not in proposed_timetable:
                return False, f"Invalid day: {day}"
                
            if period >= len(proposed_timetable[day]):
                return False, f"Invalid period: {period}"
                
            proposed_timetable[day][period] = new_subject
        
        # Validate the proposed timetable
        analysis = analyze_timetable(proposed_timetable)
        if not analysis:
            return False, "Failed to analyze proposed changes"
            
        # Check if the changes create any serious issues
        if len(analysis['potential_issues']) > 3:
            return False, "Too many potential issues in proposed changes"
            
        return True, proposed_timetable
        
    except Exception as e:
        print(f"Error validating changes: {str(e)}")
        return False, str(e)

def suggest_timetable_changes(query, current_timetable):
    """Generate AI suggestions for timetable changes"""
    try:
        analysis = analyze_timetable(current_timetable)
        if not analysis:
            return [], "Failed to analyze current timetable"
            
        suggested_changes = []
        
        # Parse user query for specific requirements
        requirements = {
            'balance': 'balance' in query.lower(),
            'workload': 'workload' in query.lower(),
            'breaks': 'break' in query.lower(),
            'specific_day': next((day for day in current_timetable.keys() 
                                if day.lower() in query.lower()), None)
        }
        
        # Generate changes based on analysis and requirements
        if requirements['balance'] or requirements['workload']:
            for day, patterns in analysis['daily_patterns'].items():
                if len(patterns['morning']) > 3:
                    suggested_changes.append({
                        'day': day,
                        'period': 2,  # Example period
                        'subject': 'Art',  # Lighter subject
                        'description': f"Move a lighter subject to morning on {day}"
                    })
                    
        if requirements['breaks']:
            for day, periods in current_timetable.items():
                last_break = -1
                for i, subject in enumerate(periods):
                    if subject in ["Break", "Lunch"]:
                        if last_break != -1 and (i - last_break > 4):
                            suggested_changes.append({
                                'day': day,
                                'period': i - 2,
                                'subject': "Break",
                                'description': f"Add break period on {day}"
                            })
                        last_break = i
                        
        return suggested_changes, "Generated suggestions based on analysis"
        
    except Exception as e:
        print(f"Error suggesting changes: {str(e)}")
        return [], str(e)
