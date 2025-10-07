import json

def create_strategyqa_cot_prompt(sample, prompt_type="comprehensive"):
    """
    Create optimal prompt for StrategyQA CoT generation
    """
    
    if prompt_type == "comprehensive":
        # RECOMMENDED: Include all context for best reasoning
        prompt = f"""Please solve this yes/no question step by step with clear reasoning.

**Context:**
Term: {sample['term']}
Description: {sample['description']}

**Supporting Facts:**
{sample['facts']}

**Question:** {sample['question']}

Please provide a step-by-step chain-of-thought analysis and conclude with a clear yes/no answer."""

    elif prompt_type == "question_focused":
        # Alternative: Focus mainly on question + facts
        prompt = f"""Please solve this yes/no question step by step with clear reasoning.

**Background:** {sample['term']} - {sample['description']}

**Key Facts:**
{sample['facts']}

**Question:** {sample['question']}

Please analyze this step by step and provide a clear yes/no answer."""

    elif prompt_type == "minimal":
        # Minimal: Just question + facts (not recommended)
        prompt = f"""Please solve this step by step:

**Question:** {sample['question']}

**Relevant Facts:**
{sample['facts']}

Provide step-by-step reasoning and a clear yes/no answer."""

    elif prompt_type == "question_only":
        # Question only (definitely not recommended)
        prompt = f"""Please solve this step by step:

**Question:** {sample['question']}

Provide step-by-step reasoning and a clear yes/no answer."""

    return prompt

# Example usage with the first sample
sample_data = {
    'qid': '4fd64bb6ce5b78ab20b6',
    'term': 'Mixed martial arts',
    'description': 'full contact combat sport',
    'question': 'Is Mixed martial arts totally original from Roman Colosseum games?',
    'answer': False,
    'facts': 'Mixed Martial arts in the UFC takes place in an enclosed structure called The Octagon. The Roman Colosseum was an enclosed structure where gladiators would fight.'
}

print("📋 STRATEGYQA PROMPT STRATEGIES:")
print("="*60)

strategies = ["comprehensive", "question_focused", "minimal", "question_only"]

for strategy in strategies:
    print(f"\n🎯 {strategy.upper()} STRATEGY:")
    print("-" * 40)
    prompt = create_strategyqa_cot_prompt(sample_data, strategy)
    print(prompt)
    print()

print("💡 RECOMMENDATIONS:")
print("="*60)
print("✅ BEST: 'comprehensive' - Includes term, description, facts, and question")
print("   → Gives model full context for accurate reasoning")
print("   → Similar to how humans would approach the problem")
print()
print("⚠️  AVOID: 'question_only' - Model lacks crucial context")
print("   → StrategyQA questions often require external knowledge")
print("   → Facts column provides necessary background information")
print()
print("🎯 DECOMPOSITION COLUMN:")
print("   → You mentioned 'decomposition' but it's not in this dataset")
print("   → The 'facts' column serves as the supporting evidence")
print("   → If you have decomposition hints, include them as additional context")

# Test what information each strategy provides
print("\n📊 INFORMATION CONTENT ANALYSIS:")
print("-" * 40)
for strategy in strategies:
    prompt = create_strategyqa_cot_prompt(sample_data, strategy)
    word_count = len(prompt.split())
    has_term = 'term' in prompt.lower() or 'mixed martial arts' in prompt
    has_description = 'description' in prompt.lower() or 'full contact combat sport' in prompt
    has_facts = 'facts' in prompt.lower() or 'colosseum' in prompt.lower()
    
    print(f"{strategy:15} | Words: {word_count:3d} | Term: {'✓' if has_term else '✗'} | Desc: {'✓' if has_description else '✗'} | Facts: {'✓' if has_facts else '✗'}")
