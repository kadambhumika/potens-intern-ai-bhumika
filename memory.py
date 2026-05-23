import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Define path to the incidents data file
INCIDENTS_PATH = os.path.join("data", "incidents.json")

# =====================================================================
# 1. LOAD INCIDENTS DATABASE WITH ROBUST ERROR HANDLING
# =====================================================================
def load_incidents(filepath):
    """
    Loads incident records from a JSON file.
    
    Includes beginner-friendly error handling for:
    - Missing incident database file
    - Malformed or syntax-error-ridden JSON
    - Invalid data structures (e.g., dictionary instead of a list)
    - Empty incident lists
    """
    # Error Handling Scenario #1: Missing incidents.json
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"The incident database file was not found at: '{filepath}'.\n"
            f"--> Please verify that 'data/incidents.json' exists in your directory structure."
        )
        
    # Open the file and parse the JSON contents safely
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as parse_error:
        # Error Handling Scenario: Malformed/Syntax error in JSON
        raise ValueError(
            f"Failed to read the JSON file at '{filepath}' due to a syntax error:\n"
            f"--> {parse_error.msg} at line {parse_error.lineno}, column {parse_error.colno}.\n"
            f"--> Please check for missing commas, unclosed brackets, or invalid quotes in the file."
        )
        
    # Error Handling: Ensure that the JSON file contains a list of items
    if not isinstance(data, list):
        raise ValueError(
            f"The data inside '{filepath}' must be a JSON array/list of incidents,\n"
            f"but we received a {type(data).__name__} instead."
        )
        
    # Error Handling Scenario #2: Empty incident list
    if len(data) == 0:
        raise ValueError(
            f"The incident database in '{filepath}' is empty!\n"
            f"--> Please add at least one historical incident to the file before building the vector memory index."
        )
        
    return data


# Safe loading of the incident database
try:
    print("Loading incidents database from JSON...")
    incidents = load_incidents(INCIDENTS_PATH)
    print(f"Loaded {len(incidents)} incidents successfully.")
except (FileNotFoundError, ValueError) as db_error:
    print("\n" + "!" * 80)
    print(f"DATABASE INITIALIZATION ERROR:\n{db_error}")
    print("!" * 80 + "\n")
    # Terminate or raise so the user knows immediately what failed
    raise


# =====================================================================
# 2. INITIALIZE SEMANTIC EMBEDDING MODEL
# =====================================================================
# We use the SentenceTransformer library to convert text into numeric vectors (embeddings).
# The 'all-MiniLM-L6-v2' model is a fast, lightweight, and highly effective model.
print("\nLoading sentence-transformers model ('all-MiniLM-L6-v2')...")
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully!")
except Exception as model_error:
    print("\n" + "!" * 80)
    print(f"MODEL LOADING ERROR:\n"
          f"Failed to load the SentenceTransformer model.\n"
          f"--> Error details: {model_error}\n"
          f"--> Please ensure that PyTorch and sentence-transformers are properly installed\n"
          f"    and that you have an active internet connection to download the model if it's the first run.")
    print("!" * 80 + "\n")
    raise


# =====================================================================
# 3. GENERATE TEXT EMBEDDINGS WITH ERROR HANDLING
# =====================================================================
# We need to convert each incident's "issue" text into a numerical embedding vector.
print("\nGenerating vector embeddings for loaded incidents...")
try:
    # Ensure all incident issues are valid non-empty strings before encoding
    issues = []
    for idx, incident in enumerate(incidents):
        issue_text = incident.get("issue")
        if not issue_text or not isinstance(issue_text, str) or len(issue_text.strip()) == 0:
            raise ValueError(
                f"Incident at index {idx} contains an invalid, empty, or missing 'issue' field."
            )
        issues.append(issue_text)

    # Error Handling Scenario #3: Failed embedding generation
    # We wrap encoding in a try-block in case of backend runtime errors (CUDA out-of-memory, etc.)
    issue_embeddings = model.encode(issues, convert_to_numpy=True)
    print(f"Generated {issue_embeddings.shape[0]} embeddings. Dimension size: {issue_embeddings.shape[1]}")
    
except Exception as embed_error:
    print("\n" + "!" * 80)
    print(f"EMBEDDING GENERATION ERROR:\n"
          f"Failed during text embedding generation.\n"
          f"--> Error details: {embed_error}\n"
          f"--> Ensure your training data issues contain valid strings and your execution memory limits are sufficient.")
    print("!" * 80 + "\n")
    raise


# =====================================================================
# 4. BUILD A SEARCHABLE FAISS INDEX
# =====================================================================
# FAISS (Facebook AI Similarity Search) stores our vectors for quick nearest-neighbor query comparisons.
try:
    embedding_dimension = issue_embeddings.shape[1]
    
    # We create an L2 distance index (IndexFlatL2).
    index = faiss.IndexFlatL2(embedding_dimension)
    
    # Add our generated issue embeddings into the FAISS index
    index.add(issue_embeddings)
    print(f"FAISS index built successfully with {index.ntotal} vectors.")
except Exception as faiss_error:
    print("\n" + "!" * 80)
    print(f"FAISS INDEX ERROR:\n"
          f"Failed to build or populate the FAISS similarity index.\n"
          f"--> Error details: {faiss_error}")
    print("!" * 80 + "\n")
    raise


# =====================================================================
# 5. DEFINE THE SEMANTIC SEARCH FUNCTION WITH INPUT VALIDATION
# =====================================================================
def search_similar_incidents(query, top_k=3):
    """
    Searches the FAISS index for incidents that are semantically most similar to the user query.
    
    Parameters:
    - query (str): The search phrase entered by the user.
    - top_k (int): The number of closest matches to return (defaults to 3).
    
    Returns:
    - list of dicts: The top_k matching incidents with their issues, categories,
                     resolutions, and a beginner-friendly similarity score.
    """
    # A. Validate the query input
    if not query or not isinstance(query, str) or len(query.strip()) == 0:
        print("Warning: Received an empty or invalid search query. Returning an empty results list.")
        return []
        
    # B. Ensure top_k is a valid positive integer
    if not isinstance(top_k, int) or top_k <= 0:
        print(f"Warning: Invalid top_k value ({top_k}). Defaulting top_k to 3.")
        top_k = 3
        
    # C. Limit top_k to the number of vectors in our index to prevent index out of bounds
    if top_k > index.ntotal:
        top_k = index.ntotal
        
    try:
        # D. Convert user query to a numerical embedding vector.
        query_embedding = model.encode([query], convert_to_numpy=True)
        
        # E. Query the FAISS index.
        # D: An array of L2 distances. A lower distance means higher similarity!
        # I: An array of integer indices corresponding to the matching records in our original list.
        D, I = index.search(query_embedding, top_k)
        
        results = []
        
        # F. Process the results.
        for dist, idx in zip(D[0], I[0]):
            # FAISS returns -1 as the index if it cannot find enough matches
            if idx == -1:
                continue
                
            # Retrieve the original incident record from our list
            matched_incident = incidents[idx]
            
            # G. Convert L2 distance into a beginner-friendly similarity score between 0 and 1.
            # Similarity = 1 / (1 + d).
            similarity_score = 1.0 / (1.0 + float(dist))
            
            # Build the resulting dictionary
            results.append({
                "issue": matched_incident["issue"],
                "category": matched_incident["category"],
                "resolution": matched_incident["resolution"],
                "similarity_score": similarity_score
            })
            
        return results
        
    except Exception as search_error:
        print(f"Error occurred during similarity search: {search_error}")
        return []


# =====================================================================
# 6. TEST BLOCK
# =====================================================================
if __name__ == "__main__":
    # Test query from the user request
    test_query = "Unable to login after password reset"
    
    print("\n" + "=" * 80)
    print("                INCIDENT MEMORY SYSTEM - SEMANTIC SEARCH TEST")
    print("=" * 80)
    print(f"Search Query: '{test_query}'")
    print("-" * 80)
    
    # Perform vector similarity search
    matches = search_similar_incidents(test_query, top_k=3)
    
    # Print formatted results cleanly
    if not matches:
        print("No matching incidents were found or search query was invalid.")
    else:
        for i, match in enumerate(matches, 1):
            print(f"\nMatch #{i}:")
            print(f"  • Issue:      {match['issue']}")
            print(f"  • Category:   {match['category']}")
            print(f"  • Resolution: {match['resolution']}")
            print(f"  • Score:      {match['similarity_score']:.4f} (Similarity)")
        
    print("\n" + "=" * 80)
