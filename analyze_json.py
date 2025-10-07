import json

with open('cot_improved_10.json', 'r') as f:
    data = json.load(f)

# Analyze the data
total = len(data)
correct = 0
wrong = 0
extraction_issues = 0

print("=== ANALYSIS OF 100 CoT SAMPLES ===\n")

# Check accuracy
for i, item in enumerate(data):
    # Extract the final answer from gold (after ####)
    gold_parts = item['gold'].split('#### ')
    if len(gold_parts) > 1:
        gold_final = gold_parts[1].strip()
    else:
        gold_final = "unknown"
    
    # Compare predicted vs correct
    if item['ans'] == gold_final:
        correct += 1
    else:
        wrong += 1
        if wrong <= 5:  # Show first 5 errors
            print(f"ERROR #{wrong}:")
            print(f"Question: {item['question'][:70]}...")
            print(f"Model predicted: '{item['ans']}'")
            print(f"Correct answer: '{gold_final}'")
            print(f"CoT quality: {'Good' if len(item['cot']) > 200 else 'Short'}")
            print()

print(f"SUMMARY:")
print(f"Total samples: {total}")
print(f"Correct predictions: {correct}")
print(f"Wrong predictions: {wrong}")
print(f"Accuracy: {correct/total*100:.1f}%")

# Analyze CoT quality
avg_cot_length = sum(len(item['cot']) for item in data) / len(data)
print(f"Average CoT length: {avg_cot_length:.0f} characters")

# Check for extraction patterns
has_answer_pattern = sum(1 for item in data if 'Answer:' in item['cot'])
print(f"CoTs with 'Answer:' pattern: {has_answer_pattern}/100")
