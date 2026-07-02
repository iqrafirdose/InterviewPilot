
import os
import json
import streamlit as st
import cognee
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

_memory_setup_done = False

# ── In-memory cache so we don't hit Supabase on every rerun ─────
@st.cache_resource
def get_cache():
    return {}

def _make_key(identifier, role):
    """
    Builds a stable, normalized storage key of the form:
        identifier + "__" + role
    e.g. "a6d0f951__software_engineer"

    `identifier` should be the user's unique ID (uid) only — NOT the
    display name — so that persistence never breaks due to how the
    name is typed (spacing, casing, typos across sessions).
    Normalized to lowercase with spaces/dashes replaced so that the
    same role always maps to the same key, and different roles for
    the same user always map to different keys.
    """
    key = f"{identifier}__{role}"
    key = key.replace(" ", "_").replace("-", "_")
    return key.lower()

# ── Supabase helpers ─────────────────────────────────────────────
def get_supabase():
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return None

def save_full_state_sync(user_uid, role, score_history, full_history, study_plan=""):
    key = _make_key(user_uid, role)

    # Always save to in-memory cache first (instant)
    cache = get_cache()
    cache[key] = {
        "score_history": score_history,
        "full_history": full_history,
        "study_plan": study_plan
    }
    print(f"Cache saved: {key}")

    # Then save to Supabase (persistent across restarts)
    try:
        sb = get_supabase()
        if sb:
            data = {
                "user_key": key,
                "score_history": score_history,
                "full_history": full_history,
                "study_plan": study_plan,
                "updated_at": "now()"
            }
            # Upsert = insert if not exists, update if exists
            sb.table("user_data").upsert(data, on_conflict="user_key").execute()
            print(f"Supabase saved: {key}")
    except Exception as e:
        print(f"Supabase save error: {e}")

def load_full_state_sync(user_uid, role):
    key = _make_key(user_uid, role)

    # Check in-memory cache first
    cache = get_cache()
    if key in cache:
        data = cache[key]
        print(f"Cache loaded: {key}")
        return (
            data.get("score_history", []),
            data.get("full_history", []),
            data.get("study_plan", "")
        )

    # Not in cache — load from Supabase
    try:
        sb = get_supabase()
        if sb:
            result = sb.table("user_data").select("*").eq("user_key", key).execute()
            if result.data and len(result.data) > 0:
                row = result.data[0]
                score_history = row.get("score_history", [])
                full_history = row.get("full_history", [])
                study_plan = row.get("study_plan", "")

                # Store in cache for this session
                cache[key] = {
                    "score_history": score_history,
                    "full_history": full_history,
                    "study_plan": study_plan
                }
                print(f"Supabase loaded: {key} | scores:{len(score_history)} | history:{len(full_history)}")
                return score_history, full_history, study_plan
            else:
                print(f"No data found in Supabase for: {key}")
                # Cache the empty result too, so we don't re-hit Supabase
                # every rerun for a role the user hasn't used yet.
                cache[key] = {
                    "score_history": [],
                    "full_history": [],
                    "study_plan": ""
                }
                return [], [], ""
    except Exception as e:
        print(f"Supabase load error: {e}")
        return [], [], ""

    return [], [], ""

# Keep async wrappers for compatibility
async def save_full_state(user_uid, role, score_history, full_history, study_plan=""):
    save_full_state_sync(user_uid, role, score_history, full_history, study_plan)

async def load_full_state(user_uid, role):
    return load_full_state_sync(user_uid, role)

async def setup_memory():
    global _memory_setup_done
    if _memory_setup_done:
        return
    try:
        cognee.config.set_llm_config({
            "provider": "groq",
            "model": "llama-3.3-70b-versatile",
            "api_key": GROQ_KEY
        })
        _memory_setup_done = True
    except Exception as e:
        print(f"Memory setup error: {e}")

def _dataset(user_uid, role):
    return f"rr_{user_uid}_{role}".replace(" ", "_").replace("-", "_")[:60]

async def save_answer(user_uid, role, question, answer, feedback, score, display_name=""):
    memory_text = f"""
RecallReady Interview Log
User ID: {user_uid}
Name: {display_name}
Role: {role}
Question: {question}
Answer: {answer}
Score: {score}/10
Feedback: {feedback[:400]}
"""
    try:
        dataset = _dataset(user_uid, role)
        await cognee.add(memory_text, dataset_name=dataset)
        await cognee.cognify(dataset_name=dataset)
    except Exception as e:
        print(f"Cognee answer save error: {e}")

async def get_user_profile(user_uid, role, display_name=""):
    try:
        who = display_name or user_uid
        results = await cognee.search(
            query_text=f"Overall performance summary for {who} in {role} interviews.",
            dataset_name=_dataset(user_uid, role)
        )
        if results:
            r = results[0] if isinstance(results, list) else results
            text = str(r)
            if len(text) > 20:
                return text
        return f"Memory is building for {who}. Answer more questions and try again!"
    except Exception as e:
        return f"Memory is building for {display_name or user_uid}. Answer more questions and try again!"

async def get_weak_topics(user_uid, role, display_name=""):
    try:
        who = display_name or user_uid
        results = await cognee.search(
            query_text=f"Topics where {who} scored below 5 in {role} interview practice",
            dataset_name=_dataset(user_uid, role)
        )
        if results:
            r = results[0] if isinstance(results, list) else results
            return str(r)
        return ""
    except Exception as e:
        return ""

async def get_topic_study_plan(user_uid, role, weak_questions, strong_questions, display_name=""):
    client = Groq(api_key=GROQ_KEY)
    who = display_name or "the candidate"
    weak_text = "\n".join([f"- {q}" for q in weak_questions[:8]]) if weak_questions else "None yet"
    strong_text = "\n".join([f"- {q}" for q in strong_questions[:5]]) if strong_questions else "None yet"

    prompt = f"""
A candidate named {who} is preparing for {role} interviews.

Questions they scored LOW on (below 5/10):
{weak_text}

Questions they scored HIGH on (7+/10):
{strong_text}

Identify the underlying TOPICS (not the literal question text) and create a study plan.
Do NOT repeat the questions. Find the broader concept each question tests.

Respond in EXACTLY this format, no emojis:

CORE TOPICS TO STUDY:
- [Topic name]: [why it matters for {role}]
- [Topic name]: [why it matters for {role}]

TOPICS YOU HAVE MASTERED:
- [Topic name]: keep sharp with occasional review

THIS WEEK'S PRIORITY:
[One specific topic to focus on this week and why]

LEARNING RESOURCES:
- [Topic] Blog: https://geeksforgeeks.org/[relevant-article-slug]
- [Topic] YouTube: https://youtube.com/results?search_query=[topic]+for+beginners
- [Topic] Course: https://freecodecamp.org/learn
- [Topic] Roadmap: https://roadmap.sh/[relevant-path]

SUGGESTED PRACTICE ROUTINE:
[2-3 sentences on how to practice — how many questions per day, which difficulty, when to move on]
"""
    for model in ["llama-3.3-70b-versatile", "llama3-70b-8192", "gemma2-9b-it"]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except:
            continue
    return ""