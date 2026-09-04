# Advanced Sales Intelligence for 10+ Years Experience Sales Person
# This module handles conversations like a seasoned institute sales person

from knowledge_base import COURSE_INFO, FAQS

class SalesIntelligence:
    """
    10+ years experienced institute sales person intelligence
    """
    
    def __init__(self):
        self.experience_level = "10+ years"
        self.style = "friendly_mentor"
    
    def get_introduction(self):
        """
        Warm introduction like experienced sales person
        """
        return (
            "హలో బ్రో! నేను అజయ్. Ten Thousand Coders నుండి calling. "
            "నాకు soft skills and technical training లో 10 years experience ఉంది బ్రో. "
            "ఇక్కడ మేము engineering students ని software engineers గా మార్చేస్తాము. "
            "ఇంటర్ నుండి ఉద్యోగం వరకు - మేము ఉన్నాము బ్రో. "
            "Technical course లో interest ఉంటే, నేను useful information ఇస్తాను బ్రో. "
            "Software engineer కాదా లేదా technical skills learn చేయాలనుకుంటున్నావా బ్రో?"
        )
    
    def get_interest_question(self):
        """
        Simple interest check in Telugu slang
        """
        return "Engineering student ఆవా లేదా technical skills learn చేయాలనుకుంటున్నావా బ్రో? Yes లేదా no చెప్పు బ్రో."
    
    def get_encouragement_response(self):
        """
        Response when student shows interest in Telugu slang
        """
        return (
            "బాగుంది బ్రో! నీ interest చూసి నాకు చాలా సంతోషం. "
            "నేను నీకు ఏమైనా చెప్తాను బ్రో. "
            "ఈ course లో నీరు actual industry practices, real projects, job-ready skills నేర్చుకుంటావు బ్రో. "
            "మన 85% students ని నేను personally చూసాను - top companies లో placed అవ్వటం. "
            "ఇప్పుడు నీకు specifically ఏమైనా తెలుసుకోవాలనుకుంటున్నావా బ్రో?"
        )
    
    def get_rejection_response(self):
        """
        Respectful exit when student says no in Telugu slang
        """
        return (
            "సరే బ్రో, ఏ problem లేదు. తర్వాత నీకు interest వచ్చే తర్వాత call చేస్తూ ఉంటాను బ్రో. "
            "All the best నీ studies కి బ్రో. నీ bright future కి ఎలాంటి సమస్య ఉండదు. Thank you బ్రో!"
        )
    
    def get_mid_flow_answer_intro(self, question_type):
        """
        Introduction before answering mid-flow questions in Telugu slang
        """
        responses = {
            "fees_and_discounts": "నీకు సరైన question బ్రో! ఈ investment గురించి honest explain చేస్తాను బ్రో. ",
            "placement_guarantee": "చాలా important question బ్రో! నేను నా 10 years experience నుండి చెప్తాను బ్రో. ",
            "course_timing": "Schedule ఖచ్చితంగా flexible బ్రో! నీ convenience చూసి చెప్తా బ్రో. ",
            "projects_real": "ఇది చాలా practical question బ్రో! నేను students నిర్మిన real projects చూపిస్తాను బ్రో. ",
            "prerequisite_skills": "నీకు confusion ఉందా బ్రో? అందుకే నేను ఉన్నాను బ్రో. Clear చేస్తాను బ్రో. ",
            "what_is_full_stack": "బాగుందా బ్రో! నీకు simple example ఇస్తా బ్రో - నీరు understand చేసుకుంటారు బ్రో. ",
            "salary_expectations": "Salary గురించి నేను honest explain చేస్తాను బ్రో - realistic figures బ్రో. ",
            "placement": "Placements గురించి నేను నా students నుండి నేరుగా stories చెప్తాను బ్రో. "
        }
        return responses.get(question_type, "ఈ question గురించి నీకు clear చేస్తాను బ్రో: ")
    
    def get_after_answer_continuation(self):
        """
        Smart follow-up after answering questions
        """
        continuations = [
            "ఇక్కడ చెప్పిన విషయాలు clear అయ్యాయా బ్రో? నీకు ఇంకా doubt ఉందా బ్రో?",
            "ఈ answer సరిపోతుందా బ్రో? నీకు మరో angle నుండి విచారించాలనుకుంటున్నావా బ్రో?",
            "ఇది account చేసుకో బ్రో - నీకు ఇదే answer చాలా సాధారణమైనది. More detail కావాలా బ్రో?",
            "నీ concern clear అయ్యాలని నేను నిశ్చితం బ్రో. ఇంకా question ఉందా బ్రో?",
            "ఇక్కడ చెప్పిన విషయం నీకు convincing అయ్యాయా బ్రో? మీకు నా numbers trust చేయవచ్చు బ్రో.",
            "నీకు ఇంకా ఏమైనా doubt ఉందా బ్రో? నేను clear చేస్తాను బ్రో - ఏమైనా అడుగు బ్రో.",
            "ఈ explanation సరిపోతుందా బ్రో? నీకు practical example కావాలా బ్రో?",
            "మీరు ఇంకా ఏమైనా తెలుసుకోవాలనుకుంటున్నారా బ్రో? నేను ఉన్నాను బ్రో."
        ]
        return continuations[0]  # Can rotate these
    
    def get_demo_push_message(self, turn_number):
        """
        Smart demo push after multiple conversations
        """
        if turn_number >= 4:
            return (
                "తర్వాత నేను నీకు suggest చేస్తాను బ్రో - free demo class కి వెళ్లు బ్రో. "
                "అక్కడ నీరు live coding చూస్తాయ బ్రో, actual mentors తో కలిసేటాయ బ్రో, మరియు నీ doubts clear చేస్తాయ బ్రో. "
                "1 hour, completely free, no pressure బ్రో. మీకు ఆసక్తి ఉందా బ్రో?"
            )
        return None
    
    def get_closing_message(self):
        """
        Professional closing if call ends in Telugu slang
        """
        return (
            "ఇది చాలా nice conversation బ్రో. నీతో మాట్లాడటం చాలా బాగా ఉంది బ్రో. "
            "ఇక్కడ చెప్పిన విషయాలు consider చేసుకో బ్రో. "
            "తర్వాత నీకు questions ఉంటే, నా contact number వాడు బ్రో. "
            "నీ brilliant future కి all the best బ్రో! Thank you బ్రో!"
        )
    
    def get_objection_handler(self, objection_type):
        """
        Handle common objections like experienced sales person
        """
        handlers = {
            "expensive": (
                "నీకు fee చాలా ఎక్కువ అనిపిస్తుందా బ్రో? నేను చెప్తాను బ్రో - "
                "ఇది investment బ్రో, expense కాదు బ్రో. నీరు 6 months లో ఈ fee కు doubly earn చేస్తాయ బ్రో. "
                "ఇలాంటి training లేకుండా, నీరు 2-3 years waste చేస్తాయ బ్రో. Investment చెసుకో బ్రో!"
            ),
            "time": (
                "Time manage చేయాలనుకుంటున్నావా బ్రో? పీర్ బోధ బ్రో! "
                "మన course పూర్తిగా మీ schedule నుండి flexible బ్రో. "
                "పూర్తి-time job చేస్తూ కూడా, evening batches లో చేయవచ్చు బ్రో."
            ),
            "doubt": (
                "Doubt ఉందా బ్రో? అందుకే నేను ఉన్నాను బ్రో! "
                "చెల్లు బ్రో, నీరు try చేసుకో బ్రో. 30-day money back guarantee ఉంది బ్రో. "
                "ఉండకపోతే, complete refund బ్రో. Risk లేదు బ్రో!"
            ),
            "job_guarantee": (
                "నీరు placement guarantee అన్నారా బ్రో? నేను guarantee ఇవ్వను బ్రో - "
                "కానీ నీరు काम చేస్తే, 90% సంభావ్యత ఉంది బ్రో। "
                "మన 85% students ని personally నేను place చేసాను బ్రో. "
                "నీరు serious ఉండాలి బ్రో."
            )
        }
        return handlers.get(objection_type, "ఈ doubt గురించి మీరు చింతపడకండి. నీరు sure చేసుకోవచ్చు.")

# Create global instance
sales_person = SalesIntelligence()

def get_intro_message():
    return sales_person.get_introduction()

def get_interest_check():
    return sales_person.get_interest_question()

def get_yes_response():
    return sales_person.get_encouragement_response()

def get_no_response():
    return sales_person.get_rejection_response()

def get_answer_intro(q_type):
    return sales_person.get_mid_flow_answer_intro(q_type)

def get_after_answer():
    return sales_person.get_after_answer_continuation()

def get_demo_message(turn):
    return sales_person.get_demo_push_message(turn)

def get_close():
    return sales_person.get_closing_message()

def handle_objection(obj_type):
    return sales_person.get_objection_handler(obj_type)
