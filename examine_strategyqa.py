from datasets import load_dataset
import json

# Load StrategyQA dataset to examine its structure
print("🔍 LOADING STRATEGYQA DATASET...")
print("="*50)

try:
    # Try common StrategyQA dataset names
    dataset_names = [
        'ChilleD/StrategyQA',
        'allenai/strategyqa', 
        'StrategyQA',
        'strategy_qa'
    ]
    
    strategyqa_ds = None
    for name in dataset_names:
        try:
            print(f"Trying: {name}")
            strategyqa_ds = load_dataset(name, split="train")
            print(f"✅ SUCCESS: {name} - {len(strategyqa_ds)} samples")
            break
        except Exception as e:
            print(f"❌ Failed: {str(e)[:60]}...")
    
    if strategyqa_ds is None:
        print("🔍 Trying default StrategyQA...")
        strategyqa_ds = load_dataset("allenai/strategyqa", split="train")
    
    print(f"\n📊 STRATEGYQA DATASET ANALYSIS:")
    print(f"Total samples: {len(strategyqa_ds)}")
    print(f"Sample keys: {list(strategyqa_ds[0].keys())}")
    
    # Show first sample
    sample = strategyqa_ds[0]
    print(f"\n🔍 FIRST SAMPLE STRUCTURE:")
    for key, value in sample.items():
        if isinstance(value, str):
            preview = value[:100] + "..." if len(str(value)) > 100 else value
        else:
            preview = str(value)
        print(f"   {key}: {preview}")
    
    # Show a few more samples to understand patterns
    print(f"\n📋 ADDITIONAL SAMPLES:")
    for i in range(1, min(4, len(strategyqa_ds))):
        sample = strategyqa_ds[i]
        print(f"\nSample {i+1}:")
        for key, value in sample.items():
            if isinstance(value, str):
                preview = value[:80] + "..." if len(str(value)) > 80 else value
            else:
                preview = str(value)
            print(f"   {key}: {preview}")
    
except Exception as e:
    print(f"❌ Error loading StrategyQA: {e}")
    print("\n🔍 Let's try to find available StrategyQA datasets...")
    
    # Search for StrategyQA alternatives
    alternatives = [
        "BIG-bench-hard",
        "bigbench", 
        "strategy-qa",
        "commonsense_qa"
    ]
    
    for alt in alternatives:
        try:
            print(f"\nTrying alternative: {alt}")
            ds = load_dataset(alt, split="train")
            if 'strategy' in str(ds[0]).lower():
                print(f"✅ Found strategy-related content in {alt}")
                sample = ds[0]
                print(f"Keys: {list(sample.keys())}")
                break
        except:
            continue
