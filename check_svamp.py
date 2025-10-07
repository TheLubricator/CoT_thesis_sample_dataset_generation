import json

# Check SVAMP file
with open('cot_svamp_final_700.json', 'r') as f:
    data = json.load(f)

print(f'📊 SVAMP file contains {len(data)} samples')
if data:
    sample = data[0]
    print(f'🔍 Sample keys: {list(sample.keys())}')
    print(f'📝 Sample type: {sample.get("type", "N/A")}')
    print(f'🎯 Sample answer: {sample.get("ans", "N/A")}')
    print(f'🥇 Gold answer: {sample.get("gold", "N/A")}')
    print(f'✅ Ready for extraction fix!')
