# Course Selection and Slot Booking Intelligence
# Handles course selection, slot booking, and confirmation

from booking_system import (
    COURSES, DEMO_SLOTS, get_course_info, 
    create_booking, get_booking_confirmation_message
)

class CourseBookingManager:
    """Manages course selection and demo slot booking"""
    
    def get_course_selection_message(self):
        """Ask student which course they want"""
        return (
            "మీరు ఏ course నుండి interested ఉంటారు బ్రో? "
            "We offer two main courses బ్రో: "
            "1. Python Full Stack - 8 weeks బ్రో, 12,000 INR (after discount) బ్రో "
            "2. Java Full Stack - 10 weeks బ్రో, 14,000 INR (after discount) బ్రో. "
            "Please say 'Python' లేదా 'Java' లేదా 'Python Full Stack' లేదా 'Java Full Stack' బ్రో."
        )
    
    def get_course_confirmation(self, course_name):
        """Confirm course selection and offer demo"""
        course = get_course_info(course_name)
        if not course:
            return None
        
        return (
            f"బాగుందా బ్రో! నీరు {course['name']} చేయాలనుకుంటున్నారా బ్రో. చాలా బాగుంది బ్రో! "
            f"Duration: {course['duration']} బ్రో, Topics: {', '.join(course['topics'])} బ్రో. "
            f"ఈ course about free demo class ఉంది బ్రో - "
            f"next batch {course['next_batch']} నుండి start అవుతుంది బ్రో. "
            f"Free demo class నీ convenient day లో చేయవచ్చు బ్రో. "
            f"Demo లో live coding, actual mentors, and doubts clarification ఉంటుంది బ్రో. "
            f"మీరు free demo class కి interested ఉంటారా బ్రో? Yes or no బ్రో?"
        )
    
    def get_demo_booking_message(self, course_name):
        """Offer to book demo slot"""
        course = get_course_info(course_name)
        available_days = list(DEMO_SLOTS.keys())
        days_str = ", ".join(available_days)

        if not course:
            return (
                f"కూల్ బ్రో! మీ slot book చేసుకోవడానికి ఇదిగో free demo options ఉన్నాయి బ్రో. "
                f"Available days: {days_str} బ్రో. "
                f"దయచేసి Monday, Tuesday, Wednesday, Thursday లేదా Friday లో ఒకటి చెప్పండి బ్రో."
            )
        
        return (
            f"కూల్ బ్రో! నీ demo slot book చేస్తానా బ్రో? "
            f"Available days: {days_str} బ్రో. "
            f"నీకు ఏ day convenient బ్రో? Please say Monday, Tuesday, Wednesday, Thursday, or Friday బ్రో."
        )
    
    def get_demo_time_message(self):
        """Ask for preferred demo time"""
        return (
            "Available times: 10:00 AM, 2:00 PM, 4:00 PM బ్రో. "
            "మీకు ఏ time convenient బ్రో? Please say the time బ్రో."
        )
    
    def get_booking_confirmation(self, booking):
        """Generate booking confirmation message"""
        return get_booking_confirmation_message(booking)
    
    def get_closing_message(self, booking):
        """Professional closing with booking details"""
        return (
            f"ధన్యవాదాలు బ్రో! మీ booking confirmed బ్రో! "
            f"Course: {booking['course_name']} బ్రో, "
            f"Demo Date: {booking['demo_date']} బ్రో, "
            f"Demo Time: {booking['demo_time']} బ్రో. "
            f"ఈ details మీ phone కి message లో కూడా పంపిస్తాం బ్రో. "
            f"Demo లో చూపించేవి చాలా exciting ఉంటుంది బ్రో. "
            f"See you soon బ్రో! All the best for your bright future బ్రో!"
        )
    
    def get_course_name_from_input(self, user_input):
        """Extract course name from user input"""
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ["python", "py"]):
            return "python"
        elif any(word in text_lower for word in ["java"]):
            return "java"
        
        return None
    
    def get_day_from_input(self, user_input):
        """Extract day from user input"""
        text_lower = user_input.lower()
        days = ["monday", "tuesday", "wednesday", "thursday", "friday"]
        
        for day in days:
            if day in text_lower:
                return day.capitalize()
        
        return None
    
    def get_time_from_input(self, user_input):
        """Extract time from user input"""
        text_lower = user_input.lower()
        times = ["10:00 AM", "2:00 PM", "4:00 PM"]
        
        if any(word in text_lower for word in ["10", "morning", "10am"]):
            return "10:00 AM"
        elif any(word in text_lower for word in ["2", "afternoon", "2pm"]):
            return "2:00 PM"
        elif any(word in text_lower for word in ["4", "evening", "4pm"]):
            return "4:00 PM"
        
        return None

# Create global instance
booking_manager = CourseBookingManager()

def get_course_selection():
    return booking_manager.get_course_selection_message()

def get_course_confirmation(course_name):
    return booking_manager.get_course_confirmation(course_name)

def get_demo_booking(course_name):
    return booking_manager.get_demo_booking_message(course_name)

def get_demo_time():
    return booking_manager.get_demo_time_message()

def get_booking_confirmation(booking):
    return booking_manager.get_booking_confirmation(booking)

def get_closing(booking):
    return booking_manager.get_closing_message(booking)

def extract_course(user_input):
    return booking_manager.get_course_name_from_input(user_input)

def extract_day(user_input):
    return booking_manager.get_day_from_input(user_input)

def extract_time(user_input):
    return booking_manager.get_time_from_input(user_input)
