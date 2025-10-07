import json
import re

# Load the SVAMP fixed data to analyze errors
with open('cot_svamp_final_700_fixed.json', 'r') as f:
    data = json.load(f)

print('🔍 SVAMP ERROR ANALYSIS: CoT vs Extraction Issues')
print('='*60)

# Analyze incorrect samples
incorrect_samples = [entry for entry in data if not entry['is_correct']]
correct_samples = [entry for entry in data if entry['is_correct']]

print(f'📊 BASIC STATS:')
print(f'   Total: {len(data)}')
print(f'   Correct: {len(correct_samples)} ({len(correct_samples)/len(data)*100:.1f}%)')
print(f'   Incorrect: {len(incorrect_samples)} ({len(incorrect_samples)/len(data)*100:.1f}%)')

# Sample analysis of incorrect answers
print(f'\n🔍 ANALYZING FIRST 10 INCORRECT SAMPLES:')
print('-'*60)

for i, entry in enumerate(incorrect_samples[:10]):
    print(f'\n❌ SAMPLE {i+1}:')
    print(f'   ID: {entry["id"]}')
    print(f'   Type: {entry["type"]}')
    print(f'   Body: {entry["body"][:80]}...')
    print(f'   Question: {entry["question"]}')
    print(f'   Gold Answer: {entry["gold"]}')
    print(f'   Extracted Answer: {entry["ans"]}')
    
    # Check if the gold answer appears in the CoT
    cot = entry['cot']
    gold_in_cot = entry['gold'] in cot
    extracted_in_cot = entry['ans'] in cot
    
    print(f'   Gold in CoT: {"✅" if gold_in_cot else "❌"} ({entry["gold"]})')
    print(f'   Extracted in CoT: {"✅" if extracted_in_cot else "❌"} ({entry["ans"]})')
    
    # Look for calculation patterns
    if entry['type'] == 'Common-Division':
        # Look for division in CoT
        div_pattern = r'(\d+)\s*[/÷]\s*(\d+)\s*=\s*(\d+)'
        div_matches = re.findall(div_pattern, cot)
        if div_matches:
            print(f'   Division found: {div_matches}')
            # Check if any division result matches gold
            for match in div_matches:
                if match[2] == entry['gold']:
                    print(f'   🎯 EXTRACTION ERROR: Correct calculation {match[0]}÷{match[1]}={match[2]} found but not extracted!')
    
    # Show last few lines of CoT to see final reasoning
    lines = cot.split('\n')
    relevant_lines = [line.strip() for line in lines[-3:] if line.strip()]
    print(f'   Last CoT lines:')
    for line in relevant_lines:
        print(f'      "{line[:100]}..."')

print(f'\n📈 SUMMARY ANALYSIS:')

# Count how many have gold answer in CoT
gold_in_cot_count = sum(1 for entry in incorrect_samples if entry['gold'] in entry['cot'])
extraction_errors = gold_in_cot_count
reasoning_errors = len(incorrect_samples) - gold_in_cot_count

print(f'   🎯 Likely EXTRACTION errors: {extraction_errors} ({extraction_errors/len(incorrect_samples)*100:.1f}%)')
print(f'   🤖 Likely MODEL/CoT errors: {reasoning_errors} ({reasoning_errors/len(incorrect_samples)*100:.1f}%)')

print(f'\n💡 NEXT STEPS:')
if extraction_errors > reasoning_errors:
    print('   ⚠️  EXTRACTION is the main issue - need better patterns!')
else:
    print('   ⚠️  MODEL REASONING is the main issue - need better prompts!')
