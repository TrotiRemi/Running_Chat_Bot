"""
Phase 4: Evaluation Script
Test the fine-tuned model trained on consolidated dataset (159 examples) on various scenarios.

The model was fine-tuned on complete_training_dataset.json which merges:
  - Original running_schedule_dataset.json (141 examples)
  - Augmented examples from Excel PDF (80 examples)
  - Extracted examples from 55 PDF programs (46 examples)
  - After deduplication: 159 unique training examples
"""

import json
import torch
from pathlib import Path
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Configuration
MODEL_PATH = Path(__file__).parent.parent / "models" / "finetuned_gpt2"
TEST_FILE = Path(__file__).parent.parent / "Data" / "processed" / "text_files" / "test.txt"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Test scenarios
TEST_SCENARIOS = [
    {
        "instruction": "Je suis un coureur débutant et je veux préparer un 5km en 8 semaines. Je peux m'entraîner 3x/week.",
        "input": "Niveau: débutant, Objectif: 5km, Durée: 8 semaines, Fréquence: 3x/week"
    },
    {
        "instruction": "Je suis un coureur intermédiaire préparant un Marathon en 12 semaines. Je peux m'entraîner 5x/week.",
        "input": "Niveau: intermédiaire, Objectif: Marathon, Durée: 12 semaines, Fréquence: 5x/week"
    },
    {
        "instruction": "Je suis un coureur avancé visant un sub-3h marathon en 16 semaines. Je peux m'entraîner 6x/week.",
        "input": "Niveau: avancé, Objectif: Marathon (Sub 3h), Durée: 16 semaines, Fréquence: 6x/week"
    },
]


def load_model_and_tokenizer():
    """Load fine-tuned model and tokenizer"""
    print("🤖 Loading fine-tuned GPT-2 model...")
    print(f"   From: {MODEL_PATH}\n")
    
    tokenizer = GPT2Tokenizer.from_pretrained(str(MODEL_PATH))
    model = GPT2LMHeadModel.from_pretrained(str(MODEL_PATH))
    model.to(DEVICE)
    model.eval()
    
    print(f"✓ Model loaded successfully on {DEVICE}\n")
    return model, tokenizer


def generate_schedule(model, tokenizer, instruction: str, input_text: str, max_length: int = 300):
    """Generate training schedule for given scenario"""
    
    prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
    
    # Tokenize
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(DEVICE)
    
    # Generate
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=max_length,
            num_beams=1,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id,
        )
    
    # Decode
    full_response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    # Extract only the response part
    if "### Response:" in full_response:
        response = full_response.split("### Response:")[-1].strip()
    else:
        response = full_response
    
    return response


def evaluate_on_test_set(model, tokenizer):
    """Evaluate on official test set"""
    print("📈 Evaluating on Official Test Set\n")
    print("="*80)
    
    if not TEST_FILE.exists():
        print(f"⚠️  Test file not found: {TEST_FILE}")
        return
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        examples = f.read().split("\n\n")
    
    examples = [ex.strip() for ex in examples if ex.strip()]
    
    print(f"Found {len(examples)} test examples\n")
    
    for i, example in enumerate(examples, 1):
        print(f"TEST EXAMPLE {i}:")
        print("-" * 80)
        print(example[:200] + "..." if len(example) > 200 else example)
        print("-" * 80 + "\n")


def evaluate_scenarios(model, tokenizer):
    """Evaluate on custom test scenarios"""
    print("\n📊 Evaluating on Custom Scenarios\n")
    print("="*80)
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n🎯 SCENARIO {i}")
        print("="*80)
        print(f"\n📋 Instruction:\n{scenario['instruction']}")
        print(f"\n📝 Input:\n{scenario['input']}")
        
        print(f"\n💡 Generated Schedule:\n")
        schedule = generate_schedule(model, tokenizer, scenario['instruction'], scenario['input'])
        print(schedule)
        
        print("\n" + "="*80)


def calculate_perplexity(model, tokenizer, max_length=1024):
    """Calculate perplexity on test set (chunked for long sequences)"""
    print("\n📊 Computing Perplexity on Test Set\n")
    
    if not TEST_FILE.exists():
        print(f"⚠️  Test file not found")
        return
    
    with open(TEST_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Tokenize entire text
    inputs = tokenizer(text, return_tensors='pt')
    input_ids = inputs['input_ids'].to(DEVICE)
    
    # Process in chunks if sequence is too long
    total_loss = 0.0
    num_chunks = 0
    
    for i in range(0, input_ids.shape[1], max_length):
        chunk = input_ids[:, i:i+max_length]
        
        # Skip if chunk is too small
        if chunk.shape[1] < 10:
            continue
        
        with torch.no_grad():
            outputs = model(chunk, labels=chunk)
            loss = outputs.loss
            total_loss += loss.item()
            num_chunks += 1
    
    # Calculate average perplexity
    avg_loss = total_loss / num_chunks if num_chunks > 0 else 0
    perplexity = torch.exp(torch.tensor(avg_loss)).item()
    
    print(f"✓ Test Perplexity: {perplexity:.4f}")
    print(f"  (Computed over {num_chunks} chunks)")
    print(f"  (Lower is better; baseline GPT-2 ~20+)\n")
    
    return perplexity


def main():
    """Main evaluation pipeline"""
    print("\n" + "="*80)
    print("PHASE 4: EVALUATION OF FINE-TUNED GPT-2 MODEL")
    print("="*80 + "\n")
    
    # Load model
    model, tokenizer = load_model_and_tokenizer()
    
    # Evaluate on test set
    evaluate_on_test_set(model, tokenizer)
    
    # Evaluate on scenarios
    evaluate_scenarios(model, tokenizer)
    
    # Calculate perplexity
    perplexity = calculate_perplexity(model, tokenizer)
    
    # Summary
    print("\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"\n✅ Evaluation completed!")
    print(f"\n📊 Metrics:")
    print(f"   Test Perplexity: {perplexity:.4f}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Review generated schedules above")
    print(f"   2. Run demo.py for interactive testing")
    print(f"   3. If results are good, proceed to Phase 5 (documentation)\n")


if __name__ == "__main__":
    main()
