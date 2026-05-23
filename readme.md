# 🛡️ Sentinel AI - Enterprise Incident Intelligence System

Sentinel AI is a modern, AI-powered operations center dashboard built to automatically triage, classify, and escalate incoming enterprise IT incidents. Using advanced semantic search and large language model (LLM) reasoning, the system provides real-time analytics, auditable decision trails, and automated enterprise communications.

## 🌟 Key Features

*   **Semantic Memory Retrieval**: Utilizes `sentence-transformers` (`all-MiniLM-L6-v2`) and **FAISS** (Facebook AI Similarity Search) to find historically similar incidents based on their underlying meaning, rather than exact keyword matches.
*   **AI Reasoning Engine**: Integrates with the **Groq API** (`llama3-70b-8192`) to dynamically classify incidents into categories (Security, Billing, Technical Issue, Account Access, Feature Request) and assign priority severity levels (P0, P1, P2).
*   **Automated Escalation Protocols**: Programmatic safety thresholds enforce human escalation (Tier 3 Engineering Support) if the AI confidence score drops below 60% or if a P0 Critical/Security threat is detected.
*   **Live Operations Dashboard**: Built with **Streamlit**, featuring a dark-themed, glassmorphic UI that visualizes metric tiles, AI reasoning timelines, and semantic match proximities.
*   **Explainable Mock Mode**: Automatically falls back to a realistic local simulation mode if no Groq API key is detected, allowing beginners to test the dashboard out of the box.

## ⚙️ System Architecture

1.  **Streamlit UI (`app.py`)**: Receives incoming alert reports and visualizes the telemetry data.
2.  **FAISS Vector Storage (`memory.py`)**: Queries the historical incident database (`data/incidents.json`) for semantic similarities.
3.  **Groq Reasoning Agent (`agent.py`)**: Injects semantic matches as context and processes the triage via the Groq LLM.
4.  **Telemetry & Safety**: Enforces structured JSON outputs and safety thresholds locally before returning the classification.

## 🚀 Getting Started

### Prerequisites

*   Python 3.8+
*   *(Optional but recommended)* A free API key from [Groq](https://console.groq.com/) for live LLM inference.

### Installation

1.  **Clone the repository or navigate to the project directory:**
    ```bash
    cd sentinel-ai
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    To use live AI triage, set your Groq API key.
    ```powershell
    # Windows PowerShell
    $env:GROQ_API_KEY="your_groq_api_key_here"
    ```
    ```bash
    # macOS/Linux
    export GROQ_API_KEY="your_groq_api_key_here"
    ```
    *(If no key is provided, the system safely falls back to a built-in deterministic simulation mode).*

### Running the Application

Launch the Streamlit operations dashboard:

```bash
streamlit run app.py
```

The application will be accessible in your web browser, typically at `http://localhost:8501`.

## 📁 Project Structure

*   `app.py`: The main Streamlit frontend application.
*   `agent.py`: Contains the triage logic, Groq LLM integration, and programmatic safety checks.
*   `memory.py`: Handles loading the incident database, generating text embeddings, and executing FAISS similarity searches.
*   `data/incidents.json`: The historical incident database used for the semantic memory index.

## 🏷️ Supported Classifications

*   **Security**: Intrusion alerts, MFA/credentials.
*   **Billing**: Payment deduplication, subscription errors.
*   **Technical Issue**: Downtime, crash loops, memory leaks.
*   **Account Access**: Locked accounts, password resets.
*   **Feature Request**: Aesthetics, roadmap requests.

## ⚠️ Severity Priorities

*   **P0 (Critical)**: Broad outages, compromises, active threats.
*   **P1 (Important)**: Blockers, active billing failures.
*   **P2 (Normal)**: Non-blocking bugs, enhancements, feature requests.

## 🏗️ Design Decisions

*   **Real Tool Calling & Modular Design**: Integrated a proper multi-tool framework (`tools.py`) where the AI can autonomously select functions such as semantic searching, customer record lookup, or automated email drafting. 
*   **LLM Choice (llama3-70b-8192)**: Using Groq for low-latency JSON mode response. Llama3-70B was chosen for its high reasoning capabilities to ensure accurate triage categorizations without hallucinations.
*   **Semantic Over Lexical Search**: Using `sentence-transformers` and `FAISS` rather than simple keyword matching (like Elasticsearch). This allows the agent to recognize incidents described with different phrasing.
*   **Strict Output Schema via JSON Mode**: The system guarantees deterministic structure (`{ category, priority, next_tool, reasoning, why, tool_result }`) by leveraging structured generation and fallback mock simulation.

## 🚧 What is Broken or Unfinished

*   **Mock Tool Implementations**: The `lookup_customer_record` tool currently returns a mock dictionary instead of querying a real PostgreSQL/Stripe database.
*   **Altair Visualization**: The 2D PCA semantic projection map in the Streamlit UI is currently commented out due to dependency conflicts and edge-case rendering bugs.

## 🔮 What I Would Build Next

1.  **Human-in-the-Loop Triage Gate**: Implement an explicit Streamlit view where P0 or low-confidence issues wait for a manual admin "Approve/Reject" button before dispatching the ticket to Jira.
2.  **Live Database Hooks**: Connect `lookup_customer_record` to actual CRM APIs (like Salesforce or HubSpot).
3.  **Reranking Strategy**: Apply a Cross-Encoder to re-rank FAISS matches before feeding them to the LLM to improve context density.

---

## 🤖 AI USE LOG

*   **Claude 3.5 Sonnet / Antigravity Agent**: ~15,000 tokens / 20 messages. Used to plan the architecture, generate the FAISS semantic search logic, enforce the JSON output schema, and align the project exactly with the internship guidelines (including the implementation of `tools.py`).
*   **GitHub Copilot**: ~200 lines accepted. Used for boilerplate auto-completions in Streamlit UI configurations, generating the list of 10 example test cases, and standard Python exception handling.
