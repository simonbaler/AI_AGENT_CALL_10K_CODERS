# Booking Management System
# Stores and manages student demo slot bookings

import json
import os
from datetime import datetime

BOOKINGS_FILE = "student_bookings.json"

def load_bookings():
    """Load existing bookings from file"""
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_booking(booking):
    """Save a new booking to file"""
    bookings = load_bookings()
    bookings.append(booking)
    
    with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bookings, f, ensure_ascii=False, indent=2)
    
    return True

def create_booking(phone_number, course_name, demo_date, demo_time="10:00 AM", student_name="", college="", language="en-IN"):
    """
    Create a new booking record
    
    Example:
    {
        "student_name": "John Doe",
        "student_phone": "+919876543210",
        "course_name": "Python Full Stack",
        "demo_date": "Monday",
        "demo_time": "10:00 AM",
        "booking_date": "2026-05-11",
        "booking_status": "confirmed"
    }
    """
    booking = {
        "student_name": student_name,
        "college": college,
        "language": language,
        "student_phone": phone_number,
        "course_name": course_name,
        "demo_date": demo_date,
        "demo_time": demo_time,
        "booking_date": datetime.now().strftime("%Y-%m-%d"),
        "booking_time": datetime.now().strftime("%H:%M:%S"),
        "booking_status": "confirmed"
    }
    
    save_booking(booking)
    return booking

def get_bookings_for_date(date):
    """Get all bookings for a specific date"""
    bookings = load_bookings()
    return [b for b in bookings if b["demo_date"] == date]

def get_student_booking(phone_number):
    """Get booking details for a specific student"""
    bookings = load_bookings()
    return next((b for b in bookings if b["student_phone"] == phone_number), None)

def get_booking_confirmation_message(booking):
    """Generate booking confirmation message"""
    return (
        f"మీ demo slot successfully book అయ్యింది! "
        f"Course: {booking['course_name']}, "
        f"Demo Date: {booking['demo_date']}, "
        f"Demo Time: {booking['demo_time']}. "
        f"ఈ details మీ రెండవ confirmation message లో చూస్తారు. "
        f"All the best!"
    )

# Available courses
COURSES = {
    "python": {
        "name": "Python Full Stack",
        "duration": "8 weeks",
        "fee": "12,000 INR (20% discount)",
        "next_batch": "Monday",
        "topics": ["Python", "Django", "React", "Databases", "APIs"]
    },
    "java": {
        "name": "Java Full Stack",
        "duration": "10 weeks",
        "fee": "14,000 INR (20% discount)",
        "next_batch": "Monday",
        "topics": ["Java", "Spring Boot", "React", "Databases", "Microservices"]
    }
}

# Available demo slots
DEMO_SLOTS = {
    "Monday": ["10:00 AM", "2:00 PM", "4:00 PM"],
    "Tuesday": ["10:00 AM", "2:00 PM", "4:00 PM"],
    "Wednesday": ["10:00 AM", "2:00 PM", "4:00 PM"],
    "Thursday": ["10:00 AM", "2:00 PM", "4:00 PM"],
    "Friday": ["10:00 AM", "2:00 PM", "4:00 PM"]
}

def get_course_info(course_key):
    """Get course information"""
    return COURSES.get(course_key.lower())

def get_available_slots(day):
    """Get available demo slots for a day"""
    return DEMO_SLOTS.get(day, [])
