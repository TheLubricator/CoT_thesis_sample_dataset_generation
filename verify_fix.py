import json

# Load the newly regenerated data
with open("cot_improved_gsm8k_final_2000_enhanced.json", "r") as f:
    data = json.load(f)

print("VERIFICATION OF UPDATED DATASET:")
print("="*60)

for i, entry in enumerate(data[:]):  # Check first 3 entries
    print(f"\nEntry {i+1}:")
    print(f"Question: {entry['question'][:80]}...")
    print(f"Extracted answer: {entry['ans']}")
    
    # Extract the correct answer from gold (format: "#### NUMBER")
    gold_number = entry['gold'].split('#### ')[-1] if '#### ' in entry['gold'] else "Unknown"
    print(f"Gold answer: {gold_number}")
    
    if entry['ans'] == gold_number:
        print(f"✅ CORRECT extraction!")
    else:
        print(f"❌ Wrong extraction - should be {gold_number}")

print("\n" + "="*60)
print("SUMMARY:")
correct_count = 0
for entry in data:
    gold_number = entry['gold'].split('#### ')[-1] if '#### ' in entry['gold'] else "Unknown"
    if entry['ans'] == gold_number:
        correct_count += 1

print(f"Correct extractions: {correct_count}/{len(data)} ({correct_count/len(data)*100:.1f}%)")

if correct_count == len(data):
    print("🎉 ALL EXTRACTIONS ARE NOW CORRECT!")
else:
    print(f"❌ Still have {len(data) - correct_count} incorrect extractions")
