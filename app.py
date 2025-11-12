"""
Dumroo.ai Admin Panel - AI-Powered Data Query Assistant

Main Streamlit application for natural language queries on student data
with role-based access control.
"""
import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from utils import get_filtered_data, validate_user_role, get_available_classes, get_available_regions
from query_agent import create_query_agent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dumroo.ai Query Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .role-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .query-result {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
    }
    .error-box {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = None
    if 'filtered_data' not in st.session_state:
        st.session_state.filtered_data = None
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None


def setup_sidebar():
    """Set up the sidebar for user role configuration."""
    st.sidebar.title("👤 Admin Configuration")
    
    # Get available options from data
    try:
        available_classes = get_available_classes()
        available_regions = get_available_regions()
    except Exception as e:
        st.sidebar.error(f"Error loading data options: {str(e)}")
        return None
    
    # User role input
    st.sidebar.subheader("Configure Your Role")
    
    username = st.sidebar.text_input(
        "Username",
        value="Roshni_Admin",
        help="Enter your admin username"
    )
    
    assigned_class = st.sidebar.selectbox(
        "Assigned Class",
        options=available_classes,
        help="Select the class you have access to"
    )
    
    region = st.sidebar.selectbox(
        "Region",
        options=available_regions,
        help="Select the region you have access to"
    )
    
    # Create user role dictionary
    user_role = {
        "username": username,
        "assigned_class": int(assigned_class),
        "region": region
    }
    
    # Validate user role
    is_valid, error_msg = validate_user_role(user_role)
    
    if not is_valid:
        st.sidebar.error(f"Invalid role: {error_msg}")
        return None
    
    # Display role summary
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 Your Access")
    st.sidebar.info(f"""
    **Username:** {username}  
    **Class:** {assigned_class}  
    **Region:** {region}
    """)
    
    return user_role


def load_and_filter_data(user_role):
    """Load and filter data based on user role."""
    try:
        filtered_df = get_filtered_data(user_role)
        return filtered_df, None
    except Exception as e:
        return None, str(e)


def display_data_summary(df):
    """Display summary statistics of the filtered data."""
    st.subheader("📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", len(df))
    
    with col2:
        homework_submitted = len(df[df['homework_submitted'] == 'Yes'])
        st.metric("Homework Submitted", homework_submitted)
    
    with col3:
        homework_not_submitted = len(df[df['homework_submitted'] == 'No'])
        st.metric("Homework Not Submitted", homework_not_submitted)
    
    with col4:
        avg_score = round(df['quiz_score'].mean(), 2)
        st.metric("Avg Quiz Score", f"{avg_score}%")
    
    # Show data preview in expander
    with st.expander("📋 View Data Preview"):
        st.dataframe(df, use_container_width=True)


def process_query(agent, query):
    """Process a natural language query using the agent."""
    if not query or not query.strip():
        return None, "Please enter a query"
    
    with st.spinner("🤔 Processing your query..."):
        result = agent.query(query)
    
    if result['success']:
        return result['result'], None
    else:
        return None, result.get('error', 'Unknown error occurred')


def display_example_queries():
    """Display example queries in the sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💡 Example Queries")
    
    examples = [
        "Show students who haven't submitted homework yet",
        "List all students with quiz scores above 85",
        "What is the average quiz score?",
        "Show me the top 3 students by quiz score",
        "How many students submitted homework?",
        "List students sorted by date",
        "Show students with quiz scores below 75"
    ]
    
    for example in examples:
        if st.sidebar.button(example, key=f"example_{example[:20]}", use_container_width=True):
            st.session_state.example_query = example


def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<div class="main-header">🎓 Dumroo.ai Query Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask questions about student data in natural language</div>', unsafe_allow_html=True)
    
    # Check for Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    
    if not gemini_api_key:
        st.error("⚠️ Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
        st.info("Create a `.env` file in the project root and add: `GEMINI_API_KEY=your-api-key-here`")
        st.stop()
    
    # Setup sidebar and get user role
    user_role = setup_sidebar()
    
    if user_role is None:
        st.warning("Please configure your admin role in the sidebar to continue.")
        st.stop()
    
    # Load and filter data
    filtered_df, error = load_and_filter_data(user_role)
    
    if error:
        st.error(f"Error loading data: {error}")
        st.stop()
    
    if len(filtered_df) == 0:
        st.warning("No data available for your role permissions.")
        st.stop()
    
    # Store filtered data in session state
    st.session_state.filtered_data = filtered_df
    
    # Initialize or update agent if role changed
    if (st.session_state.current_agent is None or 
        st.session_state.user_role != user_role):
        try:
            st.session_state.current_agent = create_query_agent(
                gemini_api_key,
                filtered_df,
                model="gemini-2.0-flash"  # Using gemini-2.0-flash (free tier: 15 RPM, 1M TPM)
            )
            st.session_state.user_role = user_role
        except Exception as e:
            st.error(f"Error initializing query agent: {str(e)}")
            st.stop()
    
    # Display data summary
    display_data_summary(filtered_df)
    
    # Display example queries
    display_example_queries()
    
    st.markdown("---")
    
    # Query input section
    st.subheader("🔍 Ask a Question")
    
    # Check if an example was clicked
    default_query = ""
    if 'example_query' in st.session_state:
        default_query = st.session_state.example_query
        del st.session_state.example_query
    
    query = st.text_input(
        "Enter your question in natural language:",
        value=default_query,
        placeholder="e.g., Show students who haven't submitted homework yet",
        help="Ask questions about the student data in plain English"
    )
    
    col1, col2 = st.columns([1, 5])
    
    with col1:
        submit_button = st.button("🚀 Submit Query", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear History", use_container_width=True)
    
    if clear_button:
        st.session_state.query_history = []
        st.rerun()
    
    # Process query
    if submit_button and query:
        result, error = process_query(st.session_state.current_agent, query)
        
        if error:
            st.markdown('<div class="error-box">', unsafe_allow_html=True)
            st.error(f"❌ Error: {error}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Add to history
            st.session_state.query_history.append({
                "query": query,
                "result": result
            })
            
            # Display result
            st.markdown('<div class="query-result">', unsafe_allow_html=True)
            st.success("✅ Query processed successfully!")
            st.markdown("**Result:**")
            st.write(result)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Display query history
    if st.session_state.query_history:
        st.markdown("---")
        st.subheader("📜 Query History")
        
        for idx, item in enumerate(reversed(st.session_state.query_history[-5:])):
            with st.expander(f"Query {len(st.session_state.query_history) - idx}: {item['query']}"):
                st.markdown("**Result:**")
                st.write(item['result'])
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.9rem;'>"
        "Powered by LangChain & Google Gemini | Dumroo.ai © 2025"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
