import re
import json

def extract_from_final_answer_section(cot_text):
    """
    Extract number from the '5. Give a clear final answer:' section specifically
    """
    
    # Strategy 1: Look for section 5 specifically
    section_5_patterns = [
        r"\*\*5\.\s*Give a clear final answer:\*\*.*?(\d+)",              # "**5. Give a clear final answer:** Mark has **35** flowers"
        r"5\.\s*Give a clear final answer:.*?(\d+)",                     # Without bold formatting
        r"Give a clear final answer:.*?(\d+)",                           # Just the header
    ]
    
    # Strategy 2: Look for emphasized numbers after final answer section
    final_section_patterns = [
        r"Give a clear final answer:.*?\*\*(\d+)\*\*",                   # "**35**" after final answer
        r"final answer:.*?\*\*(\d+)\*\*",                               # Case variations
        r"Give a clear final answer:.*?(\d+)\s*(?:flowers?|pages?|pounds?|dollars?|pieces?)", # "35 flowers"
    ]
    
    # Try section-specific patterns first
    for pattern in section_5_patterns + final_section_patterns:
        matches = re.findall(pattern, cot_text, re.IGNORECASE | re.DOTALL)
        if matches:
            result = matches[-1]  # Take last match
            print(f"✅ Found '{result}' in final answer section using: {pattern}")
            return result
    
    print("❌ No final answer section patterns matched")
    return None

# Test on a few examples from the JSON
def test_final_answer_extraction():
    with open('cot_improved_10.json', 'r') as f:
        data = json.load(f)
    
    print("=== TESTING FINAL ANSWER SECTION EXTRACTION ===\n")
    
    # Test on problematic cases
    test_cases = [5, 2, 8]  # Mark's garden, Weng, Ken's package
    
    for idx in test_cases:
        item = data[idx]
        gold_parts = item['gold'].split('#### ')
        correct_answer = gold_parts[1].strip() if len(gold_parts) > 1 else "unknown"
        
        print(f"Problem {idx+1}: {item['question'][:60]}...")
        print(f"Expected: {correct_answer}")
        print(f"Current wrong extraction: {item['ans']}")
        
        # Show the final answer section
        cot_lines = item['cot'].split('\n')
        final_section_found = False
        for i, line in enumerate(cot_lines):
            if "Give a clear final answer" in line:
                print("Final answer section:")
                for j in range(max(0, i), min(len(cot_lines), i+3)):
                    print(f"  {cot_lines[j]}")
                final_section_found = True
                break
        
        if not final_section_found:
            print("❌ No 'Give a clear final answer' section found!")
        
        # Test extraction
        new_extraction = extract_from_final_answer_section(item['cot'])
        
        if new_extraction == correct_answer:
            print(f"🎉 SUCCESS! Extracted: {new_extraction}")
        else:
            print(f"⚠️ Still incorrect: {new_extraction}")
            
        print("-" * 80)

if __name__ == "__main__":
    test_final_answer_extraction()
