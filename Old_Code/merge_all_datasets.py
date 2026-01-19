"""
Merge all training programs from PDFs and Excel into one comprehensive dataset
Create a large unified training dataset for model fine-tuning
"""

import json
from pathlib import Path
from typing import Dict, List

# Configuration
CATALOG_PATH = Path(__file__).parent.parent / "Data" / "processed" / "pdf" / "program_catalog.json"
AUGMENTED_PATH = Path(__file__).parent.parent / "Data" / "processed" / "augmented_examples.json"
ORIGINAL_PATH = Path(__file__).parent.parent / "Data" / "processed" / "running_schedule_dataset.json"
OUTPUT_PATH = Path(__file__).parent.parent / "Data" / "processed" / "complete_training_dataset.json"

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def extract_schedule_from_content(content: str) -> str:
    """Extract the training schedule table from PDF content"""
    if not content:
        return ""
    
    lines = content.split('\n')
    schedule_lines = []
    in_schedule = False
    week_found = 0
    
    for i, line in enumerate(lines):
        # Detect schedule start with WEEK and day headers
        if "WEEK" in line.upper() and any(day in line.upper() for day in ["MONDAY", "TUESDAY", "WEDNESDAY"]):
            in_schedule = True
            week_found = i
        
        if in_schedule:
            schedule_lines.append(line.strip())
            # Collect schedule lines (stop after ~25 lines for a good sample)
            if len(schedule_lines) > 25:
                break
    
    if schedule_lines:
        return "\n".join(schedule_lines)
    
    # Fallback: return content preview
    return content[:400] if content else ""


def extract_duration_from_program(program: Dict, filename: str) -> str:
    """Extract duration from program metadata and filename"""
    
    # First try: from metadata
    if program.get("duration"):
        return program["duration"]
    
    # Second try: from detected weeks
    if program.get("detected_weeks"):
        return f"{program['detected_weeks']} semaines"
    
    # Third try: from filename patterns
    if "8-week" in filename.lower():
        return "8 semaines"
    elif "12-week" in filename.lower():
        return "12 semaines"
    elif "14-week" in filename.lower():
        return "14 semaines"
    elif "16-week" in filename.lower():
        return "16 semaines"
    elif "20-week" in filename.lower():
        return "20 semaines"
    elif "3-day" in filename.lower():
        return "8 semaines"  # Typical for 3-day programs
    
    # Default
    return "12 semaines"


def create_example_from_pdf_program(program: Dict) -> Dict:
    """
    Create training example from PDF program data
    """
    
    filename = program.get("filename", "Unknown")
    distance = program.get("distance")
    level = program.get("level", "Intermédiaire")
    content = program.get("full_content", "")
    age_group = program.get("age_group")
    goal_time = program.get("goal_time")
    
    # Skip if no distance
    if not distance:
        return None
    
    # Extract duration properly
    duration = extract_duration_from_program(program, filename)
    duration_weeks = int(duration.split()[0]) if duration else 12
    
    # Map level to French
    level_map = {
        "Débutant": "débutant",
        "Intermédiaire": "intermédiaire",
        "Avancé": "avancé",
        "Maintenance": "intermédiaire",
        "Initiation": "débutant",
    }
    level_fr = level_map.get(level, "intermédiaire")
    
    # Determine frequency from duration heuristic
    if "3-day" in filename:
        frequency = "3x/week"
    elif "4-day" in filename or "4c" in filename:
        frequency = "4x/week"
    elif "5-day" in filename or "5-day" in filename:
        frequency = "5x/week"
    else:
        frequency = "4x/week"
    
    # Build instruction
    instruction = f"Je suis un coureur {level_fr} et je veux préparer un {distance} en {duration_weeks} semaines"
    if goal_time:
        instruction += f" en {goal_time}"
    instruction += f". Je peux m'entraîner {frequency}."
    
    # Build input
    input_text = f"Niveau: {level_fr}, Objectif: {distance}, Durée: {duration_weeks} semaines, Fréquence: {frequency}"
    if goal_time:
        input_text += f", Record visé: {goal_time}"
    if age_group:
        input_text += f", Groupe d'âge: {age_group}"
    
    # Build output with actual schedule
    output = f"""# Programme d'Entraînement {distance}
**Niveau:** {level_fr.capitalize()}
**Objectif:** {distance}
**Durée:** {duration_weeks} semaines
**Fréquence d'entraînement:** {frequency}"""
    
    if goal_time:
        output += f"\n**Record visé:** {goal_time}"
    if age_group:
        output += f"\n**Groupe d'âge:** {age_group}"
    
    # Add detected weeks from content
    if program.get("detected_weeks"):
        output += f"\n**Semaines de préparation détectées:** {program['detected_weeks']}"
    
    # Add schedule if available
    schedule = extract_schedule_from_content(content)
    if schedule:
        output += f"\n\n**Emploi du temps:**\n```\n{schedule}\n```"
    
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "metadata": {
            "source": "pdf_program",
            "pdf_file": filename,
            "level": level_fr,
            "goal": distance,
            "duration_weeks": duration_weeks,
            "frequency": frequency,
            "goal_time": goal_time,
            "age_group": age_group,
            "category": program.get("category", "Général"),
        }
    }


def main():
    """Main merge pipeline"""
    print("\n" + "="*80)
    print("MERGING ALL TRAINING PROGRAMS INTO COMPREHENSIVE DATASET")
    print("="*80 + "\n")
    
    all_examples = []
    
    # Step 1: Load PDF catalog
    print("📂 Loading PDF catalog...")
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    pdf_programs = catalog.get("programs", [])
    print(f"   ✓ Loaded {len(pdf_programs)} PDF programs\n")
    
    # Step 2: Extract examples from PDF programs
    print("📝 Creating examples from PDF programs...")
    pdf_examples_count = 0
    
    for program in pdf_programs:
        example = create_example_from_pdf_program(program)
        if example:
            all_examples.append(example)
            pdf_examples_count += 1
    
    print(f"   ✓ Created {pdf_examples_count} examples from PDFs\n")
    
    # Step 3: Load augmented examples (from Excel-based generation)
    print("📂 Loading augmented examples from Excel...")
    with open(AUGMENTED_PATH, 'r', encoding='utf-8') as f:
        augmented = json.load(f)
    
    augmented_count = len(augmented)
    all_examples.extend(augmented)
    print(f"   ✓ Loaded {augmented_count} augmented examples\n")
    
    # Step 4: Load original dataset
    print("📂 Loading original dataset...")
    with open(ORIGINAL_PATH, 'r', encoding='utf-8') as f:
        original = json.load(f)
    
    original_count = len(original)
    all_examples.extend(original)
    print(f"   ✓ Loaded {original_count} original examples\n")
    
    # Step 5: Deduplicate by instruction
    print("🔄 Deduplicating examples...")
    seen = set()
    unique_examples = []
    duplicates = 0
    
    for example in all_examples:
        instruction = example["instruction"]
        if instruction not in seen:
            seen.add(instruction)
            unique_examples.append(example)
        else:
            duplicates += 1
    
    print(f"   ✓ Removed {duplicates} duplicates\n")
    
    # Step 6: Save unified dataset
    print("💾 Saving unified dataset...")
    unified_dataset = {
        "total_examples": len(unique_examples),
        "sources": {
            "pdf_programs": pdf_examples_count,
            "augmented_from_excel": augmented_count,
            "original_dataset": original_count,
        },
        "deduplication": {
            "total_before": len(all_examples),
            "duplicates_removed": duplicates,
            "unique_after": len(unique_examples),
        },
        "training_examples": unique_examples,
    }
    
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(unified_dataset, f, indent=2, ensure_ascii=False)
    
    print(f"   ✓ Saved to: {OUTPUT_PATH}\n")
    
    # Step 7: Summary statistics
    print("="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    print(f"📊 Dataset Composition:")
    print(f"   From PDFs:              {pdf_examples_count:3d} examples")
    print(f"   From Excel (augmented): {augmented_count:3d} examples")
    print(f"   From original dataset:  {original_count:3d} examples")
    print(f"   ────────────────────────────────")
    print(f"   Total (before dedup):   {len(all_examples):3d} examples")
    print(f"   Duplicates removed:     {duplicates:3d}")
    print(f"   ────────────────────────────────")
    print(f"   FINAL DATASET:          {len(unique_examples):3d} examples ✅\n")
    
    # Stats by level
    levels = {}
    for ex in unique_examples:
        level = ex["metadata"]["level"]
        levels[level] = levels.get(level, 0) + 1
    
    print(f"📈 By Level:")
    for level, count in sorted(levels.items()):
        print(f"   {level.capitalize():20s}: {count:3d}")
    
    # Stats by goal
    goals = {}
    for ex in unique_examples:
        goal = ex["metadata"]["goal"]
        goals[goal] = goals.get(goal, 0) + 1
    
    print(f"\n🎯 By Goal/Distance:")
    for goal, count in sorted(goals.items()):
        print(f"   {goal:20s}: {count:3d}")
    
    print(f"\n✅ Complete training dataset ready for fine-tuning!")
    print(f"\n🎯 Next steps:")
    print(f"   1. Run: python src/train.py")
    print(f"   2. Evaluate: python src/evaluate.py")
    print(f"   3. Test: python src/demo.py\n")


if __name__ == "__main__":
    main()
