# Question Detection and Answer Generation System

from knowledge_base import COURSE_INFO, FAQS

def detect_question_type(user_text):
    """
    Detect what type of question the student is asking
    Returns the answer from knowledge base
    """
    text_lower = user_text.lower()
    
    # Check for self-introduction or assistant capabilities
    if any(word in text_lower for word in ["who are you", "who r you", "what is your name", "introduce yourself", "tell me about yourself", "who is speaking", "who is this"]):
        return "who_are_you", None
    if any(word in text_lower for word in ["what can you do", "what do you do", "your purpose", "how can you help", "help me", "what are you"]):
        return "what_can_you_do", None
    if "gemini" in text_lower:
        if any(word in text_lower for word in ["how", "work", "works", "what is", "explain", "how does", "does it"]):
            return "how_gemini_works", None
        return "google_gemini", None
    if any(word in text_lower for word in ["what is ai", "ai how", "how does ai work", "artificial intelligence", "large language model", "llm", "chatgpt", "chat gpt"]):
        return "what_is_ai", None
    if any(word in text_lower for word in ["transformer", "attention mechanism", "attention model", "large language model", "llm", "language model"]):
        return "what_is_llm", None
    if any(word in text_lower for word in ["training data", "trained on", "training process", "train the model", "fine tune", "fine-tune", "fine tuning"]):
        return "what_is_training_data", None
    if any(word in text_lower for word in ["are you a sales", "sales agent", "salesperson", "sales person", "sales person or ai", "sales and ai", "are you both", "agent or ai"]):
        return "are_you_sales_agent", None
    if any(word in text_lower for word in ["how do you work", "how do you answer", "how are you responding", "how do you know", "how do you do this", "how does this work", "what is your process"]):
        return "how_ai_assistant_works", None
    if any(word in text_lower for word in ["course details", "course detail", "full stack course", "python full stack", "java full stack", "full stack python", "python full stock", "python full star", "full stack programme", "course explain", "tell me about course", "course content"]):
        return "course_details", None
    if any(word in text_lower for word in ["book slot", "demo slot", "demo booking", "free demo", "demo class", "free class", "book demo", "slot on python", "slot on java"]):
        return "demo_class", "YES! We have completely FREE demo class - 1 hour hands-on coding session. No commitment needed. You'll learn basics, see real projects, ask all your doubts. Want me to book your demo slot?"
    if any(word in text_lower for word in ["certificate", "certification", "certified", "certificate after", "course complete certificate"]):
        return "certificate_value", FAQS["certificate_value"]["answer"]

    # Check for doubt/confusion words first
    doubt_words = ["doubt", "confused", "clear", "understand", "not clear", "confusing", "doubtful", "unclear", "not sure", "don't know"]
    if any(word in text_lower for word in doubt_words):
        return "general_doubt", "నీకు ఏమైనా doubt ఉందా? నేను clear చేస్తాను. నీకు ఏ topic గురించి doubt ఉంది? Course content, fees, placement, projects, లేదా schedule గురించి?"
    
    # Check for each FAQ
    if any(word in text_lower for word in ["what", "full stack", "full-stack", "what is"]):
        if any(word in text_lower for word in ["full stack", "full-stack", "web development"]):
            return "what_is_full_stack", FAQS["what_is_full_stack"]["answer"]
    
    if any(word in text_lower for word in ["why python", "why use python", "why learn python"]):
        return "why_python", FAQS["why_python"]["answer"]
    
    if any(word in text_lower for word in ["placement", "job", "placement rate", "salary"]):
        if any(word in text_lower for word in ["guarantee", "guaranteed", "sure", "100%"]):
            return "placement_guarantee", FAQS["placement_guarantee"]["answer"]
        if any(word in text_lower for word in ["salary", "pay", "earning", "money", "how much salary"]):
            return "salary_expectations", FAQS["salary_expectations"]["answer"]
        else:
            return "placement", "Our placement rate is 85%. Most students get placed in 1-3 months. Average salary: 3.5-5.5 LPA. Top companies: TCS, Infosys, Accenture, Wipro, Amazon, startups."
    
    if any(word in text_lower for word in ["when", "start date", "batch", "timing", "schedule", "start"]):
        if any(word in text_lower for word in ["flexible", "flexible schedule", "working", "job"]):
            return "schedule_flexible", FAQS["schedule_flexible"]["answer"]
        else:
            return "course_timing", FAQS["course_timing"]["answer"]
    
    if any(word in text_lower for word in ["fees", "fee", "cost", "price", "how much", "discount", "affordable", "money"]):
        return "fees_and_discounts", FAQS["fees_and_discounts"]["answer"]
    
    if any(word in text_lower for word in ["python", "prerequisite", "prior", "experience", "knowledge", "beginner", "basic", "zero"]):
        return "prerequisite_skills", FAQS["prerequisite_skills"]["answer"]
    
    if any(word in text_lower for word in ["batch size", "students per batch", "how many students", "class size", "batch"]):
        return "batch_size", FAQS["batch_size"]["answer"]
    
    if any(word in text_lower for word in ["after", "after course", "after completion", "job assistance", "support", "help"]):
        return "after_course", FAQS["after_course"]["answer"]
    
    if any(word in text_lower for word in ["project", "practical", "real project", "what will i build", "build", "create"]):
        return "projects_real", FAQS["projects_real"]["answer"]
    
    if any(word in text_lower for word in ["internship", "intern", "paid internship", "internship opportunity"]):
        return "internship", FAQS["internship"]["answer"]
    
    if any(word in text_lower for word in ["refund", "money back", "guarantee", "not satisfied", "not happy", "back"]):
        return "refund_policy", FAQS["refund_policy"]["answer"]
    
    if any(word in text_lower for word in ["certificate", "certified", "recognized", "value", "worth"]):
        return "certificate_value", FAQS["certificate_value"]["answer"]
    
    if any(word in text_lower for word in ["weeks", "how long", "duration", "learning pace", "time", "8 weeks"]):
        return "learning_pace", FAQS["learning_pace"]["answer"]
    
    if any(word in text_lower for word in ["demo", "free", "free class", "demo class", "trial"]):
        return "demo_class", "YES! We have completely FREE demo class - 1 hour hands-on coding session. No commitment needed. You'll learn basics, see real projects, ask all your doubts. Want me to book your demo slot?"
    
    # Check for common doubts and concerns
    if any(word in text_lower for word in ["difficult", "hard", "tough", "challenging", "easy"]):
        return "difficulty_level", "Don't worry! We teach from ZERO level. No prior experience needed. Our mentors have 5-10 years experience and explain everything step-by-step. 85% students are beginners when they join!"
    
    if any(word in text_lower for word in ["time", "busy", "work", "job", "college", "studies"]):
        return "time_commitment", "We understand you're busy! That's why we have flexible schedules: Evening batches (6-8 PM), Weekend batches (10 AM-1 PM), and recorded classes. You can learn at your own pace!"
    
    if any(word in text_lower for word in ["worth", "value", "benefit", "advantage", "good"]):
        return "course_worth", "This course is WORTH IT! You'll learn skills used by Google, Netflix, Amazon. Get placed in top companies. Build real projects for your portfolio. Lifetime support from mentors. Much better than college!"
    
    if any(word in text_lower for word in ["mentor", "teacher", "instructor", "support", "help"]):
        return "mentor_support", "Our mentors have 5-10 years industry experience! They provide: 1-on-1 doubt solving, Code review, Career guidance, Interview preparation, Lifetime support even after course completion."
    
    # If no specific question detected, ask for clarification
    return "unclear", None

def generate_answer(question_type, user_text):
    """
    Generate a salesperson-like response
    """
    responses = {
        "what_is_full_stack": f"నీ question బాగుందా బ్రో! {FAQS['what_is_full_stack']['answer']}",
        
        "why_python": f"Perfect question బ్రో! {FAQS['why_python']['answer']}",
        
        "placement_guarantee": f"అలా చెప్పాలంటే బ్రో - {FAQS['placement_guarantee']['answer']}",
        
        "course_timing": f"అది చాలా బాగుందా బ్రో! {FAQS['course_timing']['answer']}",
        
        "fees_and_discounts": f"నీకు specially student discount ఉంది బ్రో! {FAQS['fees_and_discounts']['answer']}",
        
        "prerequisite_skills": f"అది సరిదైనప్ర బ్రో! {FAQS['prerequisite_skills']['answer']}",
        
        "batch_size": f"చాలా ముఖ్యమైన question బ్రో! {FAQS['batch_size']['answer']}",
        
        "after_course": f"మంచి thought బ్రో! {FAQS['after_course']['answer']}",
        
        "projects_real": f"అది నిజమైన advantage బ్రో! {FAQS['projects_real']['answer']}",
        
        "internship": f"బాగుందా బ్రో! {FAQS['internship']['answer']}",
        
        "refund_policy": f"నీ confidence తో రమ్మంటా బ్రో! {FAQS['refund_policy']['answer']}",
        
        "certificate_value": f"బాగుందా బ్రో! {FAQS['certificate_value']['answer']}",
        
        "salary_expectations": f"ఇది నిజంగా important బ్రో! {FAQS['salary_expectations']['answer']}",
        
        "learning_pace": f"చాలా common doubt బ్రో! {FAQS['learning_pace']['answer']}",
        
        "demo_class": f"అంతా కుదిరిపోయిందా బ్రో? Demo class చేయనా బ్రో? 1 hour FREE, hands-on coding, no commitment బ్రో!",
        
        "general_doubt": f"నీకు ఏమైనా doubt ఉందా బ్రో? నేను clear చేస్తాను బ్రో. నీకు ఏ topic గురించి doubt ఉంది బ్రో? Course content, fees, placement, projects, లేదా schedule గురించి బ్రో?",
        
        "difficulty_level": f"Don't worry about difficulty బ్రో! నేను నా 10 years experience నుండి చెప్తాను బ్రో - we teach from ZERO level బ్రో. No prior experience needed బ్రో. Our step-by-step approach makes it easy for everyone బ్రో. 85% of our students start as complete beginners బ్రో!",
        
        "who_are_you": "నేను advanced AI sales assistant ని, మీకు course details, placement questions, demo booking, మరియు technology questions answers explain చేయగలనని. నేను sales counselor style తో మీరు comfortable గా మాట్లాడేలా చెప్తాను.",
        
        "what_can_you_do": "నేను మీకు Full Stack courses explain చేయగలను, fees, placements, project details, internship support, మరియు free demo booking కూడా manage చేయగలను. అంతేకాదు, నేను Google Gemini, AI models, programming concepts, మరియు career questions కూడా explain చేయగలను.",
        
        "are_you_sales_agent": "నేను రెండు పనులు చేస్తాను బ్రో. ఒక వైపు sales person style లో course benefits, demo booking, fees, placements discuss చేస్తాను. మరో వైపు AI assistant style లో Gemini, ChatGPT, LLMs, training data, model explanation వంటి technology questions answer చేస్తాను.",
        
        "how_ai_assistant_works": "నేను question detect చేసి, internal knowledge base నుండి best answer prepare చేస్తాను. ఈ process లో NLP patterns, keywords, మరియు predefined AI responses use చేస్తాను. మీరు sales questions అడిగితే sales pitch మరియు booking help ఇస్తాను; tech questions అడిగితే AI concept explanation కూడా ఇవ్వగలను.",
        
        "google_gemini": "Google Gemini అనేది Google యొక్క powerful multi-modal AI model. ఇది text, images, audio వంటి data తో train అయ్యి smart answers, summaries, coding help, మరియు creative content generate చేస్తుంది.",
        
        "how_gemini_works": "Google Gemini internally billions of examples తో train అవుతుంది. ఇది contextual understanding ని use చేస్తూ next word prediction చేస్తుంది, multi-modal inputs support చేస్తుంది, మరియు conversational intelligence కోసం optimize చేయబడింది.",
        
        "what_is_ai": "AI అంటే artificial intelligence. ఇది machines ని data నుండి learn చేయడానికి, human-like decisions తీసుకోవడానికి, మరియు మీరు అడగే questions కి useful answers generate చేయడానికి train చేయబడింది.",
        
        "what_is_llm": "LLM అంటే Large Language Model. ఇది text data లో patterns study చేసి, sentences generate చేయగలదు. Google Gemini, ChatGPT లాంటి models LLMs. మనం talk చేస్తున్నదే ఒక simplified version of that idea.",
        
        "what_is_training_data": "AI models training data తో learn చేస్తాయి. అంటే text, code, images, audio వంటి data example లను use చేసి model future questions కి answer ఇవ్వడం నేర్చుకుంటుంది. అది model performance కి base అవుతుంది.",
        
        "course_details": "Python Full Stack course లో నీకు teach చేసే topics: Python basics, OOP, Django/Flask, REST APIs, React frontend, SQL databases, deployment, real projects, interview prep. Free demo లో actual live coding, Q&A, mentor guidance ఉంటాయి. Interested in demo booking?",
        
        "time_commitment": f"నీ busy schedule నేను అర్థం చేసుకున్నాను బ్రో! అందుకే flexible options ఉన్నాయి బ్రో: Evening batches (6-8 PM బ్రో), Weekend batches (10 AM-1 PM బ్రో), Recorded classes for later viewing బ్రో, Flexible project deadlines బ్రో. నీకు ఏది convenient బ్రో?",
        
        "course_worth": f"అది బాగుందా బ్రో! ఈ course 100% WORTH IT బ్రో! నీరు నేర్చుకునే skills Google, Netflix, Amazon వాడతారు బ్రో. Top companies లో job అవుతారు బ్రో. Real projects portfolio కి add అవుతాయి బ్రో. Mentors lifetime support ఉంది బ్రో. College కంటే చాలా better బ్రో!",
        
        "mentor_support": f"అది ముఖ్యమైన point బ్రో! నీకు 5-10 years industry experience ఉన్న mentors ఉంటారు బ్రో. వారు ఇస్తారు బ్రో: 1-on-1 doubt solving బ్రో, Code review బ్రో, Career guidance బ్రో, Interview preparation బ్రో, Course completion తర్వాత కూడా lifetime support బ్రో!",
        
        "schedule_flexible": f"అది చాలా బాగుందా బ్రో! {FAQS['schedule_flexible']['answer']}",
        
        "unclear": f"ఈ question నాకు ఇంకా clear కాలేదు బ్రో. మీరు course structure, fees, placement support, projects, internship, లేదా schedule గురించి అడగండి బ్రో. నేను స్పష్టంగా explain చేస్తాను బ్రో.",
        
        "placement": f"మంచి question బ్రో! {COURSE_INFO['placements']['placement_rate']} students placement అవుతారు బ్రో. Average salary: {COURSE_INFO['placements']['average_salary']} బ్రో. Top companies: TCS, Infosys, Accenture, startups బ్రో.",
    }
    
    return responses.get(question_type, responses["unclear"])

def should_push_demo(conversation_turn, interest_level):
    """
    Decide if it's time to push for demo booking
    """
    if interest_level >= 2 and conversation_turn >= 3:
        return True
    if conversation_turn >= 5:
        return True
    return False

def get_demo_booking_response():
    """
    Response when pushing for demo booking
    """
    responses = [
        "నీకు free demo class book చేస్తానా? అందులో live coding చేస్తాం. 1 hour, completely free, no commitment.",
        "ఇక్కడ చెప్పిన అన్నీ demo లో see చేయవచ్చు. నీ convenient time లో. సరిపోతుందా?",
        "నీ doubt clear చేయడానికి free demo best! Actual mentors తో code చేస్తాం. నీ time ఎంటా?",
        "అన్నీ clear అయ్యే పటికి demo attend చేయనా? 0 investment, 100% practical learning!"
    ]
    return responses[0]  # Can rotate these for variety

def get_sales_pitch_response(turn_number):
    """
    Smart intro pitch based on turn number
    """
    if turn_number == 0:
        return """
హలో! నేను అజయ్. నాకు Ten Thousand Coders నుండి calling. 

మీరు engineering student? ఇంటర్ లేదా B.Tech చేస్తున్నారా? 

నిజమైన talk చేస్తాను - చాలా students coding లో struggle చేస్తారు. కానీ సరైన గైడెన్స్ తో చాలా better పడుతుంది.

আমরা Eight Week Full Stack Python Program conduct చేస్తున్నాం. Real Python, Real Projects, Real Placements. 

నీకు interest ఉందా? నేను details చెప్తాను.
"""
    else:
        return "ఇక్కడ చెప్పిన విషయాల గురించి మీకు ఏమైనా specific question ఉందా?"

