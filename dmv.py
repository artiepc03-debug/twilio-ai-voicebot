DMV_QUESTIONS = [
    "Have you ever had an ID in the state of North Carolina?",
    "Do you have your Social Security Card?",
    "Do you have your birth certificate?",
    "What is your full name?",
    "What is the best phone number?",
    "What is your email address?"
]

def get_dmv_question(step):
    if step < len(DMV_QUESTIONS):
        return DMV_QUESTIONS[step]
    return None
