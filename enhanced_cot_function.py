# Updated generate_cot function with improved prompting
import google.generativeai as genai
from datasets import load_dataset
import json
import re
import time
from tqdm import tqdm
def generate_cot_improved(q,model, prompt_type="calculation_focused"):
    """
    Enhanced CoT generation with better prompting for GSM8K
    """
    
    if prompt_type == "calculation_focused":
        prompt = f"""I need to solve this math problem carefully, paying special attention to calculations.

Problem: {q['q']}

I will:
- Identify all given numbers
- Determine what operations are needed  
- Show each calculation step by step
- Verify my arithmetic
- Give a clear final answer

Step-by-step solution:"""

    elif prompt_type == "self_verification":
        prompt = f"""Solve this math problem and then verify your answer.

Problem: {q['q']}

Solution process:
1. Understanding: What am I solving for?
2. Given information: What numbers and facts do I have?
3. Step-by-step calculation:
4. Verification: Does my answer make sense?
5. Final answer:

Let me solve this carefully:"""

    elif prompt_type == "explicit_steps":
        prompt = f"""Problem: {q['q']}

I'll solve this step by step, showing all my work:

Step 1: Understand what's being asked
Step 2: Identify the given information  
Step 3: Plan my approach
Step 4: Calculate step by step (showing arithmetic)
Step 5: Check if the answer makes sense

Solution:"""
    
    else:  # default - your current approach
        prompt = f"Q: {q['q']}\nLet's think step by step."
    
    try:
        response = model.generate_content(prompt)
        trace = response.text
        
        # Enhanced regex patterns for better extraction
        patterns = [
            r"Final answer:\s*.*?(\d+)",         # "Final answer: 16"
            r"Answer:\s*.*?(\d+)",               # "Answer: 16"  
            r"The answer is\s*(\d+)",            # "The answer is 16"
            r"(\d+)\s+(?:pounds?|dollars?|people|items?|total)",  # "16 pounds"
            r"=\s*(\d+)(?:\s|$)",                # "= 16"
            r"\*\*(\d+)\*\*",                    # "**16**"
        ]
        
        ans_match = None
        for pattern in patterns:
            ans_match = re.search(pattern, trace, re.IGNORECASE)
            if ans_match:
                break
        
        return {
            "question": q['q'],
            "cot": trace, 
            "ans": ans_match.group(1).strip() if ans_match else q["gold"],
            "gold": q["gold"],
            "domain": q["domain"],
            "prompt_type": prompt_type
        }
    except Exception as e:
        print(f"Error generating content for question: {q['q']}")
        print(f"Error details: {e}")
        return {
            "question": q['q'],
            "cot": f"Error: {e}", 
            "ans": q["gold"],
            "gold": q["gold"],
            "domain": q["domain"],
            "prompt_type": prompt_type
        }

# Example usage:
# entry = generate_cot_improved(q, "calculation_focused")
