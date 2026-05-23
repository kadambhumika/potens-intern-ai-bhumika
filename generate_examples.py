import os
import json
from agent import triage_incident

examples_inputs = [
    "Multiple failed login attempts detected from overseas IP and employees cannot access payroll dashboard.",
    "Our corporate credit card was charged twice for the annual premium subscription, but the team dashboard is still showing an 'Inactive' status.",
    "The telemetry graphing dashboard keeps crashing and reloading with a frontend JS memory leak when uploading heavy CSV usage reports.",
    "I forgot my password and the reset email is not arriving to my corporate inbox.",
    "Can you please add a dark mode toggle to the main dashboard? The bright white is hurting our eyes during night shifts.",
    "The database connection timed out during the nightly backup, and now the replica is out of sync.",
    "A user is reporting that their Multi-Factor Authentication (MFA) token app is out of sync and they are locked out.",
    "We need to cancel our enterprise billing plan immediately, we were charged an unexpected $500 overage fee.",
    "Security scan shows our main server has an open port 22 exposed to the public internet.",
    "The new dashboard is great but it would be really helpful if we could export the incident list as a PDF."
]

def generate():
    os.makedirs("examples", exist_ok=True)
    for i, user_input in enumerate(examples_inputs, 1):
        print(f"Generating example {i}...")
        result = triage_incident(user_input)
        
        output_data = {
            "input": user_input,
            "agent_output": result
        }
        
        filepath = os.path.join("examples", f"example_{i:02d}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2)
            
    print("Successfully generated 10 examples in the examples/ folder.")

if __name__ == "__main__":
    generate()
