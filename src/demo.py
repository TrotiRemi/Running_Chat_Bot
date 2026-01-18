"""
Phase 5: Interactive Demo Script
Let users test the running schedule generator interactively.

Uses fine-tuned GPT-2 model trained on consolidated dataset of 159 unique examples.
The model learned from:
  - Original running_schedule_dataset.json (141 examples)
  - Augmented examples from Excel PDF (80 examples)  
  - Extracted examples from 55 PDF programs (46 examples)

Users can customize:
  - Training level (débutant, intermédiaire, avancé)
  - Race goal (5km, 10km, Semi-Marathon, Marathon)
  - Training duration (4-24 weeks)
  - Weekly frequency (2-6x/week)
"""

import json
import torch
from pathlib import Path
from transformers import GPT2Tokenizer, GPT2LMHeadModel

# Configuration
MODEL_PATH = Path(__file__).parent.parent / "models" / "finetuned_gpt2"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

LEVELS = ["débutant", "intermédiaire", "avancé"]
GOALS = ["5km", "10km", "Marathon", "Semi-Marathon"]
DURATIONS = list(range(4, 25))  # 4-24 weeks
FREQUENCIES = ["2x/week", "3x/week", "3-4x/week", "4x/week", "5x/week", "6x/week"]


def load_model_and_tokenizer():
    """Load fine-tuned model and tokenizer"""
    print("🤖 Loading fine-tuned GPT-2 model...")
    
    tokenizer = GPT2Tokenizer.from_pretrained(str(MODEL_PATH))
    model = GPT2LMHeadModel.from_pretrained(str(MODEL_PATH))
    model.to(DEVICE)
    model.eval()
    
    print(f"✓ Model loaded successfully on {DEVICE}\n")
    return model, tokenizer


def display_menu():
    """Display interactive menu"""
    print("\n" + "="*80)
    print("RUNNING SCHEDULE GENERATOR - INTERACTIVE DEMO")
    print("="*80)
    print("\nChoose your training profile:\n")
    
    # Level
    print("1️⃣  LEVEL:")
    for i, level in enumerate(LEVELS, 1):
        print(f"   {i}. {level.capitalize()}")
    level_choice = input("   Select (1-3): ").strip()
    level = LEVELS[int(level_choice) - 1] if level_choice.isdigit() and 1 <= int(level_choice) <= 3 else "intermédiaire"
    
    # Goal
    print("\n2️⃣  GOAL:")
    for i, goal in enumerate(GOALS, 1):
        print(f"   {i}. {goal}")
    goal_choice = input("   Select (1-4): ").strip()
    goal = GOALS[int(goal_choice) - 1] if goal_choice.isdigit() and 1 <= int(goal_choice) <= 4 else "Marathon"
    
    # Duration
    print(f"\n3️⃣  DURATION: (4-24 weeks)")
    duration_choice = input("   Enter weeks: ").strip()
    duration = int(duration_choice) if duration_choice.isdigit() and 4 <= int(duration_choice) <= 24 else 12
    
    # Frequency
    print("\n4️⃣  FREQUENCY:")
    for i, freq in enumerate(FREQUENCIES, 1):
        print(f"   {i}. {freq}")
    freq_choice = input("   Select (1-6): ").strip()
    frequency = FREQUENCIES[int(freq_choice) - 1] if freq_choice.isdigit() and 1 <= int(freq_choice) <= 6 else "4x/week"
    
    return level, goal, duration, frequency


def generate_schedule(model, tokenizer, level: str, goal: str, duration: int, frequency: str):
    """Generate personalized running schedule"""
    
    instruction = f"Je suis un coureur {level} et je veux préparer un {goal} en {duration} semaines. Je peux m'entraîner {frequency}."
    input_text = f"Niveau: {level}, Objectif: {goal}, Durée: {duration} semaines, Fréquence: {frequency}"
    
    prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
    
    print("\n⏳ Generating your personalized running schedule...\n")
    
    # Tokenize
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(DEVICE)
    
    # Generate
    with torch.no_grad():
        output = model.generate(
            input_ids,
            max_length=400,
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
    
    return instruction, input_text, response


def display_schedule(instruction: str, input_text: str, schedule: str):
    """Display formatted schedule"""
    print("="*80)
    print("YOUR PERSONALIZED RUNNING SCHEDULE")
    print("="*80)
    
    print(f"\n📋 Your Profile:")
    print(f"   {instruction}")
    
    print(f"\n💡 Generated Schedule:")
    print("-"*80)
    print(schedule)
    print("-"*80)


def interactive_mode(model, tokenizer):
    """Run interactive demo"""
    
    while True:
        level, goal, duration, frequency = display_menu()
        instruction, input_text, schedule = generate_schedule(model, tokenizer, level, goal, duration, frequency)
        display_schedule(instruction, input_text, schedule)
        
        # Ask to continue
        again = input("\n\n🔄 Generate another schedule? (y/n): ").strip().lower()
        if again != 'y':
            break
    
    print("\n👋 Thanks for using Running Schedule Generator!\n")


def main():
    """Main demo pipeline"""
    print("\n" + "="*80)
    print("RUNNING SCHEDULE GENERATOR - INTERACTIVE DEMO")
    print("="*80)
    
    # Load model
    model, tokenizer = load_model_and_tokenizer()
    
    # Interactive mode
    interactive_mode(model, tokenizer)


if __name__ == "__main__":
    main()
