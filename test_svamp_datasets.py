from datasets import load_dataset
import traceback

# Test common SVAMP dataset names
dataset_names = [
    'ChilleD/SVAMP',           # Already using this one
    'arkilpatel/SVAMP',        # Author's name from original paper  
    'allenai/svamp',           # AllenAI institute
    'facebook/svamp',          # Facebook/Meta
    'SVAMP',                   # Simple name
    'svamp'                    # Lowercase
]

print('🔍 TESTING SVAMP DATASET SOURCES:')
print('='*50)

working_datasets = []

for name in dataset_names:
    try:
        print(f'\nTesting: {name}')
        ds = load_dataset(name, split='train')
        print(f'✅ SUCCESS: {len(ds)} samples')
        
        # Show sample structure
        sample = ds[0]
        print(f'   Sample keys: {list(sample.keys())}')
        if 'Question' in sample:
            print(f'   Question preview: {sample["Question"][:60]}...')
        elif 'question' in sample:
            print(f'   Question preview: {sample["question"][:60]}...')
        
        working_datasets.append((name, len(ds)))
        
    except Exception as e:
        print(f'❌ FAILED: {str(e)[:80]}...')

print(f'\n📊 WORKING DATASETS FOUND:')
for name, size in working_datasets:
    print(f'   • {name}: {size} samples')

# Also check the original paper info
print(f'\n📄 SVAMP ORIGINAL PAPER INFO:')
print('   Title: "Are NLP Models really able to Solve Simple Math Word Problems?"')
print('   Authors: Arkil Patel, Satwik Bhattamishra, Navin Goyal')
print('   Paper: https://arxiv.org/abs/2103.07191')
print('   Official Repo: https://github.com/arkilpatel/SVAMP')
