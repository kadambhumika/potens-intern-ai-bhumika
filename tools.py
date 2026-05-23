import time

def search_past_incidents(query: str) -> dict:
    """
    Search the semantic FAISS index for similar past incidents.
    
    Args:
        query (str): A description of the incident or symptom.
        
    Returns:
        dict: The result containing matches or a failure message.
    """
    try:
        from memory import search_similar_incidents
        matches = search_similar_incidents(query, top_k=3)
        return {
            "tool_name": "search_past_incidents",
            "status": "success",
            "matches_found": len(matches),
            "data": matches
        }
    except ImportError:
        return {
            "tool_name": "search_past_incidents",
            "status": "error",
            "message": "Semantic memory module unavailable."
        }

def lookup_customer_record(account_id: str = None, email: str = None) -> dict:
    """
    Looks up enterprise customer billing and status records.
    
    Args:
        account_id (str, optional): The customer's internal ID.
        email (str, optional): The customer's email address.
        
    Returns:
        dict: A mock customer record detailing their status and active flags.
    """
    # MOCK implementation for the assignment demonstration
    time.sleep(0.3) # Simulate network delay
    
    return {
        "tool_name": "lookup_customer_record",
        "status": "success",
        "customer_data": {
            "subscription_tier": "Enterprise Premium",
            "account_status": "Active",
            "recent_flags": ["Multiple failed logins detected", "Billing sync mismatch"],
            "mfa_enabled": True
        }
    }

def draft_acknowledgement(category: str) -> dict:
    """
    Drafts an automated, enterprise-grade response to the customer based on category.
    
    Args:
        category (str): The classified category of the incident.
        
    Returns:
        dict: The drafted message ready to be sent to the user.
    """
    acknowledgements = {
        "Security": "We have detected a potential security risk on your account. Our cybersecurity response center has initiated an investigation. Please do not share sensitive credentials.",
        "Billing": "Your billing query has been logged. Our finance support reps are syncing your account subscription. Expect resolution shortly.",
        "Technical Issue": "We apologize for the technical difficulties. An incident ticket is logged and our engineering team is actively investigating.",
        "Account Access": "Your account access ticket is logged. Our support desk is verifying credentials and will provide recovery instructions soon.",
        "Feature Request": "Thank you for the feedback. Your request has been cataloged for our product management team's review."
    }
    
    draft = acknowledgements.get(
        category, 
        "Your ticket has been received and is being processed by our support team."
    )
    
    return {
        "tool_name": "draft_acknowledgement",
        "status": "success",
        "draft_text": draft
    }

# Provide a structured registry of available tools for the agent to pick from
AVAILABLE_TOOLS = [
    {
        "name": "search_past_incidents",
        "description": "Searches a vector database for historically similar incidents. Useful for Technical Issues or ambiguous bugs.",
        "parameters": {"query": "string"}
    },
    {
        "name": "lookup_customer_record",
        "description": "Looks up user account status, active security flags, and billing tier. Essential for Billing, Security, or Account Access incidents.",
        "parameters": {"account_id": "string (optional)", "email": "string (optional)"}
    },
    {
        "name": "draft_acknowledgement",
        "description": "Automatically generates a professional email response template to send back to the user based on category.",
        "parameters": {"category": "string"}
    }
]
