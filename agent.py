import json
import os
import sys

try:
    from groq import Groq
except ImportError:
    print("\nWARNING: The 'groq' python library is not installed in this environment.")
    Groq = None

try:
    import tools
except ImportError as err:
    print(f"CRITICAL ERROR: Failed to import tools.py: {err}")
    sys.exit(1)


def triage_incident(user_input):
    """
    Analyzes an incoming incident report and selects a tool to execute.
    Returns:
    - dict: { category, priority, next_tool, reasoning, why, tool_result }
    """
    print(f"\n[AI Agent] Starting triage workflow for incoming incident: '{user_input}'")

    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key or Groq is None:
        print("[AI Agent] Running triage in explainable MOCK SIMULATION MODE.")
        triage_report = _simulate_agent_triage(user_input)
    else:
        print("[AI Agent] GROQ_API_KEY detected. Executing live AI Triage call...")
        triage_report = _execute_live_groq_triage(user_input, groq_api_key)

    # Programmatic Tool Execution (REAL TOOL CALLING)
    next_tool = triage_report.get("next_tool")
    print(f"[AI Agent] Agent selected next_tool: {next_tool}. Executing now...")
    
    tool_result = None
    if next_tool == "search_past_incidents":
        tool_result = tools.search_past_incidents(user_input)
    elif next_tool == "lookup_customer_record":
        tool_result = tools.lookup_customer_record()
    elif next_tool == "draft_acknowledgement":
        tool_result = tools.draft_acknowledgement(triage_report.get("category"))
    else:
        tool_result = {"error": "Invalid or missing tool selected by agent."}
        
    triage_report["tool_result"] = tool_result

    return triage_report


def _execute_live_groq_triage(user_input, api_key):
    """
    Executes a live chat completion call to the Groq API.
    """
    client = Groq(api_key=api_key)
    
    tools_list_str = json.dumps(tools.AVAILABLE_TOOLS, indent=2)

    system_prompt = (
        "You are an expert enterprise incident triage AI agent.\n"
        "Analyze the incoming IT incident and classify it according to these strict rules:\n\n"
        "Categories:\n"
        "- Security: Potential unauthorized access, MFA issues, credential compromises, data exposures.\n"
        "- Billing: Deductions, payment errors, subscription sync, invoice requests.\n"
        "- Technical Issue: Application crashes, server downtime, frontend bugs, performance lag.\n"
        "- Account Access: Password resets, locked accounts, single-sign-on (SSO) issues.\n"
        "- Feature Request: Styling enhancements, dark mode requests, new feature suggestions.\n\n"
        "Priorities:\n"
        "- P0 = Critical (Outages affecting multiple users, active security threats, payroll lockout)\n"
        "- P1 = Important (Individual blocker issues, billing discrepancies affecting access)\n"
        "- P2 = Normal (Minor styling improvements, non-blocking bug reports, feature requests)\n\n"
        f"Available Tools to Pick As next_tool:\n{tools_list_str}\n\n"
        "JSON Formatting Guideline:\n"
        "You MUST respond with a single, raw JSON object exactly matching this schema:\n"
        "{\n"
        "  \"category\": \"<Category>\",\n"
        "  \"priority\": \"<Priority>\",\n"
        "  \"next_tool\": \"<Tool Name>\",\n"
        "  \"reasoning\": [\"Step 1 thought\", \"Step 2 thought\"],\n"
        "  \"why\": \"<A single sentence explaining why this tool and category were chosen>\"\n"
        "}"
    )

    user_prompt = f"Incoming Incident Report: \"{user_input}\""

    try:
        chat_completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        raw_response = chat_completion.choices[0].message.content
        return json.loads(raw_response)
        
    except Exception as api_error:
        print(f"\n[AI Agent] Groq Live API Error: {api_error}")
        return _simulate_agent_triage(user_input)


def _simulate_agent_triage(user_input):
    """
    Simulates AI triage locally when Groq API key is missing.
    Matches the exact JSON schema required by Potens Q2 guidelines.
    """
    text_lower = user_input.lower()
    
    category = "Technical Issue"
    priority = "P2"
    next_tool = "search_past_incidents"
    reasoning = ["Ingested incident report.", "Scanning for keywords..."]
    why = "Standard technical issue requires searching past incidents for a fix."

    is_security = "login" in text_lower or "failed" in text_lower or "ip" in text_lower or "security" in text_lower
    is_payroll = "payroll" in text_lower or "salary" in text_lower
    
    if is_security and is_payroll:
        category = "Security"
        priority = "P0"
        next_tool = "lookup_customer_record"
        reasoning.extend(["Flagged multiple security patterns.", "Impacts payroll dashboard."])
        why = "P0 Security threat on payroll requires immediate customer record lookup to lock account."
    elif is_security:
        category = "Security"
        priority = "P1"
        next_tool = "lookup_customer_record"
        reasoning.append("Flagged security vulnerability indicators.")
        why = "Security issue detected; verifying customer account status."
    elif "billing" in text_lower or "payment" in text_lower:
        category = "Billing"
        priority = "P1"
        next_tool = "lookup_customer_record"
        reasoning.append("Found billing-related terms.")
        why = "Billing anomalies require pulling the customer's subscription record."
    elif "password" in text_lower or "reset" in text_lower:
        category = "Account Access"
        priority = "P2"
        next_tool = "draft_acknowledgement"
        reasoning.append("Identified account access keyphrases.")
        why = "Standard password reset; drafting automated instructions."
    elif "feature" in text_lower or "request" in text_lower:
        category = "Feature Request"
        priority = "P2"
        next_tool = "draft_acknowledgement"
        reasoning.append("Recognized feature request.")
        why = "Feature requests can be automatically acknowledged."
    else:
        reasoning.append("No specific category keyphrases found, defaulting to Technical Issue.")

    return {
        "category": category,
        "priority": priority,
        "next_tool": next_tool,
        "reasoning": reasoning,
        "why": why
    }


if __name__ == "__main__":
    test_incident = "Multiple failed login attempts detected from overseas IP and employees cannot access payroll dashboard."
    result = triage_incident(test_incident)
    print(json.dumps(result, indent=2))
