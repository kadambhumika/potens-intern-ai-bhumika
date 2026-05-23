import streamlit as st
import json
import pandas as pd
import sys
import os
import time

# =====================================================================
# STREAMLIT PAGE CONFIGURATION & PREMIUM STYLING
# =====================================================================
# st.set_page_config MUST be the very first Streamlit command in the script!
# We set layout="wide" to give the operations center dashboard a spacious, professional feel.
st.set_page_config(
    page_title="Sentinel AI - Enterprise Operations Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS injection to create a dark modern "Operations Center" aesthetic.
# We override default margins, customize font sizes, style card components, 
# and add neon cyber-blue and dark slate styling tokens.
st.markdown("""
<style>
    /* Main background and global typography settings */
    .reportview-container {
        background-color: #0f172a;
    }
    
    /* Elegant Title Glow effect */
    h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        color: #f8fafc !important;
        text-shadow: 0px 0px 12px rgba(56, 189, 248, 0.4);
    }
    
    /* Glassmorphic metric and card boundaries */
    div[data-testid="metric-container"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        padding: 15px 20px !important;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1) !important;
    }
    
    /* Make metric labels cleaner */
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.9rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Make metric values stand out in neon blue */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Enhance Streamlit text input box styling */
    .stTextArea textarea {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        font-family: 'Courier New', Courier, monospace;
    }
    
    .stTextArea textarea:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 1px #38bdf8 !important;
    }
    
    /* Premium Hover states for button inputs */
    div.stButton > button {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 1px solid #0369a1 !important;
        font-weight: 700 !important;
        width: 100%;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.3s ease-in-out !important;
    }
    
    div.stButton > button:hover {
        background-color: #38bdf8 !important;
        border-color: #0ea5e9 !important;
        color: #0f172a !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================================
# AGENT MODULE INTEGRATION & SESSION STATE INITIALIZATION
# =====================================================================
# Attempt to import our triage logic.
# Graceful error screens are displayed if the modules fail to resolve.
try:
    from agent import triage_incident
except ImportError as err:
    st.error("### 🚨 Critical System Error: Failed to import Sentinel AI Agent components!")
    st.markdown(f"**Details:** `{err}`")
    st.info("Ensure both `agent.py` and `memory.py` exist in the project directory.")
    st.stop()

# Streamlit Session State holds variables persistent across UI updates.
# We initialize state values for user input and our active execution request triggers.
if "incident_input_widget" not in st.session_state:
    st.session_state.incident_input_widget = ""
if "run_triage_trigger" not in st.session_state:
    st.session_state.run_triage_trigger = False

# Callback handler executed when one of the three example buttons are clicked.
# It populates the session state text variable and flags the dashboard to run automatically.
def load_and_triage_scenario(scenario_text):
    st.session_state.incident_input_widget = scenario_text
    st.session_state.run_triage_trigger = True


# =====================================================================
# SIDEBAR CONTROL CENTER PANEL
# =====================================================================
# Sidebars display structural configurations, system status, and secondary documentation.
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color: #38bdf8;'>🛡️ Operations Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.85rem;'>Sentinel AI Incident Intelligence • v1.0.0</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. System Architecture Diagram and Overview
    st.markdown("### ⚙️ System Architecture")
    st.markdown(
        "1. **Streamlit UI**: Receives incoming alert reports.\n"
        "2. **FAISS Vector Storage**: Queries historical incident database for semantic similarities.\n"
        "3. **Groq Reasoning Agent**: Injects semantic matches as context; processes via `llama3-70b-8192`.\n"
        "4. **Telemetry & Safety**: Enforces structured outputs and safety thresholds locally."
    )
    st.markdown("---")
    
    # 2. Supported Categories Legend
    st.markdown("### 🏷️ Supported Classifications")
    st.markdown(
        "- **Security**: Intrusion alerts, MFA/credentials.\n"
        "- **Billing**: Payment deduplication, subscription errors.\n"
        "- **Technical Issue**: Downtime, crash loops, memory leaks.\n"
        "- **Account Access**: Locked accounts, password resets.\n"
        "- **Feature Request**: Aesthetics, roadmap requests."
    )
    st.markdown("---")

    # 3. Severity / Priority Levels
    st.markdown("### ⚠️ Severity Priorities")
    st.markdown(
        "- **P0 (Critical)**: Broad outages, compromises.\n"
        "- **P1 (Important)**: Blockers, billing active failures.\n"
        "- **P2 (Normal)**: Non-blocking bugs, enhancements."
    )
    st.markdown("---")

    # 4. Semantic vector search explanation
    st.markdown("### 🔍 What is Semantic Search?")
    st.markdown(
        "Standard keyword search looks for exact text matches. "
        "Sentinel AI's semantic search uses deep learning to understand the **underlying meaning** "
        "of the sentence, finding relevant issues even if different vocabulary is used."
    )


# =====================================================================
# MAIN USER INTERFACE HEADER & EXAMPLES CONSOLE
# =====================================================================
st.title("🛡️ SentinelAI - Enterprise Incident Intelligence System")
st.caption("Powered by FAISS • Sentence Transformers • Groq Llama3-70B")
st.markdown(
    "A modern explainable operations center that analyzes security threats, "
    "billing discrepancies, and infrastructure incidents using semantic search and AI reasoning."
)
st.markdown("---")

# Row of Quick-Select pre-configured example incident buttons.
# Columns separate Streamlit widgets horizontally.
st.markdown("### 📋 Quick Triage Incident Simulator")
st.markdown("Click any scenario button to instantly load and execute the Sentinel AI triage pipeline:")

col_scen1, col_scen2, col_scen3 = st.columns(3)

with col_scen1:
    st.markdown("**🔴 Scenario A: Security Compromise**")
    if st.button("Simulate Overseas Threat", key="scen_a"):
        load_and_triage_scenario(
            "Multiple failed login attempts detected from overseas IP "
            "and employees cannot access payroll dashboard."
        )

with col_scen2:
    st.markdown("**🟡 Scenario B: Billing Anomaly**")
    if st.button("Simulate Premium Billing Block", key="scen_b"):
        load_and_triage_scenario(
            "Our corporate credit card was charged twice for the annual premium subscription, "
            "but the team dashboard is still showing an 'Inactive/Suspended' status."
        )

with col_scen3:
    st.markdown("**🔵 Scenario C: System Crash**")
    if st.button("Simulate UI Memory Leak", key="scen_c"):
        load_and_triage_scenario(
            "The telemetry graphing dashboard keeps crashing and reloading with a frontend JS memory leak "
            "when uploading heavy CSV usage reports."
        )

st.markdown("---")


# =====================================================================
# INCIDENT USER INPUT FORM
# =====================================================================
st.markdown("### 🖥️ Live Incident Ingestion Console")

# The large text input area. We bind its value directly to our session state
# so that the load scenario buttons can overwrite the text dynamically.
incident_text = st.text_area(
    "Describe the incident or copy/paste raw logs below:",
    value=st.session_state.incident_input_widget,
    key="incident_input_widget",
    height=130,
    placeholder="E.g., Production databases are timing out, or employee complains about MFA lockout..."
)

# Row containing the analysis button. Centered layout representation in Streamlit.
button_col1, button_col2, button_col3 = st.columns([2, 2, 2])
with button_col2:
    analyze_clicked = st.button("🛡️ Execute Sentinel AI Triage")


# =====================================================================
# AGENT ANALYSIS & TELEMETRY REPORTING
# =====================================================================
# We run the triage pipeline if either the 'Execute' button is manually clicked
# OR the 'run_triage_trigger' session flag is activated by clicking an example button.
if analyze_clicked or st.session_state.run_triage_trigger:
    # Immediately reset the session state trigger flag to avoid loop-triggering on future UI updates.
    st.session_state.run_triage_trigger = False
    
    # Input validation: make sure the text box is not empty
    if not incident_text.strip():
        st.warning("⚠️ Ingestion halted. Please enter or select an incident description first.")
    else:
        # Streamlit status container shows multiple processing stages in a single collapsible widget
        with st.status("Analyzing incident via Sentinel AI Reasoning Agent...", expanded=True) as status:
            st.write("🔍 **Stage 1:** Retrieving semantic memory from FAISS vector storage...")
            # Small realistic sleep transitions to give operators time to view each operations step
            time.sleep(0.6)
            
            st.write("🧠 **Stage 2:** Running AI reasoning and scanning operational rules...")
            time.sleep(0.6)
            
            st.write("📊 **Stage 3:** Calculating classification confidence scoring...")
            time.sleep(0.6)
            
            st.write("📧 **Stage 4:** Generating enterprise acknowledgement responses...")
            time.sleep(0.6)
            
            # Execute actual triage operations
            triage_report = triage_incident(incident_text)
            
            # Update status indicator to success complete
            status.update(label="Triage analysis complete!", state="complete", expanded=False)
            
        st.markdown("### 📊 Active Incident Intelligence Report")
        
        # 1. TOP METRIC TILES
        # Display key triage metadata side-by-side
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        # Extract fields from the agent response
        category = triage_report.get("category", "N/A")
        priority = triage_report.get("priority", "N/A")
        confidence = triage_report.get("confidence", 0.0)
        escalation = triage_report.get("human_escalation", False)
        
        with metric_col1:
            st.metric(label="Incident Category", value=category)
            
        with metric_col2:
            st.metric(label="Priority Assignment", value=priority)
            
        with metric_col3:
            st.metric(label="AI Confidence Index", value=f"{confidence * 100:.1f}%")
            
        with metric_col4:
            st.metric(
                label="Human Escalation Status", 
                value="🚨 ESCALATED" if escalation else "✅ SAFE"
            )

        # 2. CONFIDENCE PROGRESS BAR
        # Renders a horizontal progress bar based on confidence value [0.0 - 1.0]
        st.progress(float(confidence))
        st.markdown(f"<p style='text-align: right; font-size: 0.8rem; color: #94a3b8;'>Confidence Rating: {confidence:.2f}</p>", unsafe_allow_html=True)
        
        # 3. DYNAMIC ESCALATION ALERTS
        # Displays colored responsive boxes to draw operators' immediate attention
        if escalation:
            st.warning(
                "⚠️ **ESCALATION PROTOCOL ENFORCED:** This ticket has been routed to **Human Engineering Tier 3 Support**.\n\n"
                "*Rationale:* This is due to a Critical Priority (P0) classification, Security threat flags, "
                "or an AI confidence index falling below the established 0.6 safety threshold."
            )
        else:
            st.success(
                "✅ **STANDARD OPERATIONS PROTOCOL:** Incident successfully classified and logged without escalation.\n\n"
                "*Status:* Assigned resolution queues have been notified and standard corporate queues are operating normally."
            )
            
        # 4. SIDE-BY-SIDE ANALYTICAL TELEMETRY
        # Col 1: AI step-by-step reasoning. Col 2: FAISS similar matches.
        telemetry_col1, telemetry_col2 = st.columns(2)
        
        with telemetry_col1:
            st.markdown("#### 📋 AI Reasoning Timeline")
            # We wrap the timeline inside an st.expander, so the dashboard looks clean
            # but allows deep-dive inspection of how the AI made its decisions.
            with st.expander("🔍 View Step-by-Step Reasoning Trace (Auditable Trail)", expanded=True):
                for step_num, step_desc in enumerate(triage_report.get("reasoning_trace", []), 1):
                    # We format as a beautiful list
                    st.markdown(f"**Step {step_num}:** {step_desc}")

        with telemetry_col2:
            st.markdown("#### 🔍 Similar Historical Incidents")
            # Convert FAISS dictionary results directly to a Pandas DataFrame for professional rendering
            similar_list = triage_report.get("similar_incidents", [])
            
            if similar_list:
                df = pd.DataFrame(similar_list)
                
                # Format dataframe column titles beautifully
                df.columns = ["Historical Incident", "Category", "Resolution", "Semantic Score"]
                
                # Format scores to 2-decimal percentages for operational dashboards
                df["Semantic Score"] = df["Semantic Score"].map(lambda x: f"{x * 100:.1f}%")
                
                # st.dataframe displays interactive tables supporting column sorting and cell copying
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No matching historical logs found above standard similarity thresholds in memory.")
                
#         # 5. INTERACTIVE 2D SEMANTIC MEMORY SPACE MAP (PCA & ALTAIR)
#         # This is an explainable AI feature that projects high-dimensional embeddings (384-dim)
#         # into a 2D space so operators can see the proximity of the incident relative to historical data.
#         st.markdown("---")
#         st.markdown("### 🌌 2D Semantic Memory Space Map (Vector Dimension Projection)")
#         st.markdown(
#             "This interactive scientific visualization maps the **384-dimensional semantic embeddings** "
#             "of your incident records down to a **2-dimensional principal component coordinate plane** in real-time. "
#             "It displays how the active query (white glowing diamond) sits relative to historical incident clusters."
#         )
        
#         try:
#             from sklearn.decomposition import PCA
#             import numpy as np
#             import altair as alt
            
#             # Retrieve model embeddings and query embedding
#             from memory import model, issue_embeddings, incidents as memory_incidents
            
#             # Encode active query to vector space
#             query_emb = model.encode([incident_text], convert_to_numpy=True)
            
#             # Concatenate all embeddings for a combined PCA space
#             all_embeddings = np.concatenate([issue_embeddings, query_emb], axis=0)
            
#             # Run Principal Component Analysis (PCA) to project 384 dimensions to 2D
#             pca_model = PCA(n_components=2)
#             coords_2d = pca_model.fit_transform(all_embeddings)
            
#             # Compile DataFrame data
#             plot_data = []
            
#             # Add historical incidents
#             similar_incidents = triage_report.get("similar_incidents", [])
#             for idx, incident in enumerate(memory_incidents):
#                 # Check similarity score of this incident
#                 match_score = 0.0
#                 is_match = False
#                 for sim in similar_incidents:
#                     if sim["issue"] == incident["issue"]:
#                         match_score = sim["similarity_score"]
#                         is_match = True
#                         break
                
#                 # Setup visualization scale values
#                 plot_data.append({
#                     "PC1": float(coords_2d[idx, 0]),
#                     "PC2": float(coords_2d[idx, 1]),
#                     "Description": incident["issue"],
#                     "Category": incident["category"],
#                     "Node Classification": incident["category"],
#                     "Node Type": "Historical Incident",
#                     "Similarity Score": f"{match_score * 100:.1f}%" if is_match else "Background Node",
#                     "Match Proximity": float(match_score) * 600 if is_match else 150
#                 })
                
#             # Add active query node at coords_2d[-1]
#             plot_data.append({
#                 "PC1": float(coords_2d[-1, 0]),
#                 "PC2": float(coords_2d[-1, 1]),
#                 "Description": incident_text,
#                 "Category": "Active Incident",
#                 "Node Classification": "ACTIVE SEARCH QUERY",
#                 "Node Type": "ACTIVE SEARCH QUERY",
#                 "Similarity Score": "100.0% (Origin)",
#                 "Match Proximity": 550
#             })
#   # Add active query node safely
#             query_x = float(coords_2d[-1, 0])
#             query_y = float(coords_2d[-1, 1])

# # Validate coordinates before plotting
#             if (
#                 query_x is not None and
#                 query_y is not None and
#                 not np.isnan(query_x) and
#                 not np.isnan(query_y)
#             ):
#                 plot_data.append({
#                    "PC1": query_x,
#                    "PC2": query_y,
#                    "Description": incident_text,
#                    "Category": "Active Incident",
#                    "Node Classification": "ACTIVE SEARCH QUERY",
#                    "Node Type": "ACTIVE SEARCH QUERY",
#                    "Similarity Score": "100.0% (Origin)",
#                    "Match Proximity": 550
#                 })
            
#             # Create dataframe safely
#             plot_df = pd.DataFrame(plot_data)

# # Remove invalid numeric rows
#             plot_df = plot_df.dropna(subset=["PC1", "PC2"])

# # Ensure numeric conversion
#             plot_df["PC1"] = pd.to_numeric(plot_df["PC1"], errors="coerce")
#             plot_df["PC2"] = pd.to_numeric(plot_df["PC2"], errors="coerce")

# # Remove any remaining invalid values
#             plot_df = plot_df.dropna(subset=["PC1", "PC2"])
#             # Create Altair Scatter Plot
#             # Custom dark colors mapping to the dashboard styling
#             color_scale = alt.Scale(
#                 domain=['Security', 'Billing', 'Technical Issue', 'Account Access', 'Feature Request', 'ACTIVE SEARCH QUERY'],
#                 range=['#ef4444', '#f59e0b', '#3b82f6', '#8b5cf6', '#10b981', '#ffffff']
#             )
            
#             scatter = alt.Chart(plot_df).mark_circle().encode(
#                 x=alt.X('PC1:Q', title='Principal Component 1 (Semantic Width)', axis=alt.Axis(labels=False, ticks=False, gridColor='#334155')),
#                 y=alt.Y('PC2:Q', title='Principal Component 2 (Semantic Height)', axis=alt.Axis(labels=False, ticks=False, gridColor='#334155')),
#                 color=alt.Color('Node Classification:N', scale=color_scale, legend=alt.Legend(
#                     title="Incident Category Classifications", 
#                     orient="top", 
#                     labelColor="#94a3b8", 
#                     titleColor="#f1f5f9"
#                 )),
#                 size=alt.Size('Match Proximity:Q', scale=alt.Scale(range=[200, 950]), legend=None),
#                 tooltip=['Description:N', 'Category:N', 'Similarity Score:N', 'Node Type:N']
#             ).properties(
#                 width=None,  # Responsive width
#                 height=350,
#                 title=""
#             ).configure_view(
#                 strokeWidth=0
#             )
            
            
#             # Render chart safely
#             if not plot_df.empty:
#                  st.altair_chart(scatter, use_container_width=True)
#             else:
#                 st.warning("No valid semantic coordinates available for plotting.")
#         except Exception as vis_err:
#             st.info(f"Interactive 2D Topology mapping is currently operating in fallback mode. (Details: {vis_err})")
#         //    # ============================================================
# SEMANTIC VISUALIZATION TEMPORARILY DISABLED
# ============================================================

        st.markdown("---")
        st.markdown("### 🌌 Semantic Memory Visualization")

        st.info(
          "The advanced semantic topology visualization module is currently "
          "disabled in this deployment build. "
          "Core AI triage, semantic retrieval, explainable reasoning, and "
          "enterprise escalation systems remain fully operational."
        )
        # 6. ENTERPRISE ACKNOWLEDGEMENT NOTIFICATION
        # Renders the exact email / slack template built by the AI
        st.markdown("---")
        st.markdown("#### 📧 Generated Corporate Acknowledgement Template")
        st.info("Below is the custom communication generated by the agent for active incident channels:")
        
        # st.code displays text inside a premium code container with a quick-copy button!
        st.code(triage_report.get("acknowledgement", ""), language="text")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #475569;'>Sentinel AI Security Command • Ingested and Logged via FAISS Flat Vector Indexing</p>", unsafe_allow_html=True)
