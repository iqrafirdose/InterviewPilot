import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELS = [
    "llama-3.3-70b-versatile",
    "llama3-70b-8192",
    "gemma2-9b-it",
    "mixtral-8x7b-32768"
]

def call_groq(prompt):
    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            if "over capacity" in str(e) or "503" in str(e) or "decommissioned" in str(e):
                time.sleep(1)
                continue
            raise e
    return "All models are busy. Please try again in a moment."

ROLE_CONTEXT = {
    "Software Engineer": "Focus on DSA, system design, coding concepts, OOP, databases, APIs.",
    "QA / Testing Engineer": "Focus on test cases, bug reporting, automation tools, SDLC, Selenium, manual vs automation testing.",
    "Product Manager": "Focus on product strategy, roadmaps, user stories, prioritization frameworks, stakeholder management, metrics.",
    "Marketing Manager": "Focus on campaigns, SEO, social media strategy, brand positioning, analytics, growth hacking.",
    "Data Analyst": "Focus on SQL, Excel, data visualization, statistics, dashboards, business insights.",
    "UI/UX Designer": "Focus on design thinking, user research, wireframing, prototyping, usability testing, tools like Figma.",
    "Business Analyst": "Focus on requirements gathering, process mapping, stakeholder communication, documentation, data analysis.",
    "DevOps Engineer": "Focus on CI/CD, Docker, Kubernetes, cloud platforms, monitoring, infrastructure as code.",
    "Data Scientist": "Focus on machine learning, Python, statistics, model evaluation, feature engineering, deep learning.",
    "HR Manager": "Focus on recruitment, employee relations, performance management, policies, culture building.",
    "Finance Analyst": "Focus on financial modeling, Excel, forecasting, budgeting, P&L, valuations.",
    "Sales Executive": "Focus on sales funnel, objection handling, CRM tools, cold calling, relationship building.",
    "Custom Role": "Ask broad professional interview questions relevant to the role specified by the user."
}

# DIFFICULTY_GUIDE = {
#     "Easy": "Ask a basic, beginner-friendly question. Simple definitions, concepts, or straightforward scenarios.",
#     "Medium": "Ask a moderate question requiring some practical knowledge and application.",
#     "Hard": "Ask a challenging question requiring deep understanding, system design, or complex problem solving."
# }

# DIFFICULTY_GUIDE = {
#     "Easy": (
#         "Ask a very basic beginner-friendly question. "
#         "This should be answerable by someone who just started learning. "
#         "Focus on simple definitions, 'what is X', 'explain X simply', or 'give an example of X'. "
#         "Do NOT ask about complex algorithms, linked lists, hash maps, system design, or coding challenges. "
#         "Examples: 'What is a variable?', 'What is a function?', 'What is OOP?', 'What is an API?'"
#     ),
#     "Medium": (
#         "Ask a moderate question requiring some practical knowledge. "
#         "The person should have 1-2 months of study/experience to answer this. "
#         "Can include simple comparisons, basic code concepts, or common interview topics. "
#         "Examples: 'Difference between list and tuple', 'What is recursion with example', 'Explain GET vs POST'"
#     ),
#     "Hard": (
#         "Ask a challenging question requiring strong understanding. "
#         "Include system design, algorithms, complex data structures, or deep concepts. "
#         "Examples: 'Design a URL shortener', 'Explain Big O for common algorithms', 'How does a hash map work internally'"
#     )
# }
DIFFICULTY_GUIDE = {
    "Easy": (
        "Ask a very basic beginner-friendly question. "
        "Focus on simple definitions, introductory concepts, basic terminology, and fundamental ideas. "
        "The candidate should be able to answer after just starting to learn the field. "
        "Avoid scenario-based, analytical, strategic, or technical deep-dive questions."
    ),

    "Medium": (
        "Ask an early-intermediate question. "
        "Assume the candidate has basic knowledge and limited practical exposure. "
        "Focus on simple comparisons, common workflows, basic use cases, everyday situations, and practical understanding. "
        "Do NOT ask advanced, strategic, architectural, analytical, optimization, leadership, or expert-level questions. "
        "The candidate should be able to answer after a few weeks or months of learning."
    ),

    "Hard": (
        "Ask a challenging interview question requiring strong practical understanding. "
        "Include real-world scenarios, problem solving, decision making, troubleshooting, advanced concepts, strategy, architecture, optimization, leadership considerations, or deep domain knowledge."
    )
}

# def generate_question(role, experience_level, difficulty="Easy", topics_covered=[], weak_topics="", custom_role=""):
#     role_context = ROLE_CONTEXT.get(role, ROLE_CONTEXT["Custom Role"])
#     if role == "Custom Role" and custom_role:
#         role_display = custom_role
#         role_context = f"Ask relevant professional interview questions for the role of {custom_role}."
#     else:
#         role_display = role

#     avoid = f"Do NOT ask about: {', '.join(topics_covered[-10:])}" if topics_covered else ""
#     target = f"Focus especially on weak areas: {weak_topics}" if weak_topics else ""
#     difficulty_instruction = DIFFICULTY_GUIDE.get(difficulty, DIFFICULTY_GUIDE["Easy"])

#     prompt = f"""
# You are an expert interviewer for {role_display} positions.
# Experience level of candidate: {experience_level}
# Difficulty level: {difficulty} - {difficulty_instruction}
# {role_context}
# {avoid}
# {target}

# Generate ONE interview question appropriate for this role, experience level, and difficulty.
# Make it specific, realistic, and commonly asked in real interviews.
# Return ONLY the question. No numbering, no explanation, no extra text. No emojis.
# """
#     return call_groq(prompt)

# def get_feedback(role, question, answer, experience_level, custom_role=""):
#     role_display = custom_role if role == "Custom Role" and custom_role else role

#     prompt = f"""
# You are an expert interviewer evaluating a candidate for a {role_display} position.
# Experience level: {experience_level}
# Question asked: {question}
# Candidate answer: {answer}

# STRICT RULES:
# - Do NOT use any emojis anywhere at all
# - No blank lines between bullet points
# - Keep each section compact and concise
# - For resources, you MUST provide real working URLs

# Respond in EXACTLY this format:

# SCORE: X/10

# WHAT YOU GOT RIGHT:
# - [point 1]
# - [point 2]

# WHAT WAS MISSING:
# - [point 1]
# - [point 2]

# IDEAL ANSWER:
# - [key point 1]
# - [key point 2]
# - [key point 3]

# TIP TO IMPROVE:
# [one specific actionable tip in 1-2 sentences]

# RESOURCES:
# - [Resource name]: https://[real-url]
# - [Resource name]: https://[real-url]
# - [Resource name]: https://[real-url]

# For resources, only use these trusted sites with real URLs:
# geeksforgeeks.org, freecodecamp.org, developer.mozilla.org, w3schools.com,
# youtube.com/results?search_query=, coursera.org, roadmap.sh,
# docs.python.org, leetcode.com, hackerrank.com, atlassian.com/agile,
# hubspot.com/marketing, productplan.com, interviewbit.com
# """
#     return call_groq(prompt)

def generate_question(role, experience_level, difficulty="Easy", topics_covered=None, weak_topics="", custom_role=""):
    if topics_covered is None:
        topics_covered = []

    role_context = ROLE_CONTEXT.get(role, ROLE_CONTEXT["Custom Role"])

    if role == "Custom Role" and custom_role:
        role_display = custom_role
        role_context = f"Ask relevant professional interview questions for the role of {custom_role}."
    else:
        role_display = role

    difficulty_instruction = DIFFICULTY_GUIDE.get(
        difficulty,
        DIFFICULTY_GUIDE["Easy"]
    )

    previous_questions = "\n".join(
        [f"- {q}" for q in topics_covered[-20:]]
    ) if topics_covered else "None"

    target = f"""
Focus especially on these weak areas:
{weak_topics}
""" if weak_topics else ""

    prompt = f"""
You are an expert interviewer for {role_display} positions.

Experience Level:
{experience_level}

Difficulty:
{difficulty}

Difficulty Instructions:
{difficulty_instruction}

Role Focus:
{role_context}

Previously Asked Questions:
{previous_questions}

{target}

IMPORTANT RULES:

1. NEVER repeat any previous question.

2. NEVER ask about the same concept, topic, skill, framework, tool, methodology, or subject that appears in the previously asked questions.

3. Even if the wording is different, avoid asking about the same underlying concept again.

Examples:
- If OOP was already asked, do not ask Class/Object/Inheritance next.
- If SEO was already asked, do not ask keyword research immediately after.
- If SQL was already asked, do not ask joins immediately after.
- If recruitment was already asked, do not ask sourcing immediately after.
- If Docker was already asked, do not ask Kubernetes immediately after.
- If Excel formulas were already asked, do not ask VLOOKUP immediately after.

4. Prioritize TOPIC DIVERSITY.

5. Cover as many different concepts as possible before repeating any topic.

6. If weak areas are provided, prioritize them ONLY if they were not recently asked.

7. Generate realistic interview questions commonly asked in actual interviews.

8. For Easy difficulty:
   - Focus on beginner concepts.
   - Avoid repeating definition questions.
   - Rotate across different beginner topics.

9. For Medium difficulty:
   - Focus on practical scenarios, comparisons, and real-world applications.

10. For Hard difficulty:
    - Focus on deep understanding, strategy, architecture, case studies, advanced concepts, and problem-solving.

11. The question must be significantly different from the last 20 questions.

12. Avoid generating near-duplicate questions.

13. If the candidate has already seen many questions, deliberately choose an untouched area of the role instead of returning to familiar topics.

Return ONLY the interview question.

No numbering.
No explanation.
No extra text.
No emojis.
"""

    return call_groq(prompt)

def get_feedback(role, question, answer, experience_level, custom_role=""):
    role_display = custom_role if role == "Custom Role" and custom_role else role

    prompt = f"""
You are an expert interviewer evaluating a candidate for a {role_display} position.
Experience level: {experience_level}
Question asked: {question}
Candidate answer: {answer}

STRICT RULES:
- Do NOT use any emojis anywhere at all
- No blank lines between bullet points
- Keep each section compact and concise
- For resources, you MUST provide real working URLs

Respond in EXACTLY this format:

SCORE: X/10

WHAT YOU GOT RIGHT:
- [point 1]
- [point 2]

WHAT WAS MISSING:
- [point 1]
- [point 2]

IDEAL ANSWER:
- [key point 1]
- [key point 2]
- [key point 3]

TIP TO IMPROVE:
[one specific actionable tip in 1-2 sentences]

RESOURCES:
- [Resource name]&#58; https://[real-url]
- [Resource name]&#58; https://[real-url]
- [Resource name]&#58; https://[real-url]

For resources, only use these trusted sites with real URLs:
geeksforgeeks.org, freecodecamp.org, developer.mozilla.org, w3schools.com,
youtube.com/results?search_query=, coursera.org, roadmap.sh,
docs.python.org, leetcode.com, hackerrank.com, atlassian.com/agile,
hubspot.com/marketing, productplan.com, interviewbit.com
"""
    return call_groq(prompt)