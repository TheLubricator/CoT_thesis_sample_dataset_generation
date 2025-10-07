# PERFECT SOLUTION - Extract from structured final answer section

def extract_final_answer_structured(cot_text):
    """
    Extract answer from the structured '5. Give a clear final answer:' section
    This works specifically with the improved prompt engineering
    """
    
    # Primary pattern for structured prompts
    structured_patterns = [
        r"\*\*5\.\s*Give a clear final answer:\*\*.*?(\d+)",              # "**5. Give a clear final answer:** Mark has **35** flowers"
        r"5\.\s*Give a clear final answer:.*?\*\*(\d+)\*\*",             # "5. Give a clear final answer: **35**"
        r"Give a clear final answer:.*?\*\*(\d+)\*\*",                   # "Give a clear final answer: **35**"
        r"final answer.*?\*\*(\d+)\*\*",                                # "final answer: **35**"
    ]
    
    # Fallback patterns (in case formatting varies)
    fallback_patterns = [
        r"Answer:\s*.*?\*\*(\d+)\*\*",                                  # "Answer: **35**"
        r"\*\*(\d+)\*\*\s*(?:flowers?|pages?|pounds?|dollars?|pieces?|total|people|items?)(?:\s*\.|\s*$)",  # "**35** flowers."
    ]
    
    # Try structured patterns first (highest priority)
    for pattern in structured_patterns:
        matches = re.findall(pattern, cot_text, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[0]  # Return first match from final section
    
    # Try fallback patterns
    for pattern in fallback_patterns:
        matches = re.findall(pattern, cot_text, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[-1]  # Return last match (most likely final)
    
    return None

# This should replace the patterns in your generate_cot_improved function
print("Use this as your primary extraction pattern:")
print('r"\\*\\*5\\.\\s*Give a clear final answer:\\*\\*.*?(\\d+)"')
