import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# THESE IN-DEMAND CHAINS ARE RE-ROUTED COMPACTLY
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# 1. Load configuration and environment
load_dotenv()

# --- INJECT COMPLETE HIGH-FIDELITY MOCKUP CSS ---
st.set_page_config(page_title="Research Library - Indigenous Peoples of Canada", page_icon="📚", layout="wide")

# ==============================================================================
# --- ACCESS TOKEN PROTECTION ---
# Place right after st.set_page_config and BEFORE your st.markdown CSS block
# ==============================================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h2 style='color: #f0e8dc; font-family: system-ui, sans-serif;'>Restricted Library Access</h2>", unsafe_allow_html=True)
    password = st.text_input("Enter Access Token to proceed:", type="password")
    
    if st.button("Unlock Dashboard"):
        if password == "MySecretToken2026": 
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid Token. Access Denied.")
    st.stop()  # Prevents loading the rest of the app, saving your API tokens

# --- SIMPLE SECURE GATEWAY ---
def check_password():
    """Returns True if the user had the correct password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    # Show password entry form
    st.markdown("<h2 style='color: #f0e8dc;'>Restricted Library Access</h2>", unsafe_allow_html=True)
    password = st.text_input("Enter Access Token to proceed:", type="password")
    
    if st.button("Unlock Dashboard"):
        # Replace 'MySecretToken2026' with whatever password you want to give them
        if password == "MySecretToken2026": 
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ Invalid Token. Access Denied.")
            
    return False

# Drop everything below inside an if statement, or use an early exit:
if not check_password():
    st.stop() # Stops execution here until authenticated is True

# --- YOUR EXISTING APP CODE STARTS HERE ---
# file_links_map = load_file_mapping() ... etc

# --- GOOGLE DRIVE FILE MAPPER ---
@st.cache_data
def load_file_mapping():
    if os.path.exists("file_mapping.csv"):
        df = pd.read_csv("file_mapping.csv")
        return dict(zip(df['filename'], df['drive_id']))
    return {}

file_links_map = load_file_mapping()

# --- INITIALIZE RAG SERVICES ---
@st.cache_resource
def init_rag():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    index_name = os.getenv("PINECONE_INDEX_NAME")
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.1)
    return vectorstore, llm

vectorstore, llm = init_rag()





# ==============================================================================
# --- YOUR ORIGINAL DESIGN & APP CODE STARTS HERE ---
# st.markdown(""" <style> ... """)
# ==============================================================================

# --- INJECT MASTER STYLING ENGINE WITH SUBHEADER & CONTRAST FIXES ---
st.markdown("""
    <style>
    /* Global Base Canvas Styles */
    .stApp {
        background-color: #1a1410 !important;
        color: #ffffff !important; /* Force all base prose text to bright white */
    }
    
    /* Global Text element overrides for sharp contrast */
    p, span, label, .stMarkdown {
        color: #f5f0e6 !important;
    }
    
    /* ==============================================================================
       SUBHEADER & APP TITLES BRIGHTNESS FIX (FOR STRATEGIC ASSISTANT LINE)
       ============================================================================== */
    h1, h2, h3, h4, h5, h6, [data-testid="stHeaderBlockContainer"] h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* ==============================================================================
       STUBBORN RADIO BUTTON TEXT CONTRAST FIXES
       ============================================================================== */
    div[data-testid="stRadio"] label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    /* Explicitly targets the options text inside the radio selection group */
    div[data-testid="stRadio"] div[role="radiogroup"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar Layout Structure */
    [data-testid="stSidebar"] {
        background-color: #221c16 !important;
        border-right: 0.5px solid #4a3b2e !important;
        padding: 14px 10px !important;
    }
                            
    /* CSS Styles for the Animated System Reply Indicator Box */
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }
    .thinking-box { display: inline-flex; align-items: center; gap: 8px; background: #221c16; border: 0.5px solid #d4a843; border-radius: 8px; padding: 10px 14px; color: #d4a843; font-size: 13px; font-weight: 500; animation: pulse 1.5s infinite ease-in-out; margin-bottom: 15px; }
    .spinner { border: 2px solid rgba(212,168,67,0.2); width: 14px; height: 14px; border-radius: 50%; border-left-color: #c4721f; animation: spin 1s linear infinite; }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    /* Sidebar Branding Header */
    .logo-container {
        display: flex;
        align-items: center;
        gap: 9px;
        margin-bottom: 14px;
        padding-bottom: 14px;
        border-bottom: 0.5px solid #4a3b2e;
    }
    .logo-icon {
        width: 34px; height: 34px; background: #332a20; 
        border: 0.5px solid #d4a843; border-radius: 9px; 
        display: flex; align-items: center; justify-content: center;
        font-size: 16px; color: #d4a843; font-weight: bold;
    }
    .logo-title { font-size: 14px; font-weight: 600; color: #ffffff !important; line-height: 1.2; }
    .logo-sub { font-size: 11px; color: #d4a843 !important; font-weight: 500; }
    
    /* Data Metrics Badge */
    .badge {
        display: flex; align-items: center; gap: 5px; 
        background: rgba(212,168,67,0.15); border: 1px solid #d4a843; 
        color: #ffffff !important; font-size: 11px; font-weight: 600; padding: 6px 12px; border-radius: 20px; margin-bottom: 18px;
        width: fit-content;
    }
    
    /* Segment Group Headings */
    .sec-label { 
        font-size: 11px; font-weight: 700; letter-spacing: 0.12em; 
        text-transform: uppercase; color: #ffffff !important; margin-bottom: 12px; 
    }
    
    /* Mockup Mode Card Component Architecture */
    .mode-card {
        padding: 10px 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        background: transparent;
        border: 0.5px solid transparent;
        transition: all 0.2s ease;
    }
    .mode-card-title { font-size: 13px; font-weight: 600; color: #ffffff !important; }
    .mode-card-desc { font-size: 11px; color: #f5f0e6 !important; line-height: 1.3; margin-top: 2px; }
    
    /* Main Panel Header Pill */
    .mode-pill {
        display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 600;
        color: #ffffff !important; background: #c4721f; 
        border: 0.5px solid #d4a843; padding: 5px 10px; border-radius: 8px; margin-bottom: 12px;
    }
    
    /* Response / Content Containers */
    .user-bubble-style {
        background: rgba(196,114,31,0.2) !important;
        border: 1px solid #c4721f !important;
        color: #ffffff !important;
        border-radius: 10px; padding: 14px; font-size: 14px; line-height: 1.65;
    }
    .asst-bubble-style {
        background: #221c16 !important;
        border: 1px solid #4a3b2e !important;
        color: #ffffff !important;
        border-radius: 10px; padding: 16px; font-size: 14px; line-height: 1.65;
    }
    
    /* AI Response Internal Typographic Overrides */
    .asst-bubble-style h1, .asst-bubble-style h2, .asst-bubble-style h3, 
    .asst-bubble-style h4, .asst-bubble-style h5, .asst-bubble-style h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        margin-top: 12px !important;
        margin-bottom: 8px !important;
    }
    .asst-bubble-style strong, .asst-bubble-style b { 
        color: #ffffff !important; 
        font-weight: 600 !important; 
    }
    .cite { color: #ff9e42 !important; font-size: 12.5px; font-weight: bold; }
    
    /* Rich Metadata Citation Cards */
    .src-card {
        background: #1e1813 !important; border: 1px solid #4a3b2e !important;
        border-radius: 8px; padding: 10px 14px; margin-top: 10px;
    }
    .src-idx { font-size: 11px; font-weight: 700; color: #d4a843; text-transform: uppercase; letter-spacing: 0.08em; }
    .src-title { font-size: 14px; color: #ffffff !important; font-family: Georgia, serif; margin-top: 3px; font-weight: 500; }
    .src-meta { font-size: 11px; color: #f5f0e6 !important; margin-top: 2px; }
    .cloud-link { display: inline-block; margin-top: 8px; font-size: 12px; color: #d4a843 !important; text-decoration: none; font-weight: 600; }
    .cloud-link:hover { text-decoration: underline !important; }
    
    /* Style Cleanups */
    header, footer { visibility: hidden !important; }
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1a1410 !important;
        border: 1px solid #4a3b2e !important;
        color: #ffffff !important;
    }

    /* High Visibility Sidebar Toggle Triggers */
    button[data-testid="stSidebarCollapseAction"] {
        background-color: #d4a843 !important;
        color: #1a1410 !important;
        border: 1px solid #ffffff !important;
        border-radius: 6px !important;
        z-index: 999999 !important;
        opacity: 1 !important;
    }
    button[data-testid="stSidebarCollapseAction"]:hover {
        background-color: #ffffff !important;
    }
    button[data-testid="stSidebarCollapseAction"] svg {
        fill: #1a1410 !important;
        color: #1a1410 !important;
    }

    div[data-testid="collapsedControl"], .st-emotion-cache-16idsys {
        background-color: #d4a843 !important;
        border: 1px solid #ffffff !important;
        border-radius: 0 8px 8px 0 !important;
        z-index: 9999999 !important; 
        left: 0 !important;
        top: 12px !important;
        width: 44px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center;
        justify-content: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5) !important;
    }
    
    div[data-testid="collapsedControl"] svg, .st-emotion-cache-16idsys svg {
        fill: #1a1410 !important;
        color: #1a1410 !important;
        width: 24px !important;
        height: 24px !important;
    }        
    </style>
""", unsafe_allow_html=True)


# --- SIDEBAR: INTERFACE LAYER ---
with st.sidebar:
    st.markdown("""
        <div class="logo-container">
            <div class="logo-icon">📚</div>
            <div>
                <div class="logo-title">Research Library</div>
                <div class="logo-sub">Indigenous Peoples of Canada</div>
            </div>
        </div>
        <div class="badge">✨ 1,247 document chunks indexed</div>
        <div class="sec-label">System Mode</div>
    """, unsafe_allow_html=True)
    
    # Render Interactive Mode Selector Matching Your Mockup Specs
    selected_mode = st.radio(
        label="Select Workspace Mode",
        options=["Research Chat", "Write Report", "Research Paper", "Summarize Sources", "Reference List"],
        index=0,
        label_visibility="collapsed"
    )
    
    # Custom HTML Layout Injection to Render Descriptive Cards Below Selected Options
    st.markdown("<div style='margin-top: -20px;'>", unsafe_allow_html=True)
    modes_metadata = {
        "Research Chat": ("Ask questions, get cited answers", "rgba(196,114,31,0.15)", "#3d3026"),
        "Write Report": ("Structured sections with citations", "transparent", "transparent"),
        "Research Paper": ("Academic synthesis + APA refs", "transparent", "transparent"),
        "Summarize Sources": ("Thematic overview from the library", "transparent", "transparent"),
        "Reference List": ("Generate bibliography", "transparent", "transparent")
    }
    
    for mode, (desc, bg, border) in modes_metadata.items():
        # Highlight active metadata container state dynamically to match current user input selection
        if selected_mode == mode:
            bg, border = "rgba(196,114,31,0.08)", "rgba(196,114,31,0.3)"
        st.markdown(f"""
            <div class="mode-card" style="background: {bg}; border-color: {border};">
                <div class="mode-card-title">{'● ' if selected_mode == mode else ''}{mode}</div>
                <div class="mode-card-desc">{desc}</div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br><div class=\"sec-label\">Settings</div>", unsafe_allow_html=True)
    citation_style = st.selectbox("Citation Standard", ["APA 7th Edition", "MLA", "Chicago"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Reset Chat Thread", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --- CHAT CANVAS LAYOUT ---
st.markdown(f'<div class="mode-pill">✨ {selected_mode} Enabled</div>', unsafe_allow_html=True)
st.subheader("Strategic Research & Writing Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-bubble-style">🧑‍💻 {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="asst-bubble-style">{message["content"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


# --- DYNAMIC SYSTEM PROMPT ROUTING ENGINE ---
# Updates AI generation instructions instantly based on sidebar click
mode_instructions = {
    "Research Chat": "Answer the user's research question conversational but analytically. Use targeted references.",
    "Write Report": "Structure your response as a formal executive report segment with clear headings, bold analytical summaries, and exhaustive background data.",
    "Research Paper": f"Write in a strict peer-reviewed academic style. Focus deeply on epistemologies and ensure full compliance with {citation_style} requirements.",
    "Summarize Sources": "Provide a comprehensive thematic matrix summary grouped by core issues (e.g., policy, rights, environment) identified across the text assets.",
    "Reference List": f"Synthesize a robust, alphabetized reference list bibliography according to {citation_style} standards for the data contexts provided."
}

active_instruction = mode_instructions[selected_mode]

# --- RAG INPUT EXECUTION BAR ---
if prompt := st.chat_input("Ask anything about Indigenous Peoples of Canada research..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-bubble-style">🧑‍💻 {prompt}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # CHANGE 2: Render animated dynamic thinking/searching box container instantly on prompt submission
        message_placeholder.markdown("""
            <div class="thinking-box">
                <div class="spinner"></div>
                <span>Searching text library database & evaluating contexts...</span>
            </div>
        """, unsafe_allow_html=True)
        
        system_prompt = (
            f"You are a Senior Research Analyst working with an advanced archive. {active_instruction} "
            f"Wrap all inline citations clearly in an HTML span tag: <span class='cite'>(Author, Year, p. X)</span>. "
            "Prioritize deep accuracy regarding Indigenous rights, land titles, and treaty relations. "
            "\n\nContext: {context}"
        )
        
        full_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        chain = create_retrieval_chain(
            vectorstore.as_retriever(search_kwargs={"k": 5}), 
            create_stuff_documents_chain(llm, full_prompt)
        )
        
        response = chain.invoke({"input": prompt})
        full_response = response["answer"]
        
        message_placeholder.markdown(f'<div class="asst-bubble-style">🤖 {full_response}</div>', unsafe_allow_html=True)
        
        # --- CLOUD RETRIEVED SOURCE EXPANDER (SANUTIZED LINUX MATCHING ENGINE) ---
        # ==============================================================================
        if "context" in response:
            with st.expander("📚 View Document Sources Retrieved (Click to Download)"):
                displayed_files = set()
                source_idx = 1
                
                # Safe fallback initialization for file_links_map if loaded elsewhere
                # Create a completely case-insensitive version with stripped whitespace keys
                clean_file_links_map = {}
                if 'file_links_map' in locals() or 'file_links_map' in globals():
                    clean_file_links_map = {str(k).strip().lower(): v for k, v in file_links_map.items()}
                
                for doc in response["context"]:
                    source_path = doc.metadata.get('source', 'Unknown')
                    source_name = os.path.basename(source_path)
                    page_num = doc.metadata.get('page', '?')
                    
                    if source_name not in displayed_files:
                        drive_link_html = ""
                        
                        # ------------------------------------------------------------------
                        # CRITICAL FIX: SANITIZE PINECONE OUTPUT STRING
                        # ------------------------------------------------------------------
                        # Removes any hidden Linux/Windows carriage returns and forces lowercase
                        lookup_key = source_name.replace("\r", "").replace("\n", "").strip().lower()
                        
                        if lookup_key in clean_file_links_map:
                            drive_id = clean_file_links_map[lookup_key]
                            gdrive_url = f"https://drive.google.com/uc?export=download&id={drive_id}"
                            drive_link_html = f'<br><a class="cloud-link" href="{gdrive_url}" target="_blank">📥 Download Original Asset from Google Drive</a>'
                        else:
                            # Clear fallback text showing what key it failed to match for visibility
                            drive_link_html = f'<br><span style="color:#d4a843; font-size:11px;">⚠️ Unmapped in Google Drive Register ("{source_name}")</span>'
                        
                        st.markdown(f"""
                            <div class="src-card">
                                <div class="src-idx">Source {source_idx}</div>
                                <div class="src-title">{source_name.replace('.pdf','').replace('.docx','').title()}</div>
                                <div class="src-meta">File: {source_name} · Page Context: {page_num}</div>
                                {drive_link_html}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        displayed_files.add(source_name)
                        source_idx += 1
    st.session_state.messages.append({"role": "assistant", "content": full_response})