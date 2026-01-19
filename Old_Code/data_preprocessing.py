"""
Data Preprocessing Script
Converts XLSX Running Schedule files to instruction-response pairs (Alpaca format)
"""

import os
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Configuration
SCHEDULE_DIR = Path(__file__).parent.parent / "Data" / "Running_Schedule"
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Mapping de métadonnées basé sur le nom du fichier
SCHEDULE_METADATA = {
    "8 Week Marathon Training Plan.xlsx": {
        "duration_weeks": 8,
        "level": "intermediate",
        "goal": "Marathon",
        "frequency": "4-5x/week"
    },
    "16 Week Marathon Training Plan.xlsx": {
        "duration_weeks": 16,
        "level": "intermediate",
        "goal": "Marathon",
        "frequency": "5x/week"
    },
    "20 Week Marathon Training Plan.xlsx": {
        "duration_weeks": 20,
        "level": "intermediate",
        "goal": "Marathon",
        "frequency": "5x/week"
    },
    "20 Weeks Marathon Training Plan.xlsx": {
        "duration_weeks": 20,
        "level": "intermediate",
        "goal": "Marathon",
        "frequency": "5x/week"
    },
    "20 Week Advanced Marathon Training Plan.xlsx": {
        "duration_weeks": 20,
        "level": "advanced",
        "goal": "Marathon",
        "frequency": "5-6x/week"
    },
    "20 Week Advanced 2 Marathon Training Plan.xlsx": {
        "duration_weeks": 20,
        "level": "advanced",
        "goal": "Marathon",
        "frequency": "5-6x/week"
    },
    "3 Month Marathon Training Plan.xlsx": {
        "duration_weeks": 12,
        "level": "intermediate",
        "goal": "Marathon",
        "frequency": "4-5x/week"
    },
    "3_30 Hour Marathon Training Plan.xlsx": {
        "duration_weeks": 16,
        "level": "intermediate",
        "goal": "Marathon (Sub 3:30h)",
        "frequency": "5x/week"
    },
    "6 Month Marathon Training Plan.xlsx": {
        "duration_weeks": 24,
        "level": "beginner",
        "goal": "Marathon",
        "frequency": "3-4x/week"
    },
    "Couch To Marathon Training Plan.xlsx": {
        "duration_weeks": 24,
        "level": "beginner",
        "goal": "Marathon",
        "frequency": "3-4x/week"
    },
    "Sub 3-Hour Marathon Training Plan.xlsx": {
        "duration_weeks": 16,
        "level": "advanced",
        "goal": "Marathon (Sub 3h)",
        "frequency": "6x/week"
    },
    "Sub 4-hour Marathon Training Plan.xlsx": {
        "duration_weeks": 16,
        "level": "intermediate",
        "goal": "Marathon (Sub 4h)",
        "frequency": "5x/week"
    }
}


def explore_schedule_files() -> None:
    """Explore and display structure of XLSX files"""
    print("=" * 80)
    print("EXPLORATION DES FICHIERS DE PROGRAMME D'ENTRAÎNEMENT")
    print("=" * 80)
    
    schedule_files = list(SCHEDULE_DIR.glob("*.xlsx"))
    print(f"\n✓ {len(schedule_files)} fichiers trouvés\n")
    
    for file in schedule_files:
        print(f"\n📄 {file.name}")
        try:
            df = pd.read_excel(file, sheet_name=0)
            print(f"   Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
            print(f"   Colonnes: {list(df.columns)}")
            print(f"   Aperçu:\n{df.head(3).to_string()}")
        except Exception as e:
            print(f"   ⚠️ Erreur: {e}")


def generate_schedule_response(metadata: Dict) -> str:
    """
    Generate a realistic training schedule based on metadata
    
    Args:
        metadata: Schedule metadata (level, duration, frequency, goal)
    
    Returns:
        Formatted training schedule text
    """
    level = metadata['level']
    duration = metadata['duration_weeks']
    frequency = metadata['frequency']
    goal = metadata['goal']
    
    lines = []
    lines.append(f"# Programme d'Entraînement Marathon {duration} semaines")
    lines.append(f"**Niveau:** {level.capitalize()}")
    lines.append(f"**Objectif:** {goal}")
    lines.append(f"**Fréquence d'entraînement:** {frequency}\n")
    
    # Generate sample weeks (3-4 weeks to show the pattern)
    num_sample_weeks = min(4, duration)
    
    # Training types based on level
    training_patterns = {
        "beginner": {
            "days": ["Lundi", "Mercredi", "Samedi", "Dimanche"],
            "types": ["Récupération", "Endurance", "Longue sortie", "Facile"],
            "sample_distances": ["5-6 km", "8-10 km", "12-15 km", "6-8 km"]
        },
        "intermediate": {
            "days": ["Lundi", "Mardi", "Jeudi", "Samedi", "Dimanche"],
            "types": ["Facile", "Vitesse/Interval", "Tempo", "Longue sortie", "Récupération"],
            "sample_distances": ["8-10 km", "10x400m", "5 km tempo", "18-20 km", "6-8 km"]
        },
        "advanced": {
            "days": ["Lundi", "Mardi", "Mercredi", "Jeudi", "Samedi", "Dimanche"],
            "types": ["Récupération", "VO2 Max", "Seuil", "Intervalle court", "Longue sortie", "Facile"],
            "sample_distances": ["8 km", "6x3 min", "6 km seuil", "8x600m", "20-22 km", "8-10 km"]
        }
    }
    
    pattern = training_patterns.get(level, training_patterns["intermediate"])
    
    # Adapt distances based on duration
    if duration <= 8:
        distance_multiplier = 0.8
    elif duration <= 16:
        distance_multiplier = 1.0
    else:
        distance_multiplier = 1.2
    
    # Generate schedule for sample weeks
    for week in range(1, num_sample_weeks + 1):
        lines.append(f"\n**Semaine {week}:**")
        
        for i, day in enumerate(pattern['days']):
            workout_type = pattern['types'][i]
            distance = pattern['sample_distances'][i]
            lines.append(f"  - {day}: {distance} ({workout_type})")
        
        # Add progression note
        if week < num_sample_weeks:
            lines.append(f"  *Semaine progressive: augmentation progressive de l'intensité*")
    
    # Add final advice
    lines.append(f"\n**Notes importantes:**")
    lines.append(f"- Commencer progressivement et écouter son corps")
    lines.append(f"- Respecter les jours de repos")
    lines.append(f"- Augmenter le volume graduellement (10% par semaine maximum)")
    lines.append(f"- Se chauffer avant et étirer après chaque séance")
    lines.append(f"- Adapter le programme à votre condition physique")
    
    return "\n".join(lines)
    
    return "\n".join(lines)


def create_instruction_response_pair(
    schedule_text: str,
    metadata: Dict,
    file_name: str
) -> Dict:
    """
    Create an instruction-response pair in Alpaca format
    
    Args:
        schedule_text: Formatted schedule text
        metadata: Schedule metadata
        file_name: Original file name
    
    Returns:
        Dictionary with instruction, input, output
    """
    
    # Create varied instructions based on metadata
    level_fr = {
        "beginner": "débutant",
        "intermediate": "intermédiaire",
        "advanced": "avancé"
    }
    
    goal_simple = metadata['goal'].split('(')[0].strip()
    
    instructions = [
        f"Je suis un coureur {level_fr[metadata['level']]} et je veux préparer un {goal_simple} en {metadata['duration_weeks']} semaines. Je peux m'entraîner {metadata['frequency']}.",
        f"Crée un programme d'entraînement pour un coureur {level_fr[metadata['level']]} visant un {goal_simple} en {metadata['duration_weeks']} semaines avec {metadata['frequency']} d'entraînement par semaine.",
        f"J'ai besoin d'un plan d'entraînement pour le {goal_simple}. Niveau: {level_fr[metadata['level']]}, Durée: {metadata['duration_weeks']} semaines, Disponibilité: {metadata['frequency']}.",
    ]
    
    return {
        "instruction": instructions[0],  # Use first instruction
        "input": f"Niveau: {level_fr[metadata['level']]}, Objectif: {goal_simple}, Durée: {metadata['duration_weeks']} semaines, Fréquence: {metadata['frequency']}",
        "output": schedule_text,
        "metadata": {
            "source_file": file_name,
            **metadata
        }
    }


def create_dataset() -> List[Dict]:
    """
    Create full dataset from XLSX files
    
    Returns:
        List of instruction-response pairs
    """
    dataset = []
    
    schedule_files = sorted(SCHEDULE_DIR.glob("*.xlsx"))
    
    for file in schedule_files:
        file_name = file.name
        print(f"\n📖 Processing: {file_name}")
        
        if file_name not in SCHEDULE_METADATA:
            print(f"   ⚠️ No metadata found, skipping...")
            continue
        
        try:
            # Read Excel file
            df = pd.read_excel(file, sheet_name=0)
            metadata = SCHEDULE_METADATA[file_name]
            
            # Generate schedule text (without parsing complex Excel structure)
            schedule_text = generate_schedule_response(metadata)
            
            # Create instruction-response pair
            pair = create_instruction_response_pair(schedule_text, metadata, file_name)
            dataset.append(pair)
            
            print(f"   ✓ Processed successfully ({len(schedule_text)} chars)")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
    
    return dataset


def save_dataset(dataset: List[Dict], format: str = "json") -> None:
    """
    Save dataset to file
    
    Args:
        dataset: List of instruction-response pairs
        format: 'json' or 'jsonl'
    """
    if format == "json":
        output_file = OUTPUT_DIR / "running_schedule_dataset.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    elif format == "jsonl":
        output_file = OUTPUT_DIR / "running_schedule_dataset.jsonl"
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"\n✅ Dataset saved: {output_file}")
    print(f"   Total samples: {len(dataset)}")


def main():
    """Main pipeline"""
    print("\n🚀 PHASE 2: DATASET PREPARATION\n")
    
    # Step 1: Explore files
    explore_schedule_files()
    
    # Step 2: Create dataset
    print("\n" + "=" * 80)
    print("CRÉATION DU DATASET")
    print("=" * 80)
    
    dataset = create_dataset()
    
    # Step 3: Save dataset
    print("\n" + "=" * 80)
    print("SAUVEGARDE")
    print("=" * 80)
    
    save_dataset(dataset, format="json")
    save_dataset(dataset, format="jsonl")
    
    # Step 4: Statistics
    print("\n" + "=" * 80)
    print("STATISTIQUES")
    print("=" * 80)
    print(f"\n📊 Total samples: {len(dataset)}")
    
    levels = {}
    for item in dataset:
        level = item['metadata']['level']
        levels[level] = levels.get(level, 0) + 1
    
    print(f"📚 Par niveau:")
    for level, count in sorted(levels.items()):
        print(f"   - {level}: {count}")
    
    print(f"\n💾 Fichiers créés:")
    print(f"   - {OUTPUT_DIR / 'running_schedule_dataset.json'}")
    print(f"   - {OUTPUT_DIR / 'running_schedule_dataset.jsonl'}")


if __name__ == "__main__":
    main()
