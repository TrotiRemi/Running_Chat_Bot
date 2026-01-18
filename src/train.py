"""
Phase 3: Fine-Tuning Script for GPT-2 on Running Schedule Dataset

Trains a GPT-2 model to generate personalized running training programs.
Uses consolidated dataset from:
  - 141 original examples (running_schedule_dataset.json)
  - 80 augmented examples from Excel PDF (augmented_examples.json)
  - 46 examples from PDF running programs (program_catalog.json)
  - Total: 159 unique examples after deduplication

This consolidated dataset ensures better model generalization.
"""

import json
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List
from sklearn.model_selection import train_test_split
from transformers import (
    GPT2Tokenizer,
    GPT2LMHeadModel,
    Trainer,
    TrainingArguments,
    TextDataset,
    DataCollatorForLanguageModeling
)

# Configuration
DATASET_PATH = Path(__file__).parent.parent / "Data" / "processed" / "complete_training_dataset.json"
OUTPUT_DIR = Path(__file__).parent.parent / "models" / "finetuned_gpt2"
TEXT_DATA_DIR = Path(__file__).parent.parent / "Data" / "processed" / "text_files"
RESULTS_DIR = Path(__file__).parent.parent / "results"

# Create directories
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEXT_DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Hyperparameters
HYPERPARAMS = {
    "learning_rate": 5e-5,
    "batch_size": 2,  # Small batch size due to limited GPU memory
    "num_epochs": 3,
    "max_seq_length": 512,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    "save_steps": 50,
    "eval_steps": 50,
}

# Device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🖥️ Using device: {DEVICE}")
print(f"🔧 GPU available: {torch.cuda.is_available()}\n")


def load_dataset(dataset_path: Path) -> List[Dict]:
    """Load consolidated dataset from JSON file
    
    The consolidated dataset (complete_training_dataset.json) includes:
    - Examples from original running_schedule_dataset.json (Excel-based)
    - Augmented examples from PDF augmentation (augmented_examples.json)
    - Examples extracted from 55 PDF running programs (program_catalog.json)
    """
    print(f"📂 Loading consolidated dataset from {dataset_path}")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle both old format (list) and new format (dict with metadata)
    if isinstance(data, dict) and "training_examples" in data:
        dataset = data["training_examples"]
        print(f"   Sources:")
        print(f"     - PDF programs: {data['sources'].get('pdf_programs', 0)}")
        print(f"     - Augmented from Excel: {data['sources'].get('augmented_from_excel', 0)}")
        print(f"     - Original dataset: {data['sources'].get('original_dataset', 0)}")
        print(f"   After deduplication: {data['total_examples']} unique examples")
    else:
        dataset = data
    
    print(f"✓ Loaded {len(dataset)} training samples\n")
    return dataset


def create_prompt(example: Dict) -> str:
    """
    Create a complete prompt from instruction-input-output
    Format: "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n{output}"
    """
    instruction = example.get("instruction", "")
    input_text = example.get("input", "")
    output = example.get("output", "")
    
    prompt = f"""### Instruction:
{instruction}

### Input:
{input_text}

### Response:
{output}"""
    
    return prompt


def prepare_text_files(dataset: List[Dict], output_dir: Path) -> tuple:
    """
    Create train, validation, and test text files
    
    Returns:
        Tuple of (train_file, val_file, test_file) paths
    """
    print("📝 Preparing text files...")
    
    # Split dataset
    train, temp = train_test_split(dataset, test_size=0.3, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)
    
    print(f"   Train: {len(train)} | Val: {len(val)} | Test: {len(test)}")
    
    # Create text files
    def write_file(split, split_name):
        file_path = output_dir / f"{split_name}.txt"
        with open(file_path, 'w', encoding='utf-8') as f:
            for example in split:
                prompt = create_prompt(example)
                f.write(prompt + "\n\n")
        return file_path
    
    train_file = write_file(train, "train")
    val_file = write_file(val, "val")
    test_file = write_file(test, "test")
    
    print(f"✓ Text files created:")
    print(f"  - {train_file}")
    print(f"  - {val_file}")
    print(f"  - {test_file}\n")
    
    return train_file, val_file, test_file


class CustomDataset(torch.utils.data.Dataset):
    """Custom dataset for GPT-2 fine-tuning"""
    
    def __init__(self, file_path: Path, tokenizer, max_length: int):
        self.tokenizer = tokenizer
        self.max_length = max_length
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            self.examples = f.read().split("\n\n")
        
        # Filter empty examples
        self.examples = [ex.strip() for ex in self.examples if ex.strip()]
        
        print(f"   Loaded {len(self.examples)} examples from {file_path.name}")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        text = self.examples[idx]
        
        # Tokenize
        encodings = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        input_ids = encodings['input_ids'][0]
        attention_mask = encodings['attention_mask'][0]
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': input_ids.clone()
        }


def load_model_and_tokenizer():
    """Load pre-trained GPT-2 model and tokenizer"""
    print("🤖 Loading GPT-2 model and tokenizer...")
    
    tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained('gpt2')
    
    # Set pad token
    tokenizer.pad_token = tokenizer.eos_token
    
    print(f"✓ Model loaded successfully")
    print(f"  Model size: {model.num_parameters():,} parameters\n")
    
    return model, tokenizer


def train_model(model, tokenizer, train_file: Path, val_file: Path) -> str:
    """
    Train the model using Hugging Face Trainer
    
    Returns:
        Path to best model checkpoint
    """
    print("🎓 Starting fine-tuning training...\n")
    
    # Create datasets
    print("📊 Creating datasets...")
    train_dataset = CustomDataset(train_file, tokenizer, HYPERPARAMS["max_seq_length"])
    val_dataset = CustomDataset(val_file, tokenizer, HYPERPARAMS["max_seq_length"])
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR / "checkpoints"),
        overwrite_output_dir=True,
        num_train_epochs=HYPERPARAMS["num_epochs"],
        per_device_train_batch_size=HYPERPARAMS["batch_size"],
        per_device_eval_batch_size=HYPERPARAMS["batch_size"],
        learning_rate=HYPERPARAMS["learning_rate"],
        weight_decay=HYPERPARAMS["weight_decay"],
        warmup_steps=HYPERPARAMS["warmup_steps"],
        logging_steps=10,
        eval_steps=HYPERPARAMS["eval_steps"],
        save_steps=HYPERPARAMS["save_steps"],
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        eval_strategy="steps",
        save_strategy="steps",
        logging_dir=str(RESULTS_DIR / "logs"),
        seed=42,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
    )
    
    # Train
    print("\n" + "="*80)
    print("TRAINING IN PROGRESS")
    print("="*80 + "\n")
    
    trainer.train()
    
    print("\n" + "="*80)
    print("TRAINING COMPLETED")
    print("="*80 + "\n")
    
    return trainer


def save_model(model, tokenizer, output_dir: Path):
    """Save fine-tuned model and tokenizer"""
    print(f"💾 Saving model to {output_dir}...")
    
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    
    print(f"✓ Model saved successfully\n")


def evaluate_model(trainer, test_file: Path, tokenizer):
    """Evaluate model on test set"""
    print("📈 Evaluating model on test set...")
    
    test_dataset = CustomDataset(test_file, tokenizer, HYPERPARAMS["max_seq_length"])
    
    # Use trainer to evaluate
    eval_results = trainer.evaluate(eval_dataset=test_dataset)
    
    print("\n📊 Test Set Results:")
    for key, value in eval_results.items():
        print(f"  {key}: {value:.4f}")
    
    return eval_results


def save_training_config(hyperparams: Dict, output_dir: Path):
    """Save training configuration for reference"""
    config = {
        "hyperparameters": hyperparams,
        "device": str(DEVICE),
        "dataset_samples": 11,
        "model": "gpt2",
    }
    
    config_path = output_dir / "training_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Config saved: {config_path}\n")


def main():
    """Main training pipeline"""
    print("\n" + "="*80)
    print("PHASE 3: FINE-TUNING GPT-2 ON RUNNING SCHEDULE DATASET")
    print("="*80 + "\n")
    
    # Step 1: Load dataset
    dataset = load_dataset(DATASET_PATH)
    
    # Step 2: Create text files
    train_file, val_file, test_file = prepare_text_files(dataset, TEXT_DATA_DIR)
    
    # Step 3: Load model
    model, tokenizer = load_model_and_tokenizer()
    
    # Step 4: Train
    trainer = train_model(model, tokenizer, train_file, val_file)
    
    # Step 5: Save model
    save_model(trainer.model, tokenizer, OUTPUT_DIR)
    
    # Step 6: Evaluate
    eval_results = evaluate_model(trainer, test_file, tokenizer)
    
    # Step 7: Save config
    save_training_config(HYPERPARAMS, RESULTS_DIR)
    
    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"\n✅ Fine-tuning completed successfully!")
    print(f"\n📁 Output locations:")
    print(f"   Model: {OUTPUT_DIR}")
    print(f"   Results: {RESULTS_DIR}")
    print(f"   Logs: {RESULTS_DIR / 'logs'}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Run evaluate.py to test the model")
    print(f"   2. Run demo.py for interactive testing")
    print(f"   3. Check TensorBoard: tensorboard --logdir={RESULTS_DIR / 'logs'}\n")


if __name__ == "__main__":
    main()
