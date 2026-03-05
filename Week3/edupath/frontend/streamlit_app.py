import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# API Base URL
API_URL = "http://localhost:5000/api"

# Page config
st.set_page_config(
    page_title="EduPath - Your AI Learning Trainer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .streak-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None

# ═══════════════════════════════════════════════════════════════
# SIDEBAR - User Selection
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("🎓 EduPath")
    st.markdown("---")
    
    # User selection/creation
    if st.session_state.user_id is None:
        st.subheader("Welcome!")
        
        with st.expander("Create New Account", expanded=True):
            with st.form("create_user"):
                username = st.text_input("Username")
                email = st.text_input("Email")
                full_name = st.text_input("Full Name")
                learning_goal = st.text_input("What do you want to learn?")
                current_level = st.selectbox("Current Level", ["Beginner", "Intermediate", "Advanced"])
                
                if st.form_submit_button("Create Account"):
                    response = requests.post(f"{API_URL}/user/create", json={
                        "username": username,
                        "email": email,
                        "full_name": full_name,
                        "learning_goal": learning_goal,
                        "current_level": current_level
                    })
                    
                    if response.status_code == 201:
                        data = response.json()
                        st.session_state.user_id = data['user_id']
                        st.session_state.user_name = full_name
                        st.success("Account created! Welcome to EduPath!")
                        st.rerun()
                    else:
                        st.error("Error creating account")
        
        st.markdown("---")
        st.markdown("**Quick Login (Demo)**")
        demo_user_id = st.number_input("Enter User ID", min_value=1, value=1)
        if st.button("Login"):
            st.session_state.user_id = demo_user_id
            st.rerun()
    
    else:
        # User is logged in
        try:
            user_response = requests.get(f"{API_URL}/user/{st.session_state.user_id}")
            if user_response.status_code == 200:
                user_data = user_response.json()
                st.session_state.user_name = user_data['full_name']
                
                st.markdown(f"### Hello, {user_data['full_name']}! 👋")
                st.markdown(f"**Goal:** {user_data['learning_goal']}")
                
                # Streak display
                st.markdown("---")
                st.markdown("### 🔥 Your Streak")
                st.markdown(f"""
                <div class="streak-box">
                    <h1>{user_data['stats']['current_streak']}</h1>
                    <p>Day Streak</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("---")
                if st.button("Logout"):
                    st.session_state.user_id = None
                    st.session_state.user_name = None
                    st.rerun()
        except:
            st.error("Error loading user data")

# ═══════════════════════════════════════════════════════════════
# MAIN CONTENT
# ═══════════════════════════════════════════════════════════════

if st.session_state.user_id is None:
    st.markdown('<h1 class="main-header">🎓 Welcome to EduPath</h1>', unsafe_allow_html=True)
    st.markdown("### Your AI-Powered Personal Learning Trainer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📅 Daily Check-ins")
        st.write("Get personalized morning motivation and evening reflections")
    
    with col2:
        st.markdown("#### 📊 Progress Tracking")
        st.write("Track your learning journey with detailed analytics")
    
    with col3:
        st.markdown("#### 🤖 AI Coach")
        st.write("Get adaptive recommendations and support when you struggle")
    
    st.markdown("---")
    st.info("👈 Create an account or login in the sidebar to get started!")

else:
    # User is logged in - show main dashboard
    st.markdown(f'<h1 class="main-header">Welcome back, {st.session_state.user_name}!</h1>', unsafe_allow_html=True)
    
    # Get dashboard data
    try:
        dashboard = requests.get(f"{API_URL}/dashboard/{st.session_state.user_id}").json()
        
        # Today's status
        st.markdown("### 📅 Today")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Session Today", "✅" if dashboard['today']['session_completed'] else "❌")
        
        with col2:
            st.metric("Current Streak", f"{dashboard['streak']['current']} days")
        
        with col3:
            st.metric("This Week", f"{dashboard['this_week']['sessions']} sessions")
        
        with col4:
            st.metric("Mastery", f"{dashboard['knowledge']['mastery_percentage']}%")
        
        st.markdown("---")
        
        # Main tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📅 Daily Check-in", "📊 Dashboard", "💬 AI Coach", "📚 Learning Path"])
        
        with tab1:
            st.markdown("### Morning Check-in")
            if st.button("Get Today's Motivation"):
                with st.spinner("Getting your personalized check-in..."):
                    checkin = requests.get(f"{API_URL}/checkin/morning/{st.session_state.user_id}").json()
                    
                    st.success(checkin.get('greeting', ''))
                    st.info(checkin.get('motivation', ''))
                    st.write("**Today's Plan:**")
                    st.write(checkin.get('today_plan', ''))
                    
                    if 'suggested_topics' in checkin:
                        st.write("**Suggested Topics:**")
                        for topic in checkin['suggested_topics']:
                            st.write(f"- {topic}")
        
        with tab2:
            st.markdown("### Your Progress")
            
            # Recent sessions
            if dashboard['recent_sessions']:
                df = pd.DataFrame(dashboard['recent_sessions'])
                st.dataframe(df, use_container_width=True)
        
        with tab3:
            st.markdown("### Chat with Your AI Coach")
            
            user_message = st.text_area("Ask your coach anything...")
            if st.button("Send"):
                if user_message:
                    with st.spinner("Coach is thinking..."):
                        response = requests.post(f"{API_URL}/coach/chat", json={
                            "user_id": st.session_state.user_id,
                            "message": user_message,
                            "conversation_history": []
                        }).json()
                        
                        st.markdown("**Coach:**")
                        st.write(response['response'])
        
        with tab4:
            st.markdown("### Your Learning Path")
            
            knowledge = requests.get(f"{API_URL}/knowledge/state/{st.session_state.user_id}").json()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Mastered", len(knowledge.get('mastered_concepts', [])))
            
            with col2:
                st.metric("In Progress", len(knowledge.get('in_progress_concepts', [])))
            
            with col3:
                st.metric("Ready to Learn", len(knowledge.get('ready_to_learn', [])))
    
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
        st.info("Make sure the Flask API is running at http://localhost:5000")