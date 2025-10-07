import json
import re

# Load the improved JSON data
with open('cot_improved_10.json', 'r') as f:
    data = json.load(f)

print("=== ANALYZING ALL EXTRACTION ERRORS ===\n")

# Current patterns used in the function
current_patterns = [
    r"Final answer:\s*.*?(\d+)",
    r"Answer:\s*.*?(\d+)",
    r"The answer is\s*(\d+)",
    r"(\d+)\s+(?:pounds?|dollars?|people|items?|total|left|altogether)",
    r"=\s*(\d+)(?:\s|$)",
    r"\*\*(\d+)\*\*",
]

errors_found = []

for i, item in enumerate(data):
    # Extract correct answer from gold
    gold_parts = item['gold'].split('#### ')
    correct_answer = gold_parts[1].strip() if len(gold_parts) > 1 else "unknown"
    
    extracted_answer = item['ans']
    
    if extracted_answer != correct_answer:
        print(f"❌ ERROR #{i+1}:")
        print(f"Question: {item['question'][:60]}...")
        print(f"Correct: {correct_answer}")
        print(f"Extracted: {extracted_answer}")
        
        # Test current patterns on this CoT
        print("\nTesting current patterns:")
        for j, pattern in enumerate(current_patterns):
            matches = re.findall(pattern, item['cot'], re.IGNORECASE)
            if matches:
                print(f"  Pattern {j+1}: {pattern} → {matches}")
                if matches[0] == extracted_answer:
                    print(f"    ⚠️ This pattern caused the wrong extraction!")
                break
        
        # Look for the correct answer in the CoT
        print(f"\nLooking for correct answer '{correct_answer}' in CoT:")
        if correct_answer in item['cot']:
            print(f"  ✅ '{correct_answer}' found in CoT text")
            # Find contexts where correct answer appears
            lines = item['cot'].split('\n')
            for line_num, line in enumerate(lines):
                if correct_answer in line:
                    print(f"    Line {line_num}: {line.strip()}")
        else:
            print(f"  ❌ '{correct_answer}' NOT found in CoT text")
        
        errors_found.append({
            'index': i,
            'question': item['question'][:50],
            'correct': correct_answer,
            'extracted': extracted_answer,
            'cot_snippet': item['cot'][-200:]  # Last 200 chars
        })
        
        print("\n" + "="*80 + "\n")

print(f"SUMMARY: Found {len(errors_found)} extraction errors out of 10 problems")

# Analyze patterns in the errors
print("\nERROR PATTERNS:")
for error in errors_found:
    print(f"- {error['question']}... → Got '{error['extracted']}' instead of '{error['correct']}'")
