#!/usr/bin/env python3
"""
Enhanced answer extraction that handles multiple numbers in final sentences.
This addresses cases where the final line has multiple numbers and the algorithm
picks the wrong one (e.g., "earned $10 for 50 minutes" picking 50 instead of 10).
"""

import json
import re
from tqdm import tqdm

def extract_answer_enhanced(cot_text):
    """
    Enhanced extraction logic that better handles multiple numbers in context.
    """
    trace = cot_text
    
    # Method 1: Prioritized pattern matching (NEW APPROACH)
    # Look for highly specific final answer patterns first
    prioritized_patterns = [
        # Dollar amounts (highest priority for money problems)
        r"earned\s*\*\*\$(\d+(?:\.\d{2})?)\*\*",                              # "earned **$10**"
        r"made\s*\*\*\$(\d+(?:\.\d{2})?)\*\*",                                # "made **$100**" 
        r"costs?\s*\*\*\$(\d+(?:\.\d{2})?)\*\*",                              # "costs **$50**"
        r"needs?\s*\*\*\$(\d+(?:\.\d{2})?)\*\*",                              # "needs **$5**"
        r"saves?\s*\*\*\$(\d+(?:\.\d{2})?)\*\*",                              # "saves **$25**"
        
        # Final answer with units (high priority)
        r"\*\*(\d+(?:\.\d{2})?)\s*(?:dollars?|pages?|clips?|flowers?|items?|people|pounds?)\*\*",  # "**42 pages**"
        r"(?:total|altogether|answer).*?\*\*(\d+(?:\.\d{2})?)\*\*",            # "total **72**"
        
        # GSM8K format
        r"####\s*(\d+)",                                                       # "#### 10"
        
        # Final sentence patterns (medium priority)
        r"final answer:?\s*.*?\*\*(\d+(?:\.\d{2})?)\*\*",                     # "final answer: **10**"
        r"answer:?\s*.*?\*\*(\d+(?:\.\d{2})?)\*\*",                           # "answer: **10**"
        r"should (?:read|buy|pay|earn|save).*?\*\*(\d+(?:\.\d{2})?)\*\*",     # "should read **42**"
        
        # Monetary context patterns
        r"\*\*\$(\d+(?:\.\d{2})?)\*\*(?:\s+for|\s+total|\s+altogether|\.?\s*$)",  # "**$10** for" or "**$10**."
    ]
    
    # Try prioritized patterns first
    for pattern in prioritized_patterns:
        match = re.search(pattern, trace, re.IGNORECASE)
        if match:
            extracted = match.group(1).replace(',', '').split('.')[0]
            return extracted
    
    # Method 2: Enhanced last line analysis
    lines = trace.split('\n')
    last_line_number = None
    
    for line in reversed(lines):
        if not line.strip():
            continue
            
        # Look for numbers in the line
        numbers = re.findall(r'(\d+(?:\.\d{2})?)', line)
        if not numbers:
            continue
            
        # ENHANCED CONTEXT-AWARE SELECTION
        if len(numbers) == 1:
            # Only one number, take it
            last_line_number = numbers[0].split('.')[0]
            break
        elif len(numbers) > 1:
            # Multiple numbers - use context to choose the right one
            line_lower = line.lower()
            
            # Priority 1: Look for money context
            money_patterns = [
                (r'(?:earned?|made?|costs?|needs?|saves?|paid?)\s*.*?\$?(\d+(?:\.\d{2})?)', 'money_verb'),
                (r'\$(\d+(?:\.\d{2})?)', 'dollar_sign'),
                (r'(\d+(?:\.\d{2})?)\s*dollars?', 'dollar_word'),
            ]
            
            for money_pattern, context_type in money_patterns:
                money_matches = re.findall(money_pattern, line, re.IGNORECASE)
                if money_matches:
                    last_line_number = money_matches[0].split('.')[0]
                    break
            
            if last_line_number:
                break
                
            # Priority 2: Look for answer-indicating context
            answer_indicators = ['answer', 'total', 'altogether', 'final', 'result']
            if any(indicator in line_lower for indicator in answer_indicators):
                # Find number closest to answer indicators
                best_number = None
                best_distance = float('inf')
                
                for num in numbers:
                    for indicator in answer_indicators:
                        if indicator in line_lower:
                            num_pos = line_lower.find(num)
                            indicator_pos = line_lower.find(indicator)
                            if num_pos != -1 and indicator_pos != -1:
                                distance = abs(num_pos - indicator_pos)
                                if distance < best_distance:
                                    best_distance = distance
                                    best_number = num
                
                if best_number:
                    last_line_number = best_number.split('.')[0]
                    break
            
            # Priority 3: Look for units that indicate the answer type
            unit_patterns = [
                (r'(\d+(?:\.\d{2})?)\s*(?:pages?|clips?|flowers?|items?|people|pounds?|feet|ft\.?)', 'unit_after'),
                (r'(?:pages?|clips?|flowers?|items?|people|pounds?|feet|ft\.?)\s*.*?(\d+(?:\.\d{2})?)', 'unit_before'),
            ]
            
            for unit_pattern, context_type in unit_patterns:
                unit_matches = re.findall(unit_pattern, line, re.IGNORECASE)
                if unit_matches:
                    last_line_number = unit_matches[0].split('.')[0]
                    break
            
            if last_line_number:
                break
            
            # Priority 4: Default to largest number (old behavior)
            clean_numbers = [num.replace(',', '') for num in numbers]
            last_line_number = max(clean_numbers, key=lambda x: int(float(x))).split('.')[0]
            break
    
    # Method 3: Fallback patterns (same as before)
    if not last_line_number:
        fallback_patterns = [
            r"Step 5:.*?final answer.*?\*\*(\d+(?:\.\d{2})?)\*\*",
            r"Give a clear final answer:.*?\*\*(\d+(?:\.\d{2})?)\*\*",
            r"The answer is\s*(\d+(?:\.\d{2})?)",
            r"=\s*(\d+(?:\.\d{2})?)(?:\s*\.|\s*$)",
        ]
        
        for pattern in fallback_patterns:
            match = re.search(pattern, trace, re.IGNORECASE)
            if match:
                last_line_number = match.group(1).split('.')[0]
                break
    
    return last_line_number

def fix_contextual_extraction(input_file, output_file):
    """
    Re-process samples with enhanced context-aware extraction.
    """
    print(f"🔄 Loading data from {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📊 Processing {len(data)} samples with enhanced extraction...")
    
    # Statistics tracking
    stats = {
        'total': len(data),
        'extraction_improved': 0,
        'newly_correct': 0,
        'total_correct_after_fix': 0,
        'originally_correct': 0
    }
    
    # Track specific improvements
    improvements = []
    
    # Process each sample
    for i, sample in enumerate(tqdm(data, desc="Enhanced extraction")):
        original_ans = sample.get('ans', '')
        cot_text = sample.get('cot', '')
        gold_text = sample.get('gold', '')
        
        # Extract gold answer
        gold_match = re.search(r'####\s*(\d+)', gold_text)
        gold_answer = gold_match.group(1) if gold_match else None
        
        # Apply enhanced extraction
        new_ans = extract_answer_enhanced(cot_text)
        
        if new_ans is None:
            new_ans = original_ans
        
        # Check if extraction improved
        was_originally_correct = str(original_ans) == str(gold_answer) if gold_answer else False
        is_now_correct = str(new_ans) == str(gold_answer) if gold_answer else False
        
        if new_ans != original_ans:
            stats['extraction_improved'] += 1
            improvements.append({
                'index': i,
                'question': sample['question'][:60] + "...",
                'original_ans': original_ans,
                'new_ans': new_ans,
                'gold': gold_answer,
                'improvement': not was_originally_correct and is_now_correct
            })
        
        # Update sample
        sample['ans'] = new_ans
        sample['is_correct'] = is_now_correct
        
        # Update stats
        if was_originally_correct:
            stats['originally_correct'] += 1
        if is_now_correct:
            stats['total_correct_after_fix'] += 1
            if not was_originally_correct:
                stats['newly_correct'] += 1
    
    # Save enhanced data
    print(f"💾 Saving enhanced data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Generate report
    print("\n" + "="*60)
    print("📊 ENHANCED EXTRACTION REPORT")
    print("="*60)
    
    print(f"📈 Total samples processed: {stats['total']}")
    print(f"🔧 Extractions changed: {stats['extraction_improved']}")
    print(f"✅ Originally correct: {stats['originally_correct']} ({stats['originally_correct']/stats['total']*100:.1f}%)")
    print(f"🎯 Newly correct: {stats['newly_correct']}")
    print(f"🏆 Total correct after fix: {stats['total_correct_after_fix']} ({stats['total_correct_after_fix']/stats['total']*100:.1f}%)")
    
    accuracy_improvement = stats['total_correct_after_fix'] - stats['originally_correct']
    print(f"📈 Net accuracy improvement: +{accuracy_improvement} samples (+{accuracy_improvement/stats['total']*100:.1f}%)")
    
    # Show improvements
    actual_improvements = [imp for imp in improvements if imp['improvement']]
    if actual_improvements:
        print(f"\n🎯 ACTUAL IMPROVEMENTS (showing first 10):")
        print("-" * 80)
        for imp in actual_improvements[:10]:
            print(f"Sample {imp['index']}: {imp['question']}")
            print(f"  ❌ Old: {imp['original_ans']} → ✅ New: {imp['new_ans']} (Gold: {imp['gold']})")
            print()
    
    # Show examples of changes (including regressions)
    if improvements:
        print(f"\n📋 ALL CHANGES (showing first 10):")
        print("-" * 80)
        for imp in improvements[:10]:
            status = "✅ IMPROVED" if imp['improvement'] else "⚠️ CHANGED"
            print(f"{status} - Sample {imp['index']}: {imp['question']}")
            print(f"  Old: {imp['original_ans']} → New: {imp['new_ans']} (Gold: {imp['gold']})")
            print()
    
    print("="*60)
    print(f"✅ Complete! Enhanced data saved to: {output_file}")
    
    return stats, improvements

if __name__ == "__main__":
    input_file = "cot_improved_gsm8k_final_2000_fixed.json"
    output_file = "cot_improved_gsm8k_final_2000_enhanced.json"
    
    stats, improvements = fix_contextual_extraction(input_file, output_file)
