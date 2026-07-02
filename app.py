import streamlit as st
import asyncio
import re
import uuid
from datetime import datetime
from interviewer import generate_question, get_feedback, ROLE_CONTEXT
from memory import save_answer, get_user_profile, get_weak_topics, setup_memory, save_full_state, load_full_state, get_topic_study_plan, save_full_state_sync, load_full_state_sync, save_full_state_sync, load_full_state_sync

st.set_page_config(page_title="RecallReady", page_icon="R", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0a0a0f;
    color: #f0f0f0;
}
.main { background-color: #0a0a0f; }
.block-container { background-color: #0a0a0f; padding-top: 2rem; }

.hero-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #6c63ff55;
    border-radius: 20px;
    padding: 48px;
    margin-bottom: 32px;
}
.hero-card h1 { color: #ffffff; font-size: 2.8rem; font-weight: 700; margin: 0 0 8px 0; letter-spacing: -0.5px; }
.hero-card p { color: #c0c0d8; font-size: 1.1rem; margin: 0; line-height: 1.6; }

.feature-box { background: #14142a; border: 1px solid #3a3a5a; border-radius: 14px; padding: 18px 20px; margin-bottom: 10px; }
.feature-title { color: #d0c8ff; font-weight: 600; font-size: 0.95rem; margin-bottom: 4px; }
.feature-desc { color: #8888aa; font-size: 0.85rem; }

.user-id-box {
    background: linear-gradient(135deg, #12122a, #1a1a3e);
    border: 2px solid #6c63ff77;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 16px 0;
}
.user-id-label { color: #9090c0; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 8px; }
.user-id-code { color: #b0a8ff; font-size: 1.6rem; font-weight: 700; letter-spacing: 4px; font-family: monospace; }
.user-id-hint { color: #6060a0; font-size: 0.82rem; margin-top: 8px; line-height: 1.5; }

.question-box {
    background: #14142a;
    border-left: 4px solid #7c73ff;
    border-top: 1px solid #3a3a5a;
    border-right: 1px solid #3a3a5a;
    border-bottom: 1px solid #3a3a5a;
    border-radius: 12px;
    padding: 28px;
    font-size: 1.1rem;
    font-weight: 500;
    color: #f0f0ff;
    margin: 20px 0;
    line-height: 1.7;
}

.feedback-box {
    background: #14142a;
    border: 1px solid #3a3a5a;
    border-radius: 14px;
    padding: 28px;
    line-height: 2;
    color: #e0e0f8;
    font-size: 0.95rem;
}

.score-great { background: #0a2a0a; border: 2px solid #3a8a3a; border-radius: 12px; padding: 16px 20px; color: #80ff80; font-weight: 700; font-size: 1.1rem; margin-bottom: 16px; }
.score-ok { background: #2a1e0a; border: 2px solid #8a6a2a; border-radius: 12px; padding: 16px 20px; color: #ffcc60; font-weight: 700; font-size: 1.1rem; margin-bottom: 16px; }
.score-bad { background: #2a0a0a; border: 2px solid #8a2a2a; border-radius: 12px; padding: 16px 20px; color: #ff7070; font-weight: 700; font-size: 1.1rem; margin-bottom: 16px; }

.stat-card { background: #14142a; border: 1px solid #3a3a5a; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 10px; }
.stat-number { font-size: 2.2rem; font-weight: 700; color: #9d95ff; line-height: 1; }
.stat-label { color: #7070a0; font-size: 0.78rem; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }

.badge { background: #252550; color: #b0aaff; border: 1px solid #5a54cc; border-radius: 20px; padding: 4px 16px; font-weight: 600; font-size: 0.85rem; display: inline-block; }
.diff-easy { background: #0a2a12; color: #80ff90; border: 1px solid #3a8a4a; border-radius: 8px; padding: 4px 12px; font-weight: 600; font-size: 0.82rem; display: inline-block; }
.diff-medium { background: #2a1e0a; color: #ffcc60; border: 1px solid #8a6a2a; border-radius: 8px; padding: 4px 12px; font-weight: 600; font-size: 0.82rem; display: inline-block; }
.diff-hard { background: #2a0a0a; color: #ff7070; border: 1px solid #8a2a2a; border-radius: 8px; padding: 4px 12px; font-weight: 600; font-size: 0.82rem; display: inline-block; }

.section-label { color: #8080b0; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; margin-bottom: 6px; }

.welcome-back { background: #14142a; border: 1px solid #3a3a5a; border-radius: 16px; padding: 32px; text-align: center; margin-bottom: 24px; }
.welcome-back h3 { color: #d0c8ff; font-size: 1.3rem; margin-bottom: 6px; }
.welcome-back p { color: #8080aa; font-size: 0.9rem; margin-bottom: 0; }

.rec-hint { background: #0f0f2a; border: 1px solid #3a3a5a; border-radius: 10px; padding: 14px 18px; color: #8080b0; font-size: 0.88rem; line-height: 1.5; }

.report-card {
    background: linear-gradient(160deg, #0f0f1a 0%, #1a1a3e 50%, #0f2040 100%);
    border: 2px solid #6c63ff66;
    border-radius: 20px;
    padding: 28px 32px;
    text-align: center;
    margin: 12px 0;
}
.report-title { color: #9090c0; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; margin-bottom: 8px; }
.report-name { color: #ffffff; font-size: 1.2rem; font-weight: 700; margin-bottom: 2px; }
.report-role { color: #7070a0; font-size: 0.85rem; margin-bottom: 16px; }
.report-score { font-size: 3.5rem; font-weight: 800; line-height: 1; margin-bottom: 4px; letter-spacing: -2px; }
.report-grade { font-size: 0.85rem; font-weight: 700; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 2px; }
.report-divider { border: none; border-top: 1px solid #2a2a4a; margin: 16px 0; }

.q-breakdown-card {
    background: #0f0f1a;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 16px;
}

.study-plan-box { background: #14142a; border: 1px solid #3a3a5a; border-radius: 14px; padding: 24px; margin-bottom: 16px; }
.topic-pill { background: #0f0f2a; border: 1px solid #3a3a6a; border-radius: 10px; padding: 14px 18px; margin-bottom: 10px; }

.stButton > button {
    background: linear-gradient(135deg, #7c5cf6 0%, #5c53ef 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    padding: 12px 24px;
    font-weight: 700;
    font-size: 0.95rem;
    width: 100%;
    letter-spacing: 0.3px;
    transition: all 0.2s;
    box-shadow: 0 4px 16px #6c63ff44;
}
.stButton > button:hover { background: linear-gradient(135deg, #9d80ff, #7c73ee); transform: translateY(-1px); box-shadow: 0 6px 24px #6c63ff66; }
.stButton > button:active { transform: translateY(0); }

.stTextInput input { background: #14142a !important; border: 1px solid #3a3a5a !important; border-radius: 10px !important; color: #f0f0f0 !important; padding: 12px 16px !important; }
.stTextInput input:focus { border-color: #7c73ff !important; box-shadow: 0 0 0 2px #6c63ff33 !important; }
.stTextArea textarea { background: #14142a !important; border: 1px solid #3a3a5a !important; border-radius: 12px !important; color: #f0f0f0 !important; font-size: 0.95rem !important; padding: 16px !important; line-height: 1.6 !important; }
.stTextArea textarea::placeholder { color: #5050a0 !important; }
.stSelectbox > div > div { background: #14142a !important; border: 1px solid #3a3a5a !important; border-radius: 10px !important; color: #f0f0f0 !important; }
div[data-testid="stRadio"] > div { background: #14142a; border: 1px solid #3a3a5a; border-radius: 10px; padding: 10px 16px; }
div[data-testid="stRadio"] label { color: #d0d0f0 !important; font-weight: 500; }
.stCheckbox label { color: #b0b0d0 !important; font-size: 0.95rem; }
iframe[title="streamlit_mic_recorder"] {
    height: 44px !important;
    width: auto !important;
    max-width: 200px !important;
    border: none !important;
    background: transparent !important;
    border-radius: 10px !important;
}
div[data-testid="stCustomComponentV1"] {
    background: transparent !important;
    width: auto !important;
    max-width: 200px !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}
div[data-testid="element-container"]:has(iframe[title="streamlit_mic_recorder"]) {
    width: auto !important;
    display: inline-block !important;
}
div[data-testid="stTabs"] button { color: #8080b0 !important; font-weight: 600; }
div[data-testid="stTabs"] button[aria-selected="true"] { color: #c0b8ff !important; }
h1, h2, h3, h4 { color: #e8e8ff; }
p { color: #b0b0d0; }

.header-bar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; padding: 16px 0 12px 0; border-bottom: 1px solid #2a2a4a; margin-bottom: 0; }
.header-title { font-size: 1.6rem; font-weight: 700; color: #ffffff; letter-spacing: -0.3px; }

@keyframes glow-pulse {
    0% { box-shadow: 0 0 0 0 #6c63ff55; }
    50% { box-shadow: 0 0 24px 8px #6c63ff33; }
    100% { box-shadow: 0 0 0 0 #6c63ff00; }
}
.score-pulse { animation: glow-pulse 1.5s ease-in-out; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

defaults = {
    "user_setup_done": False,
    "user_name": "",
    "display_name": "",
    "user_uid": "",
    "user_role": "",
    "custom_role": "",
    "experience_level": "",
    "difficulty": "Easy",
    "current_question": None,
    "topics_covered": [],
    "scores": [],
    "history": [],
    "show_feedback": False,
    "current_feedback": "",
    "current_score": 0,
    "is_returning_user": False,
    "show_change_role": False,
    "name_input": "",
    "uid_input": "",
    "mock_mode": False,
    "mock_questions": [],
    "mock_answers": [],
    "mock_scores": [],
    "mock_feedbacks": [],
    "mock_current": 0,
    "mock_done": False,
    "mock_showing_feedback": False,
    "score_history": [],
    "study_plan": "",
    "generated_uid": "",
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

if not st.session_state.generated_uid:
    st.session_state.generated_uid = str(uuid.uuid4())[:8].upper()

def render_feedback(text):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F9FF"
        u"\U00002700-\U000027BF"
        u"\U0001F1E0-\U0001F1FF"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    text = re.sub(r'(https?://[^\s\)\]<>]+)', r'<a href="\1" target="_blank" style="color:#a090ff;text-decoration:underline;font-weight:600;">\1</a>', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    paragraphs = text.split('\n\n')
    html_parts = []
    for p in paragraphs:
        p = p.replace('\n', '<br>')
        html_parts.append(f'<div style="margin-bottom:16px;">{p}</div>')
    return ''.join(html_parts)

def score_banner(score, prefix="Score"):
    if score >= 7:
        return f'<div class="score-great score-pulse">{prefix}: {score}/10 — Strong answer</div>'
    elif score >= 5:
        return f'<div class="score-ok score-pulse">{prefix}: {score}/10 — Decent, keep improving</div>'
    else:
        return f'<div class="score-bad score-pulse">{prefix}: {score}/10 — Needs more work</div>'

def get_grade(avg):
    if avg >= 8.5: return "S", "#f0d040", "Outstanding"
    if avg >= 7: return "A", "#70ff70", "Strong"
    if avg >= 5.5: return "B", "#b0a8ff", "Good"
    if avg >= 4: return "C", "#ffcc60", "Average"
    return "D", "#ff7070", "Needs Work"

def persist_state(role_override=None):
    """
    Saves the CURRENT session state (score_history, history, study_plan)
    to Supabase under the given role (or the current role if not specified).
    The storage key is based on user_uid + role ONLY (not the display name),
    so slight differences in how the name is typed never break persistence.
    Always pass role_override explicitly when saving BEFORE a role switch,
    so it doesn't accidentally save under the new role.
    """
    if role_override:
        role_d = role_override
    else:
        role_d = st.session_state.custom_role if st.session_state.user_role == "Custom Role" else st.session_state.user_role

    if not role_d:
        return

    save_full_state_sync(
        st.session_state.user_uid,
        role_d,
        st.session_state.score_history,
        st.session_state.history,
        st.session_state.study_plan
    )

def load_role_state(role_d):
    """
    Loads saved state for a specific role from Supabase and applies it
    to session state. Keyed on user_uid + role only. Used both on first
    login and on every role switch.
    """
    past_scores, past_history, past_plan = load_full_state_sync(st.session_state.user_uid, role_d)
    st.session_state.score_history = past_scores if past_scores else []
    st.session_state.history = past_history if past_history else []
    st.session_state.scores = [s["score"] for s in st.session_state.score_history]
    st.session_state.study_plan = past_plan if past_plan else ""

# SCREEN 1: Setup
if not st.session_state.user_setup_done:
    st.markdown("""
    <div class="hero-card">
        <h1>RecallReady</h1>
        <p>The AI interviewer that remembers you. Practice smarter — it tracks your weak spots,
        adapts to your level, and gets harder as you improve.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        returning = st.checkbox("I have used RecallReady before — load my memory")
        st.markdown('<div class="section-label" style="margin-top:8px;">Name</div>', unsafe_allow_html=True)
        st.text_input("Name", placeholder="e.g. Priya Sharma", label_visibility="collapsed", key="name_input")

        if not returning:
            uid = st.session_state.generated_uid
            st.markdown(f"""
            <div class="user-id-box">
                <div class="user-id-label">Your Unique RecallReady ID</div>
                <div class="user-id-code">{uid}</div>
                <div class="user-id-hint">
                    Save this — screenshot it or write it down.<br>
                    Enter it next time with the same name to restore everything.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="section-label" style="margin-top:16px;">Your RecallReady ID</div>', unsafe_allow_html=True)
            st.markdown('<div style="color:#6060a0;font-size:0.82rem;margin-bottom:6px;">Enter the exact same name and ID from your first session.</div>', unsafe_allow_html=True)
            st.text_input("Your ID", placeholder="e.g. A3F9B2C1", label_visibility="collapsed", key="uid_input")

        st.markdown('<div class="section-label" style="margin-top:16px;">Target Role</div>', unsafe_allow_html=True)
        role_options = ["Select a Role"] + list(ROLE_CONTEXT.keys())
        role = st.selectbox("Role", role_options, index=0, label_visibility="collapsed")

        custom_role_input = ""
        if role == "Custom Role":
            st.markdown('<div class="section-label" style="margin-top:12px;">Specify Role</div>', unsafe_allow_html=True)
            custom_role_input = st.text_input("Custom Role", placeholder="e.g. Growth Hacker", label_visibility="collapsed", key="custom_role_input")

        st.markdown('<div class="section-label" style="margin-top:16px;">Experience Level</div>', unsafe_allow_html=True)
        experience = st.selectbox("Experience", [
            "Fresher (0-1 years)", "Junior (1-3 years)", "Mid-level (3-5 years)",
            "Senior (5-8 years)", "Lead / Manager (8+ years)"
        ], label_visibility="collapsed")

        st.markdown('<div class="section-label" style="margin-top:16px;">Starting Difficulty</div>', unsafe_allow_html=True)
        difficulty = st.radio("Difficulty", ["Easy", "Medium", "Hard"], horizontal=True, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start Interview Session"):
            name = st.session_state.name_input.strip()
            if not name:
                st.error("Please enter your name.")
            elif returning and not st.session_state.uid_input.strip():
                st.error("Please enter your RecallReady ID.")
            elif role == "Select a Role":
                st.error("Please select a role.")
            elif role == "Custom Role" and not custom_role_input.strip():
                st.error("Please enter your custom role.")
            else:
                uid = st.session_state.uid_input.strip().upper() if returning else st.session_state.generated_uid
                asyncio.run(setup_memory())
                st.session_state.user_setup_done = True
                st.session_state.display_name = name
                st.session_state.user_uid = uid
                st.session_state.user_name = f"{name}_{uid}"
                st.session_state.user_role = role
                st.session_state.custom_role = custom_role_input.strip()
                st.session_state.experience_level = experience
                st.session_state.difficulty = difficulty
                st.session_state.is_returning_user = returning

                role_d = custom_role_input.strip() if role == "Custom Role" else role

                if returning:
                    with st.spinner("Loading your previous progress and history..."):
                        load_role_state(role_d)
                else:
                    with st.spinner("Preparing your first question..."):
                        q = generate_question(role, experience, difficulty, custom_role=custom_role_input.strip())
                        st.session_state.current_question = q
                        st.session_state.topics_covered.append(q)
                st.rerun()

    with col2:
        st.markdown('<div class="section-label">Why RecallReady</div>', unsafe_allow_html=True)
        for title, desc in [
            ("Unique Memory Per User", "Each user gets a unique ID — your memory and progress are completely private"),
            ("Everything Saved Across Sessions", "Progress, history and study plan all reload when you return with your ID"),
            ("Per-Role Progress", "Each role you practice keeps its own separate history, scores and study plan"),
            ("Targets Weak Spots", "Detects where you struggle and focuses questions there automatically"),
            ("Mock Interview Mode", "5-question sessions Easy to Hard with a full graded report card"),
            ("AI Topic Study Plan", "Identifies underlying topics you struggle with and gives real learning resources"),
            ("Any Role", "Software, Marketing, Product, HR, Finance — fully personalised"),
        ]:
            st.markdown(f'<div class="feature-box"><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>', unsafe_allow_html=True)

# SCREEN 2: Main App
else:
    role_display = st.session_state.custom_role if st.session_state.user_role == "Custom Role" else st.session_state.user_role

    diff_class = f"diff-{st.session_state.difficulty.lower()}"
    col_h1, col_h2, col_h3, col_h4 = st.columns([4, 1, 1, 1])
    with col_h1:
        st.markdown(f"""
        <div class="header-bar">
            <span class="header-title">RecallReady</span>
            <span class="badge">{role_display}</span>
            <span class="{diff_class}">{st.session_state.difficulty}</span>
            <span style="color:#7070a0;font-size:0.85rem;">{st.session_state.display_name} &middot; {st.session_state.experience_level}</span>
            <span style="color:#3a3a6a;font-size:0.75rem;font-family:monospace;">ID: {st.session_state.user_uid}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        new_diff = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"],
            index=["Easy", "Medium", "Hard"].index(st.session_state.difficulty),
            key="diff_selector", label_visibility="collapsed")
        if new_diff != st.session_state.difficulty:
            st.session_state.difficulty = new_diff
            st.rerun()
    with col_h3:
        if st.button("Change Role"):
            st.session_state.show_change_role = not st.session_state.show_change_role
            st.rerun()
    with col_h4:
        if st.button("New Session"):
            persist_state()
            for key in defaults:
                st.session_state[key] = defaults[key]
            st.rerun()

    if st.session_state.show_change_role:
        st.markdown('<hr style="border:1px solid #2a2a4a;margin:8px 0 16px 0;">', unsafe_allow_html=True)
        cr1, cr2, cr3 = st.columns([3, 3, 2])
        with cr1:
            st.markdown('<div class="section-label">New Role</div>', unsafe_allow_html=True)
            new_role_options = ["Select a Role"] + list(ROLE_CONTEXT.keys())
            new_role = st.selectbox("New Role", new_role_options, index=0, key="new_role_select", label_visibility="collapsed")
        with cr2:
            st.markdown('<div class="section-label">Experience Level</div>', unsafe_allow_html=True)
            new_exp = st.selectbox("Experience Level", [
                "Fresher (0-1 years)", "Junior (1-3 years)", "Mid-level (3-5 years)",
                "Senior (5-8 years)", "Lead / Manager (8+ years)"
            ], key="new_exp", label_visibility="collapsed")
        with cr3:
            new_custom = ""
            if new_role == "Custom Role":
                st.markdown('<div class="section-label">Role Name</div>', unsafe_allow_html=True)
                new_custom = st.text_input("Role Name", key="new_custom_role", placeholder="e.g. Growth Hacker", label_visibility="collapsed")
            else:
                st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Apply Changes"):
                if new_role == "Select a Role":
                    st.error("Please select a role.")
                elif new_role == "Custom Role" and not new_custom.strip():
                    st.error("Please enter your custom role name.")
                else:
                    # 1. Save the CURRENT (old) role's state before switching away from it.
                    old_role_d = st.session_state.custom_role if st.session_state.user_role == "Custom Role" else st.session_state.user_role
                    persist_state(role_override=old_role_d)

                    # 2. Switch role in session state.
                    st.session_state.user_role = new_role
                    st.session_state.custom_role = new_custom
                    st.session_state.experience_level = new_exp
                    st.session_state.current_question = None
                    st.session_state.show_feedback = False
                    st.session_state.topics_covered = []
                    st.session_state.show_change_role = False

                    new_role_d = new_custom if new_role == "Custom Role" else new_role

                    # 3. Load the NEW role's saved state from Supabase (do NOT wipe to empty).
                    with st.spinner(f"Loading your {new_role_d} progress..."):
                        load_role_state(new_role_d)

                    role_display = new_role_d
                    with st.spinner("Generating first question for new role..."):
                        q = generate_question(new_role, new_exp, st.session_state.difficulty, custom_role=new_custom)
                        st.session_state.current_question = q
                        st.session_state.topics_covered.append(q)
                    st.rerun()
        st.markdown('<hr style="border:1px solid #2a2a4a;margin:16px 0 8px 0;">', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["Practice", "Mock Interview", "Progress", "Study Plan"])

    # TAB 1: Practice
    with tab1:
        main_col, side_col = st.columns([2, 1], gap="large")
        with main_col:
            if st.session_state.is_returning_user and not st.session_state.current_question:
                loaded_msg = f"Loaded {len(st.session_state.history)} previous answers. Choose how to continue." if st.session_state.history else "No previous answers found for this ID. Starting fresh."
                st.markdown(f'<div class="welcome-back"><h3>Welcome back, {st.session_state.display_name}</h3><p>{loaded_msg}</p></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("New Random Question", key="ret_new"):
                        with st.spinner("Generating question..."):
                            q = generate_question(st.session_state.user_role, st.session_state.experience_level, st.session_state.difficulty, st.session_state.topics_covered, custom_role=st.session_state.custom_role)
                            st.session_state.current_question = q
                            st.session_state.show_feedback = False
                            st.session_state.topics_covered.append(q)
                            st.rerun()
                with c2:
                    if st.button("Target My Weak Areas", key="ret_weak"):
                        with st.spinner("Checking your memory..."):
                            weak = asyncio.run(get_weak_topics(st.session_state.user_uid, role_display, display_name=st.session_state.display_name))
                            q = generate_question(st.session_state.user_role, st.session_state.experience_level, st.session_state.difficulty, st.session_state.topics_covered, weak_topics=weak, custom_role=st.session_state.custom_role)
                            st.session_state.current_question = q
                            st.session_state.show_feedback = False
                            st.session_state.topics_covered.append(q)
                            st.rerun()

            if st.session_state.current_question:
                st.markdown(f'<div class="question-box">{st.session_state.current_question}</div>', unsafe_allow_html=True)

                if not st.session_state.show_feedback:
                    st.markdown('<div class="section-label">Your Answer</div>', unsafe_allow_html=True)
                    answer_method = st.radio("Answer via", ["Type", "Voice"], horizontal=True, label_visibility="collapsed", key="practice_method")
                    user_answer = ""
                    if answer_method == "Type":
                        user_answer = st.text_area("Answer", height=200, placeholder="Type your answer here. The more detail you give, the better the feedback.", label_visibility="collapsed", key="typed_answer")
                    else:
                        try:
                            from streamlit_mic_recorder import mic_recorder
                            rc1, rc2 = st.columns([0.65, 2.35])
                            with rc1:
                                audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", use_container_width=False, key="mic_practice")
                            with rc2:
                                st.markdown('<div class="rec-hint">Click <b style="color:#a090ff">Start Recording</b>, speak clearly, then click <b style="color:#a090ff">Stop</b>.</div>', unsafe_allow_html=True)
                            if audio:
                                from voice import transcribe_audio
                                with st.spinner("Transcribing..."):
                                    user_answer = transcribe_audio(audio['bytes'])
                                st.success(f"Transcribed: {user_answer}")
                        except:
                            st.warning("Voice not available. Please type.")
                            user_answer = st.text_area("Answer", height=200, label_visibility="collapsed")

                    c1, _ = st.columns([1, 3])
                    with c1:
                        if st.button("Submit Answer", key="submit_practice"):
                            if user_answer.strip():
                                with st.spinner("Analysing your answer..."):
                                    feedback = get_feedback(st.session_state.user_role, st.session_state.current_question, user_answer, st.session_state.experience_level, custom_role=st.session_state.custom_role)
                                    try:
                                        score_line = [l for l in feedback.split('\n') if 'SCORE:' in l][0]
                                        score = float(score_line.split('/')[0].replace('SCORE:', '').strip())
                                    except:
                                        score = 5.0
                                    new_entry = {"q": st.session_state.current_question[:40], "score": score, "time": datetime.now().strftime("%H:%M")}
                                    st.session_state.scores.append(score)
                                    st.session_state.score_history.append(new_entry)
                                    st.session_state.history.append({
                                        "question": st.session_state.current_question,
                                        "answer": user_answer,
                                        "score": score
                                    })
                                    st.session_state.current_feedback = feedback
                                    st.session_state.current_score = score
                                    st.session_state.show_feedback = True
                                    asyncio.run(save_answer(st.session_state.user_uid, role_display, st.session_state.current_question, user_answer, feedback, score, display_name=st.session_state.display_name))
                                    persist_state()
                                st.rerun()
                            else:
                                st.warning("Please enter an answer.")
                else:
                    st.markdown(score_banner(st.session_state.current_score), unsafe_allow_html=True)
                    st.markdown(f'<div class="feedback-box">{render_feedback(st.session_state.current_feedback)}</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Next Question", key="next_practice"):
                            with st.spinner("Generating..."):
                                q = generate_question(st.session_state.user_role, st.session_state.experience_level, st.session_state.difficulty, st.session_state.topics_covered, custom_role=st.session_state.custom_role)
                                st.session_state.current_question = q
                                st.session_state.show_feedback = False
                                st.session_state.topics_covered.append(q)
                                st.rerun()
                    with c2:
                        if st.button("Practice Weak Area", key="weak_practice"):
                            with st.spinner("Checking memory..."):
                                weak = asyncio.run(get_weak_topics(st.session_state.user_uid, role_display, display_name=st.session_state.display_name))
                                q = generate_question(st.session_state.user_role, st.session_state.experience_level, st.session_state.difficulty, st.session_state.topics_covered, weak_topics=weak, custom_role=st.session_state.custom_role)
                                st.session_state.current_question = q
                                st.session_state.show_feedback = False
                                st.session_state.topics_covered.append(q)
                                st.rerun()

        with side_col:
            st.markdown(f"""
            <div class="user-id-box" style="margin-bottom:16px;">
                <div class="user-id-label">Your RecallReady ID</div>
                <div class="user-id-code">{st.session_state.user_uid}</div>
                <div class="user-id-hint">Save this to restore your memory and progress next session.</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-label">Session Stats</div>', unsafe_allow_html=True)
            if st.session_state.scores:
                avg = sum(st.session_state.scores) / len(st.session_state.scores)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(st.session_state.scores)}</div><div class="stat-label">Questions</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-card"><div class="stat-number">{avg:.1f}</div><div class="stat-label">Avg Score</div></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stat-card"><div class="stat-number">{max(st.session_state.scores)}/10</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)
                if avg >= 7: st.success("Strong performance. Keep it up.")
                elif avg >= 5: st.warning("Making progress. Stay consistent.")
                else: st.error("Needs more practice. Focus on basics.")
            else:
                st.markdown('<div class="stat-card"><div style="color:#6060a0;font-size:0.88rem;padding:8px 0;">Answer questions to see your stats</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("View Memory Profile", key="mem_btn"):
                with st.spinner("Loading from memory..."):
                    profile = asyncio.run(get_user_profile(st.session_state.user_uid, role_display, display_name=st.session_state.display_name))
                    st.info(profile)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.session_state.history:
                st.markdown('<div class="section-label">Recent History</div>', unsafe_allow_html=True)
                for item in reversed(st.session_state.history[-5:]):
                    color = "#80ff80" if item['score'] >= 7 else "#ffcc60" if item['score'] >= 5 else "#ff7070"
                    label = "Pass" if item['score'] >= 7 else "Average" if item['score'] >= 5 else "Fail"
                    with st.expander(f"{item['score']}/10 — {item['question'][:40]}..."):
                        st.markdown(f'<span style="color:{color};font-weight:700;">{label}</span>', unsafe_allow_html=True)
                        st.write(item['question'])

    # TAB 2: Mock Interview
    with tab2:
        MOCK_TOTAL = 5
        if not st.session_state.mock_mode and not st.session_state.mock_done:
            st.markdown("""
            <div class="report-card">
                <div class="report-title">Mock Interview Mode</div>
                <div class="report-name">5 Questions. Real Pressure. Full Report.</div>
                <div class="report-role">Questions progress from Easy to Hard — just like a real interview</div>
                <div style="display:flex;justify-content:center;gap:12px;margin-top:16px;flex-wrap:wrap;">
                    <div style="background:#0a2a12;border:1px solid #3a8a4a;border-radius:8px;padding:6px 16px;color:#80ff90;font-size:0.82rem;font-weight:600;">Q1-2: Easy</div>
                    <div style="background:#2a1e0a;border:1px solid #8a6a2a;border-radius:8px;padding:6px 16px;color:#ffcc60;font-size:0.82rem;font-weight:600;">Q3-4: Medium</div>
                    <div style="background:#2a0a0a;border:1px solid #8a2a2a;border-radius:8px;padding:6px 16px;color:#ff7070;font-size:0.82rem;font-weight:600;">Q5: Hard</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1, 1, 1])
            with c2:
                if st.button("Start Mock Interview", key="start_mock"):
                    with st.spinner("Preparing 5 questions..."):
                        qs = []
                        for diff in ["Easy", "Easy", "Medium", "Medium", "Hard"]:
                            q = generate_question(st.session_state.user_role, st.session_state.experience_level, diff, qs, custom_role=st.session_state.custom_role)
                            qs.append(q)
                        st.session_state.mock_questions = qs
                        st.session_state.mock_answers = []
                        st.session_state.mock_scores = []
                        st.session_state.mock_feedbacks = []
                        st.session_state.mock_current = 0
                        st.session_state.mock_done = False
                        st.session_state.mock_showing_feedback = False
                        st.session_state.mock_mode = True
                    st.rerun()

        elif st.session_state.mock_mode and not st.session_state.mock_done:
            curr = st.session_state.mock_current
            difficulties = ["Easy", "Easy", "Medium", "Medium", "Hard"]
            diff_colors = {"Easy": "#80ff90", "Medium": "#ffcc60", "Hard": "#ff7070"}
            d = difficulties[curr]

            prog_html = '<div style="display:flex;gap:6px;margin-bottom:20px;">'
            for i in range(MOCK_TOTAL):
                if i < curr:
                    s = st.session_state.mock_scores[i]
                    c = "#70ff70" if s >= 7 else "#ffcc60" if s >= 5 else "#ff7070"
                    prog_html += f'<div style="flex:1;height:8px;background:{c};border-radius:4px;"></div>'
                elif i == curr:
                    prog_html += f'<div style="flex:1;height:8px;background:#7c73ff;border-radius:4px;"></div>'
                else:
                    prog_html += f'<div style="flex:1;height:8px;background:#2a2a4a;border-radius:4px;"></div>'
            prog_html += '</div>'
            st.markdown('<div class="section-label">Interview Progress</div>', unsafe_allow_html=True)
            st.markdown(prog_html, unsafe_allow_html=True)
            st.markdown(f'<div style="color:{diff_colors[d]};font-size:0.82rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">Question {curr+1} of {MOCK_TOTAL} &middot; {d}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="question-box">{st.session_state.mock_questions[curr]}</div>', unsafe_allow_html=True)

            if not st.session_state.mock_showing_feedback:
                answer_method = st.radio("Answer via", ["Type", "Voice"], horizontal=True, label_visibility="collapsed", key=f"mock_method_{curr}")
                mock_answer = ""
                if answer_method == "Type":
                    mock_answer = st.text_area("Answer", height=180, placeholder="Type your answer clearly...", label_visibility="collapsed", key=f"mock_text_{curr}")
                else:
                    try:
                        from streamlit_mic_recorder import mic_recorder
                        rc1, rc2 = st.columns([0.65, 2.35])
                        with rc1:
                            audio = mic_recorder(start_prompt="Start Recording", stop_prompt="Stop Recording", use_container_width=False, key=f"mock_mic_{curr}")
                        with rc2:
                            st.markdown('<div class="rec-hint">Click <b style="color:#a090ff">Start</b>, speak, then click <b style="color:#a090ff">Stop</b>.</div>', unsafe_allow_html=True)
                        if audio:
                            from voice import transcribe_audio
                            with st.spinner("Transcribing..."):
                                mock_answer = transcribe_audio(audio['bytes'])
                            st.success(f"Transcribed: {mock_answer}")
                    except:
                        mock_answer = st.text_area("Answer", height=180, label_visibility="collapsed", key=f"mock_text_fb_{curr}")

                c1, _ = st.columns([1, 3])
                with c1:
                    if st.button("Submit Answer", key=f"mock_submit_{curr}"):
                        if mock_answer.strip():
                            with st.spinner("Evaluating..."):
                                fb = get_feedback(st.session_state.user_role, st.session_state.mock_questions[curr], mock_answer, st.session_state.experience_level, custom_role=st.session_state.custom_role)
                                try:
                                    score_line = [l for l in fb.split('\n') if 'SCORE:' in l][0]
                                    score = float(score_line.split('/')[0].replace('SCORE:', '').strip())
                                except:
                                    score = 5.0
                                st.session_state.mock_answers.append(mock_answer)
                                st.session_state.mock_scores.append(score)
                                st.session_state.mock_feedbacks.append(fb)
                                st.session_state.mock_showing_feedback = True
                                asyncio.run(save_answer(st.session_state.user_uid, role_display, st.session_state.mock_questions[curr], mock_answer, fb, score, display_name=st.session_state.display_name))
                            st.rerun()
                        else:
                            st.warning("Please enter an answer.")
            else:
                st.markdown(score_banner(st.session_state.mock_scores[-1]), unsafe_allow_html=True)
                st.markdown(f'<div class="feedback-box" style="margin-bottom:16px;">{render_feedback(st.session_state.mock_feedbacks[-1])}</div>', unsafe_allow_html=True)
                is_last = curr == MOCK_TOTAL - 1
                c1, _ = st.columns([1, 3])
                with c1:
                    if st.button("See My Report Card" if is_last else "Next Question", key="mock_next"):
                        if not is_last:
                            st.session_state.mock_current += 1
                            st.session_state.mock_showing_feedback = False
                        else:
                            st.session_state.mock_done = True
                            st.session_state.mock_mode = False
                            for i, s in enumerate(st.session_state.mock_scores):
                                st.session_state.scores.append(s)
                                st.session_state.score_history.append({"q": st.session_state.mock_questions[i][:40], "score": s, "time": datetime.now().strftime("%H:%M")})
                                st.session_state.history.append({
                                    "question": st.session_state.mock_questions[i],
                                    "answer": st.session_state.mock_answers[i] if i < len(st.session_state.mock_answers) else "",
                                    "score": s
                                })
                            persist_state()
                        st.rerun()

        elif st.session_state.mock_done:
            avg = sum(st.session_state.mock_scores) / len(st.session_state.mock_scores)
            grade, grade_color, grade_label = get_grade(avg)
            st.markdown(f"""
            <div class="report-card">
                <div class="report-title">Interview Report Card</div>
                <div class="report-name">{st.session_state.display_name}</div>
                <div class="report-role">{role_display} &middot; {st.session_state.experience_level}</div>
                <div class="report-score" style="color:{grade_color};">{avg:.1f}</div>
                <div style="color:#6060a0;font-size:0.78rem;margin-bottom:4px;">out of 10</div>
                <div class="report-grade" style="color:{grade_color};">Grade {grade} &mdash; {grade_label}</div>
                <hr class="report-divider">
                <div style="display:flex;justify-content:center;gap:24px;flex-wrap:wrap;">
                    <div style="text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:#70ff70;">{sum(1 for s in st.session_state.mock_scores if s >= 7)}</div><div style="color:#6060a0;font-size:0.72rem;text-transform:uppercase;">Strong</div></div>
                    <div style="text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:#ffcc60;">{sum(1 for s in st.session_state.mock_scores if 5 <= s < 7)}</div><div style="color:#6060a0;font-size:0.72rem;text-transform:uppercase;">Average</div></div>
                    <div style="text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:#ff7070;">{sum(1 for s in st.session_state.mock_scores if s < 5)}</div><div style="color:#6060a0;font-size:0.72rem;text-transform:uppercase;">Weak</div></div>
                    <div style="text-align:center;"><div style="font-size:1.4rem;font-weight:700;color:#9d95ff;">{max(st.session_state.mock_scores)}/10</div><div style="color:#6060a0;font-size:0.72rem;text-transform:uppercase;">Best</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### Question Breakdown")
            difficulties = ["Easy", "Easy", "Medium", "Medium", "Hard"]
            for i, (q, s) in enumerate(zip(st.session_state.mock_questions, st.session_state.mock_scores)):
                color = "#70ff70" if s >= 7 else "#ffcc60" if s >= 5 else "#ff7070"
                label = "Strong" if s >= 7 else "Average" if s >= 5 else "Weak"
                st.markdown(f"""
                <div class="q-breakdown-card">
                    <div style="color:#6060a0;font-size:0.8rem;font-weight:600;min-width:24px;">Q{i+1}</div>
                    <div style="flex:1;"><div style="color:#d0d0f0;font-size:0.9rem;">{q[:70]}...</div><div style="font-size:0.75rem;color:#6060a0;margin-top:2px;">{difficulties[i]}</div></div>
                    <div style="font-size:1.1rem;font-weight:700;color:{color};min-width:52px;text-align:right;">{s}/10</div>
                    <div style="background:{color}22;color:{color};border:1px solid {color}55;border-radius:6px;padding:2px 10px;font-size:0.78rem;font-weight:700;">{label}</div>
                </div>
                """, unsafe_allow_html=True)
                if i < len(st.session_state.mock_feedbacks):
                    with st.expander(f"View feedback for Q{i+1}"):
                        st.markdown(f'<div class="feedback-box">{render_feedback(st.session_state.mock_feedbacks[i])}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            c1, c2, _ = st.columns([1, 1, 2])
            with c1:
                if st.button("Try Again", key="mock_retry"):
                    st.session_state.mock_done = False
                    st.session_state.mock_mode = False
                    st.session_state.mock_questions = []
                    st.session_state.mock_answers = []
                    st.session_state.mock_scores = []
                    st.session_state.mock_feedbacks = []
                    st.session_state.mock_current = 0
                    st.session_state.mock_showing_feedback = False
                    st.rerun()
            with c2:
                if st.button("Go to Practice", key="mock_to_practice"):
                    st.session_state.mock_done = False
                    st.rerun()

    # TAB 3: Progress
    with tab3:
        st.markdown("### Your Score Progress")
        all_scores = st.session_state.score_history
        if not all_scores:
            st.markdown('<div class="welcome-back" style="padding:48px;"><h3>No data yet</h3><p>Answer questions in Practice or Mock Interview to see your progress chart here.</p></div>', unsafe_allow_html=True)
        else:
            scores_list = [s["score"] for s in all_scores]
            n = len(scores_list)
            avg_score = sum(scores_list) / n
            w, h = 700, 300
            pad_l, pad_r, pad_t, pad_b = 50, 60, 30, 50
            chart_w = w - pad_l - pad_r
            chart_h = h - pad_t - pad_b

            def cx(i): return pad_l + (int(i * chart_w / (n - 1)) if n > 1 else chart_w // 2)
            def cy(s): return pad_t + int((1 - s / 10) * chart_h)

            grid = ""
            for v in [0, 2, 4, 6, 8, 10]:
                y = cy(v)
                grid += f'<line x1="{pad_l}" y1="{y}" x2="{w-pad_r}" y2="{y}" stroke="#2a2a4a" stroke-width="1"/>'
                grid += f'<text x="{pad_l-8}" y="{y+4}" fill="#6060a0" font-size="11" text-anchor="end">{v}</text>'

            area, polyline = "", ""
            if n > 1:
                pts = " ".join([f"{cx(i)},{cy(s)}" for i, s in enumerate(scores_list)])
                area = f'<polygon points="{cx(0)},{pad_t+chart_h} {pts} {cx(n-1)},{pad_t+chart_h}" fill="#7c73ff" opacity="0.1"/>'
                polyline = f'<polyline points="{pts}" fill="none" stroke="#9d95ff" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>'

            avg_y = cy(avg_score)
            avg_line = f'<line x1="{pad_l}" y1="{avg_y}" x2="{w-pad_r}" y2="{avg_y}" stroke="#6060c0" stroke-width="1.5" stroke-dasharray="4,4"/>'
            avg_label = f'<text x="{w-pad_r+4}" y="{avg_y+4}" fill="#8080c0" font-size="11">avg {avg_score:.1f}</text>'

            dots = ""
            for i, s in enumerate(scores_list):
                color = "#70ff70" if s >= 7 else "#ffcc60" if s >= 5 else "#ff7070"
                dots += f'<circle cx="{cx(i)}" cy="{cy(s)}" r="5" fill="{color}" stroke="#0a0a0f" stroke-width="2"/>'
                if n <= 15:
                    dots += f'<text x="{cx(i)}" y="{cy(s)-10}" fill="{color}" font-size="11" font-weight="bold" text-anchor="middle">{s}</text>'

            xlabels = ""
            step = max(1, n // 10)
            for i in range(0, n, step):
                xlabels += f'<text x="{cx(i)}" y="{h-10}" fill="#6060a0" font-size="10" text-anchor="middle">Q{i+1}</text>'

            svg = f'''<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;background:#0d0d1a;border-radius:16px;border:1px solid #2a2a4a;padding:8px;">
                {grid}{area}{avg_line}{avg_label}{polyline}{dots}{xlabels}
            </svg>'''
            st.markdown(svg, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            s1, s2, s3, s4 = st.columns(4)
            above7 = sum(1 for s in scores_list if s >= 7)
            with s1: st.markdown(f'<div class="stat-card"><div class="stat-number">{n}</div><div class="stat-label">Total Questions</div></div>', unsafe_allow_html=True)
            with s2: st.markdown(f'<div class="stat-card"><div class="stat-number">{avg_score:.1f}</div><div class="stat-label">Overall Average</div></div>', unsafe_allow_html=True)
            with s3: st.markdown(f'<div class="stat-card"><div class="stat-number">{max(scores_list)}/10</div><div class="stat-label">Best Score</div></div>', unsafe_allow_html=True)
            with s4: st.markdown(f'<div class="stat-card"><div class="stat-number">{int(above7/n*100)}%</div><div class="stat-label">Pass Rate</div></div>', unsafe_allow_html=True)

            if n >= 4:
                h1 = scores_list[:n//2]
                h2 = scores_list[n//2:]
                diff = sum(h2)/len(h2) - sum(h1)/len(h1)
                if diff > 0.5: st.success(f"Your scores are improving — up {diff:.1f} points on average in recent questions.")
                elif diff < -0.5: st.warning("Your recent scores are slightly lower. Try switching to Easy difficulty to rebuild confidence.")
                else: st.info("Your performance is consistent. Push to Hard difficulty to challenge yourself further.")

    # TAB 4: Study Plan
    with tab4:
        st.markdown("### Your AI Study Plan")
        st.markdown('<div style="color:#8080b0;font-size:0.9rem;margin-bottom:24px;line-height:1.6;">Unlike feedback (which evaluates one answer), this analyzes ALL your sessions to find the underlying topics you keep struggling with — and gives you a focused plan with real learning resources.</div>', unsafe_allow_html=True)

        history = st.session_state.history
        total_answered = len(history)

        if total_answered < 3:
            st.markdown(f"""
            <div class="study-plan-box" style="text-align:center;padding:40px;">
                <div style="color:#d0c8ff;font-size:1.1rem;font-weight:600;margin-bottom:8px;">Answer at least 5 questions to generate your study plan</div>
                <div style="color:#6060a0;font-size:0.9rem;">You have answered {total_answered} so far. Keep going!</div>
                <div style="margin-top:20px;display:flex;justify-content:center;gap:8px;">
                    {"".join([f'<div style="width:20px;height:20px;border-radius:50%;background:{"#7c73ff" if i < total_answered else "#2a2a4a"};"></div>' for i in range(5)])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            c1, c2, _ = st.columns([1, 1, 2])
            with c1:
                if st.button("Generate My Study Plan", key="gen_plan"):
                    with st.spinner("Analyzing all your sessions to find topic patterns..."):
                        weak_qs = [i['question'] for i in history if i['score'] < 5]
                        strong_qs = [i['question'] for i in history if i['score'] >= 7]
                        plan = asyncio.run(get_topic_study_plan(st.session_state.user_uid, role_display, weak_qs, strong_qs, display_name=st.session_state.display_name))
                        st.session_state.study_plan = plan if plan else "Could not generate plan right now. Please try again."
                        persist_state()
            with c2:
                if st.button("Refresh Plan", key="refresh_plan"):
                    st.session_state.study_plan = ""
                    st.rerun()

            if st.session_state.study_plan:
                col_p1, col_p2 = st.columns([3, 2], gap="large")
                with col_p1:
                    st.markdown('<div class="section-label">Topic-Based Study Plan</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="feedback-box" style="min-height:300px;">{render_feedback(st.session_state.study_plan)}</div>', unsafe_allow_html=True)

                with col_p2:
                    st.markdown('<div class="section-label">Quick Stats</div>', unsafe_allow_html=True)
                    weak_count = sum(1 for i in history if i['score'] < 5)
                    medium_count = sum(1 for i in history if 5 <= i['score'] < 7)
                    strong_count = sum(1 for i in history if i['score'] >= 7)

                    st.markdown(f"""
                    <div class="topic-pill">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#ff9090;font-weight:600;font-size:0.9rem;">Need Work</span>
                            <span style="color:#ff7070;font-size:1.4rem;font-weight:700;">{weak_count}</span>
                        </div>
                        <div style="color:#6060a0;font-size:0.78rem;margin-top:4px;">Topics scored below 5 — study plan targets these</div>
                    </div>
                    <div class="topic-pill">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#ffdd90;font-weight:600;font-size:0.9rem;">Developing</span>
                            <span style="color:#ffcc60;font-size:1.4rem;font-weight:700;">{medium_count}</span>
                        </div>
                        <div style="color:#6060a0;font-size:0.78rem;margin-top:4px;">Scored 5-7 — good foundation, needs polishing</div>
                    </div>
                    <div class="topic-pill">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="color:#90ff90;font-weight:600;font-size:0.9rem;">Mastered</span>
                            <span style="color:#70ff70;font-size:1.4rem;font-weight:700;">{strong_count}</span>
                        </div>
                        <div style="color:#6060a0;font-size:0.78rem;margin-top:4px;">Scored 7+ — move on to harder versions</div>
                    </div>
                    """, unsafe_allow_html=True)