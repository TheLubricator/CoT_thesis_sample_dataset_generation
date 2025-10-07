# SVAMP HYBRID EXTRACTION FIX SCRIPT
# Adapted from GSM8K approach but customized for SVAMP dataset characteristics

import json
import re
import time
import os

def fix_svamp_extraction(input_file, output_file):
    """
    SVAMP-specific extraction fixing with context awareness and problem-type handling
    """
    
    print("🔧 SVAMP HYBRID EXTRACTION FIX")
    print("="*50)
    print(f"📂 Input:  {input_file}")
    print(f"📂 Output: {output_file}")
    
    # Load SVAMP CoT dataset
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded {len(data)} SVAMP samples")
    except Exception as e:
        print(f"❌ Error loading {input_file}: {e}")
        return
    
    # Initialize tracking
    fixed_count = 0
    svamp_method_stats = {
        "high_confidence": 0, 
        "context_filtered": 0, 
        "problem_type_aware": 0, 
        "svamp_specific": 0,
        "robust_fallback": 0
    }
    
    print("🔍 Processing samples...")
    start_time = time.time()
    
    for i, entry in enumerate(data):
        original_ans = entry['ans']
        cot = entry['cot']
        problem_type = entry.get('type', 'Unknown')
        body = entry.get('body', '')
        question = entry.get('question', '')
        gold_answer = entry['gold']
        
        # Extract original problem numbers to avoid contamination
        problem_numbers = set()
        if body:
            problem_numbers.update(re.findall(r'\d+', body))
        
        new_ans = None
        method_used = None
        
        # Method 1: SVAMP High-Confidence Patterns
        high_confidence_patterns = [
            r"final answer.*?(?:is|:)\s*(\d+)",
            r"answer.*?(?:is|:)\s*(\d+)",
            r"(?:the|my)?\s*answer\s*(?:is|:)?\s*(\d+)",
            r"each group.*?(?:has|contains|is)\s*(\d+)",
            r"(\d+).*?(?:in each|per group|each group)",
            r"(?:size|big).*?(?:is|:)\s*(\d+)",
            r"each.*?(?:group|item|piece).*?(?:is|has|contains)\s*(\d+)",
            r"therefore.*?(\d+)",
            r"so.*?(?:the answer is|answer:)\s*(\d+)",
            r"result.*?(?:is|:)\s*(\d+)",
        ]
        
        for pattern in high_confidence_patterns:
            match = re.search(pattern, cot, re.IGNORECASE)
            if match:
                candidate = match.group(1)
                if candidate not in problem_numbers or len(candidate) >= 3:
                    new_ans = candidate
                    method_used = "high_confidence"
                    break
        
        # Method 2: Problem-Type Aware Extraction
        if not new_ans and problem_type != 'Unknown':
            if problem_type == "Common-Division":
                div_patterns = [
                    r'(\d+)\s*/\s*(\d+)\s*=\s*(\d+)',
                    r'(\d+)\s*÷\s*(\d+)\s*=\s*(\d+)',
                    r'divide.*?(\d+).*?by.*?(\d+).*?(?:is|=)\s*(\d+)',
                    r'(\d+)\s*divided by\s*(\d+)\s*(?:is|=)\s*(\d+)'
                ]
                for pattern in div_patterns:
                    match = re.search(pattern, cot, re.IGNORECASE)
                    if match:
                        result = match.group(3)
                        if result not in problem_numbers:
                            new_ans = result
                            method_used = "problem_type_aware"
                            break
            
            elif problem_type == "Addition":
                add_patterns = [
                    r'(\d+)\s*\+\s*(\d+)\s*=\s*(\d+)',
                    r'total.*?(?:is|=)\s*(\d+)',
                    r'sum.*?(?:is|=)\s*(\d+)',
                    r'altogether.*?(\d+)'
                ]
                for pattern in add_patterns:
                    match = re.search(pattern, cot, re.IGNORECASE)
                    if match:
                        if len(match.groups()) == 3:
                            result = match.group(3)
                        else:
                            result = match.group(1)
                        if result not in problem_numbers:
                            new_ans = result
                            method_used = "problem_type_aware"
                            break
            
            elif problem_type == "Subtraction":
                sub_patterns = [
                    r'(\d+)\s*-\s*(\d+)\s*=\s*(\d+)',
                    r'(\d+)\s*−\s*(\d+)\s*=\s*(\d+)',
                    r'(?:left|remaining|difference).*?(?:is|=)\s*(\d+)',
                    r'subtract.*?(\d+).*?from.*?(\d+).*?(?:is|=)\s*(\d+)'
                ]
                for pattern in sub_patterns:
                    match = re.search(pattern, cot, re.IGNORECASE)
                    if match:
                        if len(match.groups()) == 3:
                            result = match.group(3)
                        else:
                            result = match.group(1)
                        if result not in problem_numbers:
                            new_ans = result
                            method_used = "problem_type_aware"
                            break
        
        # Method 3: SVAMP-Specific Context Filtering
        if not new_ans:
            lines = cot.split('\n')
            for line in reversed(lines[-5:]):
                if any(keyword in line.lower() for keyword in ['answer', 'final', 'result', 'therefore', 'so']):
                    numbers = re.findall(r'(\d+)', line)
                    for num in numbers:
                        if num not in problem_numbers or (len(num) >= 3 and int(num) > 100):
                            new_ans = num
                            method_used = "svamp_specific"
                            break
                    if new_ans:
                        break
        
        # Method 4: Context-Filtered Last Line Approach
        if not new_ans:
            lines = cot.split('\n')
            for line in reversed(lines[-3:]):
                numbers = re.findall(r'(\d+)', line)
                if numbers:
                    filtered_numbers = [n for n in numbers if n not in problem_numbers]
                    if filtered_numbers:
                        new_ans = max(filtered_numbers, key=lambda x: int(x))
                        method_used = "context_filtered"
                    else:
                        large_numbers = [n for n in numbers if len(n) >= 3]
                        if large_numbers:
                            new_ans = max(large_numbers, key=lambda x: int(x))
                            method_used = "context_filtered"
                    break
        
        # Method 5: Robust Fallback (GSM8K proven method)
        if not new_ans:
            lines = cot.split('\n')
            for line in reversed(lines):
                numbers = re.findall(r'(\d+(?:,\d{3})*|\d{1,3}(?:,\d{3})+)', line)
                if not numbers:
                    numbers = re.findall(r'(\d+)', line)
                
                if numbers:
                    clean_numbers = [num.replace(',', '') for num in numbers]
                    if clean_numbers:
                        if any(indicator in line.lower() for indicator in ['final', 'answer', 'total', 'altogether']):
                            new_ans = max(clean_numbers, key=lambda x: int(x))
                        else:
                            large_numbers = [n for n in clean_numbers if len(n) >= 3]
                            new_ans = max(large_numbers, key=lambda x: int(x)) if large_numbers else max(clean_numbers, key=lambda x: int(x))
                        method_used = "robust_fallback"
                        break
        
        # Apply fix if we found a different answer
        if new_ans and new_ans != original_ans:
            entry['ans'] = new_ans
            fixed_count += 1
        
        # Track method statistics
        if method_used:
            svamp_method_stats[method_used] += 1
        
        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{len(data)} samples...")
    
    # Add is_correct validation column
    print("✅ Adding validation column...")
    for entry in data:
        entry['is_correct'] = (entry['ans'] == entry['gold'])
    
    # Save fixed data
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return
    
    # Calculate and display results
    correct_count = sum(1 for entry in data if entry['is_correct'])
    accuracy = correct_count / len(data) * 100
    method_percentages = {k: (v / len(data) * 100) for k, v in svamp_method_stats.items()}
    
    elapsed_time = time.time() - start_time
    
    print(f"\n📊 SVAMP EXTRACTION FIX RESULTS:")
    print(f"   Total samples: {len(data)}")
    print(f"   Fixed samples: {fixed_count}")
    print(f"   Accuracy: {accuracy:.1f}% ({correct_count}/{len(data)})")
    print(f"   Processing time: {elapsed_time:.1f} seconds")
    
    print(f"\n🔧 METHOD BREAKDOWN:")
    for method, count in svamp_method_stats.items():
        pct = method_percentages[method]
        print(f"   {method}: {count} samples ({pct:.1f}%)")
    
    print(f"\n✅ SVAMP extraction fix complete!")
    return data

if __name__ == "__main__":
    input_file = "cot_svamp_final_700.json"
    output_file = "cot_svamp_final_700_fixed.json"
    
    print(f"🔍 Checking for input file: {input_file}")
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print(f"\n📁 Available SVAMP files:")
        for file in os.listdir('.'):
            if file.endswith('.json') and 'svamp' in file.lower():
                print(f"   📄 {file}")
    else:
        print(f"🚀 Starting SVAMP extraction fix...")
        fix_svamp_extraction(input_file, output_file)
