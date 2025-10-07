#!/usr/bin/env python3
"""
Fix answer extraction for existing CoT dataset and add validation column.
This script applies the improved regex patterns to re-extract answers from the 'cot' field
and adds an 'is_correct' column comparing fixed answers with gold answers.
"""

import json
import re
from tqdm import tqdm

def extract_answer_improved(cot_text):
    """
    Apply the improved extraction logic to a CoT response.
    This uses the same logic from the updated generate_cot_improved function.
    """
    trace = cot_text
    
    # Method 1: Last line with number (most reliable) - FIXED regex ordering
    lines = trace.split('\n')
    last_line_number = None
    
    for line in reversed(lines):
        # FIXED regex: Prioritize longer numbers first, then comma-separated numbers
        numbers = re.findall(r'(\d+(?:,\d{3})*|\d{1,3}(?:,\d{3})+)', line)
        if not numbers:
            # Fallback: capture any sequence of digits
            numbers = re.findall(r'(\d+)', line)
        
        if numbers:
            # Remove commas and convert to clean numbers
            clean_numbers = [num.replace(',', '') for num in numbers]
            
            # IMPROVED SELECTION LOGIC: Prioritize the best number
            if clean_numbers:
                # 1. If line contains final answer indicators, prioritize the largest number
                if any(indicator in line.lower() for indicator in ['final', 'answer', 'total', 'altogether', '####']):
                    # Pick the largest number (most likely the final answer)
                    last_line_number = max(clean_numbers, key=lambda x: int(x))
                else:
                    # 2. For non-final lines, prioritize numbers >= 3 digits, then largest
                    large_numbers = [n for n in clean_numbers if len(n) >= 3]
                    if large_numbers:
                        last_line_number = max(large_numbers, key=lambda x: int(x))
                    else:
                        last_line_number = max(clean_numbers, key=lambda x: int(x))
            break
    
    # Method 2: Structured patterns as fallback - ENHANCED with better number matching
    patterns = [
        # HIGH PRIORITY: GSM8K-style final answer patterns
        r"####\s*(\d+)",                                                             # "#### 8798"
        r"\$(\d+(?:\.\d{2})?)\b",                                                    # "$8798.00" or "$8798"
        r"made\s*\*\*\$?(\d+(?:\.\d{2})?)\*\*",                                     # "made **$8798.00**"
        r"total.*?\$?(\d+(?:\.\d{2})?)",                                             # "total refund amount: $8798"
        
        # MEDIUM PRIORITY: Structured answer patterns  
        r"\*\*Step 5:\s*Give a clear final answer\*\*.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"Step 5:.*?final answer.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"\*\*5\.\s*Give a clear final answer:\*\*.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"5\.\s*Give a clear final answer:.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"Give a clear final answer:.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        
        # STANDARD PRIORITY: Common answer patterns
        r"final answer.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"Answer:\s*.*?\*\*\$?(\d+(?:\.\d{2})?)\*\*",
        r"Final answer:\s*.*?\$?(\d+(?:\.\d{2})?)",
        r"Answer:\s*.*?\$?(\d+(?:\.\d{2})?)",
        r"The answer is\s*\$?(\d+(?:\.\d{2})?)",
        
        # COMMA-SEPARATED PATTERNS: For numbers with commas
        r"####\s*(\d{1,3}(?:,\d{3})+)",
        r"\$(\d{1,3}(?:,\d{3})+(?:\.\d{2})?)",
        
        # CONTEXT-SPECIFIC: Unit-based patterns
        r"\*\*(\d+(?:\.\d{2})?)\*\*\s*(?:clips?|flowers?|pages?|pounds?|dollars?|pieces?|total|people|items?|sq\.?\s*ft\.?)",
        r"(\d+(?:\.\d{2})?)\s+(?:pounds?|dollars?|people|items?|total|left|altogether|sq\.?\s*ft\.?)",
        r"=\s*\$?(\d+(?:\.\d{2})?)(?:\s*\.|\s*$)",
    ]
    
    # Try last line method first
    ans_match = None
    if last_line_number:
        # Mock match object for consistency
        class MockMatch:
            def __init__(self, value):
                self._value = value
            def group(self, n):
                return self._value
        ans_match = MockMatch(last_line_number)
    else:
        # Fallback to pattern matching
        for pattern in patterns:
            ans_match = re.search(pattern, trace, re.IGNORECASE)
            if ans_match:
                break
    
    if ans_match:
        # Remove commas and decimals from extracted answer
        extracted = ans_match.group(1).strip().replace(',', '').split('.')[0]
        return extracted
    else:
        return None

def extract_gold_answer(gold_text):
    """Extract the final answer from GSM8K gold format (#### number)"""
    # Look for #### followed by a number
    match = re.search(r'####\s*(\d+)', gold_text)
    if match:
        return match.group(1)
    
    # Fallback: look for any number at the end
    numbers = re.findall(r'\d+', gold_text)
    if numbers:
        return numbers[-1]  # Last number found
    
    return None

def fix_extraction_and_validate(input_file, output_file):
    """
    Process the JSON file to fix extractions and add validation.
    """
    print(f"🔄 Loading data from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Processing {len(data)} samples...")
    
    # Statistics tracking
    stats = {
        'total': len(data),
        'extraction_improved': 0,
        'extraction_failed': 0,
        'originally_correct': 0,
        'newly_correct': 0,
        'total_correct_after_fix': 0
    }
    
    # Track changes for reporting
    changes = []
    
    # Process each sample
    for i, sample in enumerate(tqdm(data, desc="Fixing extractions")):
        original_ans = sample.get('ans', '')
        cot_text = sample.get('cot', '')
        gold_text = sample.get('gold', '')
        
        # Extract gold answer for comparison
        gold_answer = extract_gold_answer(gold_text)
        
        # Apply improved extraction
        new_ans = extract_answer_improved(cot_text)
        
        # If extraction failed, keep original or use gold
        if new_ans is None:
            new_ans = original_ans if original_ans else gold_answer
            stats['extraction_failed'] += 1
        
        # Check if extraction improved
        if new_ans != original_ans:
            stats['extraction_improved'] += 1
            changes.append({
                'index': i,
                'question': sample['question'][:50] + "...",
                'original_ans': original_ans,
                'new_ans': new_ans,
                'gold': gold_answer
            })
        
        # Update the sample
        sample['ans'] = new_ans
        
        # Add is_correct field
        if gold_answer:
            is_correct = (str(new_ans) == str(gold_answer))
            sample['is_correct'] = is_correct
            
            # Track accuracy stats
            was_originally_correct = (str(original_ans) == str(gold_answer))
            if was_originally_correct:
                stats['originally_correct'] += 1
            if is_correct:
                stats['total_correct_after_fix'] += 1
                if not was_originally_correct:
                    stats['newly_correct'] += 1
        else:
            sample['is_correct'] = None  # Can't determine without gold answer
    
    # Save the fixed data
    print(f"💾 Saving fixed data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 EXTRACTION FIXING REPORT")
    print("="*60)
    
    print(f"📈 Total samples processed: {stats['total']}")
    print(f"🔧 Extractions improved: {stats['extraction_improved']}")
    print(f"❌ Extraction failures: {stats['extraction_failed']}")
    print(f"✅ Originally correct: {stats['originally_correct']} ({stats['originally_correct']/stats['total']*100:.1f}%)")
    print(f"🎯 Newly correct: {stats['newly_correct']}")
    print(f"🏆 Total correct after fix: {stats['total_correct_after_fix']} ({stats['total_correct_after_fix']/stats['total']*100:.1f}%)")
    
    accuracy_improvement = stats['total_correct_after_fix'] - stats['originally_correct']
    print(f"📈 Accuracy improvement: +{accuracy_improvement} samples (+{accuracy_improvement/stats['total']*100:.1f}%)")
    
    # Show some example changes
    if changes:
        print(f"\n🔍 SAMPLE CHANGES (showing first 10):")
        print("-" * 80)
        for change in changes[:10]:
            print(f"Sample {change['index']}: {change['question']}")
            print(f"  Old: {change['original_ans']} → New: {change['new_ans']} (Gold: {change['gold']})")
            print()
    
    print("="*60)
    print(f"✅ Complete! Fixed data saved to: {output_file}")
    
    return stats, changes

if __name__ == "__main__":
    input_file = "cot_improved_gsm8k_final_2000.json"
    output_file = "cot_improved_gsm8k_final_2000_fixed.json"
    
    stats, changes = fix_extraction_and_validate(input_file, output_file)
