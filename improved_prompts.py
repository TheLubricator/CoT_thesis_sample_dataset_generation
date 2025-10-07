# Improved prompts for GSM8K based on error analysis

def get_enhanced_prompt(question, prompt_type="enhanced_structure"):
    """
    Generate improved prompts for GSM8K math problems
    """
    
    prompts = {
        "enhanced_structure": f"""Solve this math problem step by step. Be very careful with calculations.

Problem: {question}

Instructions:
1. Read the problem carefully and identify what is being asked
2. Break down the problem into smaller steps
3. Show ALL calculations clearly
4. Double-check your arithmetic
5. State your final answer clearly

Let me work through this step by step:""",

        "calculation_focused": f"""I need to solve this math problem carefully, paying special attention to calculations.

Problem: {question}

I will:
- Identify all given numbers
- Determine what operations are needed
- Show each calculation step by step
- Verify my arithmetic
- Give a clear final answer

Step-by-step solution:""",

        "self_verification": f"""Solve this math problem and then verify your answer.

Problem: {question}

Solution process:
1. Understanding: What am I solving for?
2. Given information: What numbers and facts do I have?
3. Step-by-step calculation:
4. Verification: Does my answer make sense?
5. Final answer:

Let me solve this carefully:""",

        "explicit_arithmetic": f"""Problem: {question}

I'll solve this step by step, showing all my work:

Step 1: Understand what's being asked
Step 2: Identify the given information  
Step 3: Plan my approach
Step 4: Calculate step by step (showing arithmetic)
Step 5: Check if the answer makes sense

Solution:""",

        "multi_step_focused": f"""This is a multi-step word problem. I need to be extra careful.

Problem: {question}

I will:
- Break this into smaller sub-problems
- Solve each part completely before moving to the next
- Keep track of intermediate results
- Show all arithmetic clearly

Detailed solution:""",

        "simple_systematic": f"""Q: {question}

I need to solve this step by step:

1) What am I looking for?
2) What information do I have?
3) What calculations do I need to do?
4) Let me calculate carefully:
5) Final answer:""",

        "double_check": f"""Math Problem: {question}

I'll solve this carefully and double-check my work:

First attempt:
[Step-by-step solution]

Double-check:
[Verify the answer makes sense]

Final Answer:"""
    }
    
    return prompts.get(prompt_type, prompts["enhanced_structure"])

# Test different prompts
if __name__ == "__main__":
    test_question = "Ken created a care package to send to his brother, who was away at boarding school. Ken placed a box on a scale, and then he poured into the box enough jelly beans to bring the weight to 2 pounds. Then, he added enough brownies to cause the weight to triple. Next, he added another 2 pounds of jelly beans. And finally, he added enough gummy worms to double the weight once again. What was the final weight of the box of goodies, in pounds?"
    
    print("=== TESTING DIFFERENT PROMPTS ===\n")
    
    for prompt_type in ["enhanced_structure", "calculation_focused", "self_verification"]:
        print(f"--- {prompt_type.upper()} ---")
        print(get_enhanced_prompt(test_question, prompt_type))
        print("\n" + "="*80 + "\n")
