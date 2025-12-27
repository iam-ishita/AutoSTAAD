"""
Streamlit Web Interface for STAAD.Pro Node Data Automation
IIT Delhi Research Project - Structural Engineering Automation

This Streamlit app provides a user-friendly interface for:
1. Uploading node data files (CSV or Excel)
2. Validating the data using existing automation logic
3. Generating STAAD.Pro input files
4. Downloading the generated model.std file
"""

import streamlit as st
import pandas as pd
import io
import os
import sys
from contextlib import redirect_stdout

# Import functions from the existing automation script
from node_to_staad import read_node_data, validate_node_data, generate_staad_file


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AutoSTAAD - Node Data Converter",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS STYLING - Dark Theme & Professional UI
# ============================================================================
def apply_custom_css():
    """
    Apply custom CSS for dark theme and professional UI styling.
    This function injects CSS to create a modern, research-demo appearance.
    """
    st.markdown("""
    <style>
    /* ========================================================================
       DARK THEME BASE STYLES
       ======================================================================== */
    
    /* Main background - dark grey/black */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        color: #e0e0e0;
    }
    
    /* Sidebar background */
    [data-testid="stSidebar"] {
        background-color: #0f0f0f;
        border-right: 1px solid #2a2a2a;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* ========================================================================
       TYPOGRAPHY - Enhanced Hierarchy
       ======================================================================== */
    
    /* Main title styling */
    h1 {
        color: #00d4ff !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
        letter-spacing: -0.5px;
    }
    
    /* Section headers */
    h2 {
        color: #4dd0e1 !important;
        font-weight: 600 !important;
        font-size: 1.75rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #00bcd4;
    }
    
    /* Subsection headers */
    h3 {
        color: #80deea !important;
        font-weight: 500 !important;
        font-size: 1.4rem !important;
        margin-top: 1.5rem !important;
    }
    
    /* Body text */
    p, .stMarkdown {
        color: #d0d0d0 !important;
        line-height: 1.7;
    }
    
    /* ========================================================================
       SECTION CARDS - Professional Container Styling
       ======================================================================== */
    
    /* Custom card container */
    .section-card {
        background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%);
        border: 1px solid #3a3a3a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .section-card:hover {
        border-color: #00bcd4;
        box-shadow: 0 6px 12px rgba(0, 188, 212, 0.2);
    }
    
    /* ========================================================================
       BUTTONS - Enhanced Styling
       ======================================================================== */
    
    /* Primary buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00bcd4 0%, #0097a7 100%);
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 188, 212, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00acc1 0%, #00838f 100%);
        box-shadow: 0 4px 8px rgba(0, 188, 212, 0.4);
        transform: translateY(-1px);
    }
    
    /* Download button special styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
        box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3);
    }
    
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #43a047 0%, #2e7d32 100%);
        box-shadow: 0 4px 8px rgba(76, 175, 80, 0.4);
    }
    
    /* ========================================================================
       ALERTS & MESSAGES - High Contrast
       ======================================================================== */
    
    /* Success messages */
    [data-baseweb="notification"] {
        background-color: #1a3a1a !important;
        border-left: 4px solid #4caf50 !important;
        color: #a5d6a7 !important;
    }
    
    /* Error messages */
    .stAlert[data-baseweb="alert"] {
        background-color: #3a1a1a !important;
        border-left: 4px solid #f44336 !important;
        color: #ffcdd2 !important;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #1a2a3a !important;
        border-left: 4px solid #2196f3 !important;
        color: #90caf9 !important;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #3a2a1a !important;
        border-left: 4px solid #ff9800 !important;
        color: #ffe0b2 !important;
    }
    
    /* ========================================================================
       DATA TABLES - Dark Theme Styling
       ======================================================================== */
    
    /* DataFrame styling */
    .dataframe {
        background-color: #1a1a1a !important;
        color: #e0e0e0 !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 8px;
    }
    
    .dataframe thead {
        background-color: #2a2a2a !important;
        color: #00d4ff !important;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #252525 !important;
    }
    
    .dataframe tbody tr:hover {
        background-color: #2a3a3a !important;
    }
    
    /* ========================================================================
       FILE UPLOADER - Enhanced Styling
       ======================================================================== */
    
    .uploadedFile {
        background-color: #1e1e1e !important;
        border: 2px dashed #00bcd4 !important;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* ========================================================================
       EXPANDER - Custom Styling
       ======================================================================== */
    
    .streamlit-expanderHeader {
        background-color: #1e1e1e !important;
        color: #00d4ff !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 6px;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background-color: #1a1a1a !important;
        color: #d0d0d0 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 0 0 6px 6px;
    }
    
    /* ========================================================================
       CODE BLOCKS & TEXT AREAS
       ======================================================================== */
    
    code {
        background-color: #0f0f0f !important;
        color: #00ff88 !important;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        border: 1px solid #2a2a2a;
    }
    
    pre {
        background-color: #0f0f0f !important;
        color: #d0d0d0 !important;
        border: 1px solid #3a3a3a !important;
        border-radius: 6px;
        padding: 1rem;
    }
    
    /* ========================================================================
       DIVIDERS & SEPARATORS
       ======================================================================== */
    
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00bcd4, transparent);
        margin: 2rem 0;
    }
    
    /* ========================================================================
       SCROLLBAR STYLING (Webkit browsers)
       ======================================================================== */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #3a3a3a;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00bcd4;
    }
    
    /* ========================================================================
       CAPTION & HELPER TEXT
       ======================================================================== */
    
    .stCaption {
        color: #888 !important;
        font-style: italic;
    }
    
    /* ========================================================================
       SPINNER - Custom Color
       ======================================================================== */
    
    .stSpinner > div {
        border-color: #00bcd4 transparent transparent transparent !important;
    }
    
    </style>
    """, unsafe_allow_html=True)


# Apply custom CSS when the app loads
apply_custom_css()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def capture_validation_output(df):
    """
    Capture the console output from validate_node_data function.
    
    Since the original validation function prints to console, we capture
    that output and return it as a string for display in Streamlit.
    
    Args:
        df: DataFrame containing node data
    
    Returns:
        tuple: (validation_passed: bool, output_text: str)
    """
    # Create a StringIO object to capture stdout
    output_buffer = io.StringIO()
    
    # Redirect stdout to our buffer
    with redirect_stdout(output_buffer):
        validation_passed = validate_node_data(df)
    
    # Get the captured output
    output_text = output_buffer.getvalue()
    
    return validation_passed, output_text


def save_uploaded_file(uploaded_file):
    """
    Save uploaded file to a temporary location.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
    
    Returns:
        str: Path to the saved temporary file
    """
    # Create a temporary file path
    temp_file_path = f"temp_{uploaded_file.name}"
    
    # Write the uploaded file content to disk
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return temp_file_path


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """
    Main Streamlit application function.
    """
    
    # ========================================================================
    # HEADER SECTION - Project Overview
    # ========================================================================
    
    # Main title with enhanced styling
    st.markdown("<h1 style='text-align: center; margin-bottom: 0.5rem;'>🏗️ AutoSTAAD</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 1.2rem; margin-bottom: 2rem;'>Node Data Converter for STAAD.Pro</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 3rem;'>IIT Delhi Research Project - Structural Engineering Automation</p>", unsafe_allow_html=True)
    
    # Project overview in a styled container
    with st.container():
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%); 
                    border: 1px solid #3a3a3a; 
                    border-radius: 12px; 
                    padding: 2rem; 
                    margin: 1.5rem 0;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);'>
            <h3 style='color: #4dd0e1; margin-top: 0;'>📋 Project Overview</h3>
            <p style='color: #d0d0d0; line-height: 1.8; margin-bottom: 1.5rem;'>
                This web application automates the conversion of node coordinate data into 
                <strong style='color: #00d4ff;'>STAAD.Pro</strong> input files for structural analysis.
            </p>
            <h4 style='color: #80deea; margin-top: 1.5rem; margin-bottom: 1rem;'>Key Features:</h4>
            <ul style='color: #d0d0d0; line-height: 2;'>
                <li>✅ Upload CSV or Excel files containing node data</li>
                <li>✅ Automatic validation of node coordinates</li>
                <li>✅ Generation of STAAD.Pro compatible <code style='color: #00ff88;'>.std</code> files</li>
                <li>✅ User-friendly error reporting</li>
            </ul>
            <p style='color: #888; margin-top: 1.5rem; margin-bottom: 0;'>
                <strong>Required Columns:</strong> <code style='color: #00ff88;'>node_id</code>, 
                <code style='color: #00ff88;'>x</code>, <code style='color: #00ff88;'>y</code>, 
                <code style='color: #00ff88;'>z</code>
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 3rem 0;'>", unsafe_allow_html=True)
    
    
    # ========================================================================
    # FILE UPLOAD SECTION
    # ========================================================================
    
    # Section header with step indicator
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%); 
                border-left: 4px solid #00bcd4; 
                border-radius: 8px; 
                padding: 1rem 1.5rem; 
                margin: 2rem 0 1.5rem 0;'>
        <h2 style='color: #4dd0e1; margin: 0;'>📤 Step 1: Upload Node Data File</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader widget in a container
    with st.container():
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a file containing node data with columns: node_id, x, y, z"
        )
    
    # Initialize session state variables
    if 'validation_passed' not in st.session_state:
        st.session_state.validation_passed = False
    if 'df_loaded' not in st.session_state:
        st.session_state.df_loaded = None
    if 'staad_generated' not in st.session_state:
        st.session_state.staad_generated = False
    
    
    # ========================================================================
    # FILE PROCESSING SECTION
    # ========================================================================
    if uploaded_file is not None:
        # Display file information in styled containers
        with st.container():
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a3a1a 0%, #1e4a1e 100%); 
                        border-left: 4px solid #4caf50; 
                        border-radius: 8px; 
                        padding: 1rem 1.5rem; 
                        margin: 1rem 0;'>
                <p style='color: #a5d6a7; margin: 0; font-size: 1.1rem;'>
                    ✅ <strong>File uploaded:</strong> <code style='color: #00ff88;'>{uploaded_file.name}</code>
                </p>
                <p style='color: #81c784; margin: 0.5rem 0 0 0;'>
                    📊 File size: <strong>{uploaded_file.size:,}</strong> bytes
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Process the uploaded file
        with st.spinner("Reading file..."):
            # Save uploaded file temporarily
            temp_file_path = save_uploaded_file(uploaded_file)
            
            # Read the file using existing function
            df = read_node_data(temp_file_path)
            
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
        
        # Check if file reading was successful
        if df is None:
            st.error("❌ **Error:** Failed to read the file. Please check the file format and try again.")
            st.stop()
        
        # Store DataFrame in session state
        st.session_state.df_loaded = df
        
        # Display preview of the data in a styled container
        st.markdown("""
        <div style='margin-top: 2rem;'>
            <h3 style='color: #80deea; margin-bottom: 1rem;'>📋 Data Preview</h3>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.dataframe(df.head(10), use_container_width=True)
            st.caption(f"📊 Total rows: **{len(df)}**")
        
        # Check for required columns
        required_columns = ['node_id', 'x', 'y', 'z']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"❌ **Missing Required Columns:** {', '.join(missing_columns)}")
            st.info(f"Available columns in your file: {', '.join(df.columns.tolist())}")
            st.stop()
        
        
        # ====================================================================
        # VALIDATION SECTION
        # ====================================================================
        st.markdown("<hr style='margin: 3rem 0;'>", unsafe_allow_html=True)
        
        # Section header with step indicator
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%); 
                    border-left: 4px solid #00bcd4; 
                    border-radius: 8px; 
                    padding: 1rem 1.5rem; 
                    margin: 2rem 0 1.5rem 0;'>
            <h2 style='color: #4dd0e1; margin: 0;'>🔍 Step 2: Data Validation</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Validation button in a container
        with st.container():
            if st.button("🔍 Validate Data", type="primary", use_container_width=True):
                with st.spinner("Validating data..."):
                    # Capture validation output
                    validation_passed, validation_output = capture_validation_output(df)
                    
                    # Store validation result
                    st.session_state.validation_passed = validation_passed
                    
                    # Display validation results
                    st.markdown("""
                    <div style='margin-top: 2rem;'>
                        <h3 style='color: #80deea; margin-bottom: 1rem;'>Validation Results</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create expandable section for detailed output
                    with st.expander("📄 View Detailed Validation Report", expanded=True):
                        # Format the output for better readability
                        st.markdown(f"<pre style='background-color: #0f0f0f; color: #d0d0d0; padding: 1rem; border-radius: 6px; overflow-x: auto;'>{validation_output}</pre>", unsafe_allow_html=True)
                    
                    # Show summary in styled containers
                    if validation_passed:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #1a3a1a 0%, #1e4a1e 100%); 
                                    border-left: 4px solid #4caf50; 
                                    border-radius: 8px; 
                                    padding: 1rem 1.5rem; 
                                    margin: 1rem 0;'>
                            <p style='color: #a5d6a7; margin: 0; font-size: 1.1rem;'>
                                ✅ <strong>Validation Passed!</strong> All checks successful. You can proceed to generate the STAAD file.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.session_state.staad_generated = False  # Reset generation status
                    else:
                        st.markdown("""
                        <div style='background: linear-gradient(135deg, #3a1a1a 0%, #4a1e1e 100%); 
                                    border-left: 4px solid #f44336; 
                                    border-radius: 8px; 
                                    padding: 1rem 1.5rem; 
                                    margin: 1rem 0;'>
                            <p style='color: #ffcdd2; margin: 0; font-size: 1.1rem;'>
                                ❌ <strong>Validation Failed!</strong> Please fix the errors in your data file and upload again.
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.info("💡 **Tip:** Check the detailed validation report above to see what needs to be fixed.")
                        st.session_state.staad_generated = False
        
        # Show validation status if already validated
        if st.session_state.validation_passed:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a3a1a 0%, #1e4a1e 100%); 
                        border-left: 4px solid #4caf50; 
                        border-radius: 8px; 
                        padding: 1rem 1.5rem; 
                        margin: 1rem 0;'>
                <p style='color: #a5d6a7; margin: 0;'>✅ Validation completed successfully!</p>
            </div>
            """, unsafe_allow_html=True)
        
        
        # ====================================================================
        # STAAD FILE GENERATION SECTION
        # ====================================================================
        st.markdown("<hr style='margin: 3rem 0;'>", unsafe_allow_html=True)
        
        # Section header with step indicator
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%); 
                    border-left: 4px solid #00bcd4; 
                    border-radius: 8px; 
                    padding: 1rem 1.5rem; 
                    margin: 2rem 0 1.5rem 0;'>
            <h2 style='color: #4dd0e1; margin: 0;'>⚙️ Step 3: Generate STAAD File</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Only allow generation if validation passed
        if st.session_state.validation_passed:
            with st.container():
                if st.button("⚙️ Generate STAAD File", type="primary", use_container_width=True):
                    with st.spinner("Generating STAAD file..."):
                        # Generate the STAAD file
                        success = generate_staad_file(df, "model.std")
                        
                        if success:
                            st.session_state.staad_generated = True
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #1a3a1a 0%, #1e4a1e 100%); 
                                        border-left: 4px solid #4caf50; 
                                        border-radius: 8px; 
                                        padding: 1rem 1.5rem; 
                                        margin: 1rem 0;'>
                                <p style='color: #a5d6a7; margin: 0; font-size: 1.1rem;'>
                                    ✅ <strong>STAAD file generated successfully!</strong>
                                </p>
                                <p style='color: #81c784; margin: 0.5rem 0 0 0;'>
                                    📁 File: <code style='color: #00ff88;'>model.std</code> | Nodes: <strong>{len(df)}</strong>
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style='background: linear-gradient(135deg, #3a1a1a 0%, #4a1e1e 100%); 
                                        border-left: 4px solid #f44336; 
                                        border-radius: 8px; 
                                        padding: 1rem 1.5rem; 
                                        margin: 1rem 0;'>
                                <p style='color: #ffcdd2; margin: 0; font-size: 1.1rem;'>
                                    ❌ <strong>Error:</strong> Failed to generate STAAD file. Please try again.
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.staad_generated = False
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #3a2a1a 0%, #4a3a1e 100%); 
                        border-left: 4px solid #ff9800; 
                        border-radius: 8px; 
                        padding: 1rem 1.5rem; 
                        margin: 1rem 0;'>
                <p style='color: #ffe0b2; margin: 0;'>⚠️ Please validate your data first before generating the STAAD file.</p>
            </div>
            """, unsafe_allow_html=True)
        
        
        # ====================================================================
        # DOWNLOAD SECTION
        # ====================================================================
        st.markdown("<hr style='margin: 3rem 0;'>", unsafe_allow_html=True)
        
        # Section header with step indicator
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1e1e1e 0%, #252525 100%); 
                    border-left: 4px solid #00bcd4; 
                    border-radius: 8px; 
                    padding: 1rem 1.5rem; 
                    margin: 2rem 0 1.5rem 0;'>
            <h2 style='color: #4dd0e1; margin: 0;'>📥 Step 4: Download Generated File</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if STAAD file was generated
        if st.session_state.staad_generated:
            # Read the generated file
            try:
                with open("model.std", "rb") as f:
                    staad_file = f.read()
                
                # Provide download button in a styled container
                with st.container():
                    st.download_button(
                        label="📥 Download model.std",
                        data=staad_file,
                        file_name="model.std",
                        mime="text/plain",
                        type="primary",
                        use_container_width=True
                    )
                    
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #1a3a1a 0%, #1e4a1e 100%); 
                                border-left: 4px solid #4caf50; 
                                border-radius: 8px; 
                                padding: 1rem 1.5rem; 
                                margin: 1rem 0;'>
                        <p style='color: #a5d6a7; margin: 0;'>✅ Ready to download! Click the button above to save your STAAD file.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
            except FileNotFoundError:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #3a1a1a 0%, #4a1e1e 100%); 
                            border-left: 4px solid #f44336; 
                            border-radius: 8px; 
                            padding: 1rem 1.5rem; 
                            margin: 1rem 0;'>
                    <p style='color: #ffcdd2; margin: 0; font-size: 1.1rem;'>
                        ❌ <strong>Error:</strong> Generated file not found. Please regenerate the file.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.staad_generated = False
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #1a2a3a 0%, #1e3a4a 100%); 
                        border-left: 4px solid #2196f3; 
                        border-radius: 8px; 
                        padding: 1rem 1.5rem; 
                        margin: 1rem 0;'>
                <p style='color: #90caf9; margin: 0;'>💡 Generate the STAAD file first to enable download.</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Show instructions when no file is uploaded
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a2a3a 0%, #1e3a4a 100%); 
                    border-left: 4px solid #2196f3; 
                    border-radius: 8px; 
                    padding: 1.5rem; 
                    margin: 2rem 0;'>
            <p style='color: #90caf9; margin: 0; font-size: 1.1rem; text-align: center;'>
                👆 <strong>Please upload a CSV or Excel file to get started.</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Example data format in a styled container
        with st.expander("📝 Example Data Format", expanded=False):
            st.markdown("""
            <div style='padding: 1rem 0;'>
                <p style='color: #d0d0d0; margin-bottom: 1rem;'>
                    Your file should contain the following columns:
                </p>
                <table style='width: 100%; border-collapse: collapse; margin: 1rem 0;'>
                    <thead>
                        <tr style='background-color: #2a2a2a;'>
                            <th style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #00d4ff;'>node_id</th>
                            <th style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #00d4ff;'>x</th>
                            <th style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #00d4ff;'>y</th>
                            <th style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #00d4ff;'>z</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr style='background-color: #1a1a1a;'>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>1</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                        </tr>
                        <tr style='background-color: #252525;'>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>2</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>5.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                        </tr>
                        <tr style='background-color: #1a1a1a;'>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>3</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>5.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>3.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                        </tr>
                        <tr style='background-color: #252525;'>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>4</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>3.0</td>
                            <td style='padding: 0.75rem; border: 1px solid #3a3a3a; color: #d0d0d0; text-align: center;'>0.0</td>
                        </tr>
                    </tbody>
                </table>
                <p style='color: #888; margin-top: 1rem; margin-bottom: 0;'>
                    <strong>Note:</strong> Column names must be exactly: 
                    <code style='color: #00ff88;'>node_id</code>, 
                    <code style='color: #00ff88;'>x</code>, 
                    <code style='color: #00ff88;'>y</code>, 
                    <code style='color: #00ff88;'>z</code>
                </p>
            </div>
            """, unsafe_allow_html=True)


# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    main()

