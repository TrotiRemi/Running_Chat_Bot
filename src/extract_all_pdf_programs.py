"""
Extract and categorize all PDF training programs
Parse metadata from filenames and PDF content
Create structured JSON database of all programs
"""

import json
import re
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional

# Configuration
PDF_DIR = Path(__file__).parent.parent / "Data" / "Running_Schedule" / "pdf"
OUTPUT_DIR = Path(__file__).parent.parent / "Data" / "processed" / "pdf"
CATALOG_FILE = OUTPUT_DIR / "program_catalog.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Category mappings
DISTANCE_MAPPING = {
    "1-mile": "1 mile",
    "1mile": "1 mile",
    "5k": "5K",
    "10k": "10K",
    "10-mile": "10 miles",
    "10mile": "10 miles",
    "half-marathon": "Half Marathon",
    "halfmarathon": "Half Marathon",
    "marathon": "Marathon",
    "treadmill": "Treadmill",
}

LEVEL_MAPPING = {
    "beginner": "Débutant",
    "intermediate": "Intermédiaire",
    "advanced": "Avancé",
    "maintenance": "Maintenance",
    "couch-to": "Débutant Complet",
}

AGE_MAPPING = {
    "40": "-40 ans",
    "50": "40-50 ans",
    "60": "50+ ans",
}


def parse_pdf_filename(filename: str) -> Dict:
    """
    Parse metadata from PDF filename with improved detection
    Examples:
    - rw-3-day-5k-training-plan-68db027a12ab8.pdf
    - rw-break-130-half-marathon-training-plan-6939f08fcb44c.pdf
    - 240487r-01h-rwd-runstrongpdfs-40-beginner-66cca274c557b.pdf
    """
    
    metadata = {
        "filename": filename,
        "frequency": None,  # 3-day, 4-day, 5-day
        "distance": None,
        "level": None,
        "age_group": None,
        "goal_time": None,  # break-130 = 1h30
        "duration": None,  # 8-week, 12-week
        "category": None,
    }
    
    name = filename.lower().replace(".pdf", "")
    
    # Extract frequency (3-day, 4-day, etc.)
    freq_match = re.search(r'(\d)-day', name)
    if freq_match:
        metadata["frequency"] = f"{freq_match.group(1)}x/week"
    
    # Extract distance (more comprehensive)
    distances_keys = ["1-mile", "1mile", "5k", "10k", "10-mile", "10mile", 
                      "half-marathon", "halfmarathon", "marathon", "treadmill"]
    for key in sorted(distances_keys, key=len, reverse=True):
        if key in name:
            metadata["distance"] = DISTANCE_MAPPING.get(key, key)
            break
    
    # Extract level (more comprehensive)
    levels_keys = ["beginner", "intermediate", "advanced", "maintenance", "couch-to"]
    for key in levels_keys:
        if key in name:
            metadata["level"] = LEVEL_MAPPING.get(key, key)
            break
    
    # Extract age group from pattern: -40-, -50-, -60-
    age_match = re.search(r'-(\d{2})[a-z\-_]', name)
    if age_match:
        age = age_match.group(1)
        if age in AGE_MAPPING:
            metadata["age_group"] = AGE_MAPPING[age]
    
    # Extract goal time (break-130 = 1h30)
    break_match = re.search(r'break-(\d+)', name)
    if break_match:
        time_str = break_match.group(1)
        # Convert format: 130 -> 1:30, 215 -> 2:15, 20 -> 0:20
        if len(time_str) == 3:
            metadata["goal_time"] = f"{time_str[0]}:{time_str[1:]}"
        elif len(time_str) == 2:
            metadata["goal_time"] = f"0:{time_str}"
        elif len(time_str) == 4:
            metadata["goal_time"] = f"{time_str[0:2]}:{time_str[2:]}"
    
    # Extract duration (20-week, 12-week, etc.)
    duration_match = re.search(r'(\d+)-week', name)
    if duration_match:
        metadata["duration"] = f"{duration_match.group(1)} semaines"
    
    # Determine category
    if metadata["goal_time"]:
        metadata["category"] = "Amélioration"
    elif metadata["level"] == "Débutant Complet":
        metadata["category"] = "Initiation"
    elif metadata["level"] == "Débutant":
        metadata["category"] = "Débutant"
    elif metadata["level"] == "Intermédiaire":
        metadata["category"] = "Intermédiaire"
    elif metadata["level"] == "Avancé":
        metadata["category"] = "Avancé"
    elif metadata["level"] == "Maintenance":
        metadata["category"] = "Maintenance"
    else:
        metadata["category"] = "Général"
    
    return metadata


def extract_pdf_content(pdf_path: Path) -> str:
    """Extract text from PDF"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"   ⚠️  Error reading {pdf_path.name}: {str(e)}")
        return ""


def extract_program_details(text: str, metadata: Dict) -> Dict:
    """
    Extract detailed program information from PDF content
    Look for: weeks count, distances, weekly schedules, intensity patterns
    """
    
    details = {
        "num_pages": text.count("---") if "---" in text else 0,
        "has_schedule": "MONDAY" in text or "LUNDI" in text.upper() or "WEEK" in text.upper(),
        "has_distances": "km" in text.lower() or "mile" in text.lower(),
        "has_intervals": "interval" in text.lower() or "400m" in text or "tempo" in text.lower(),
        "has_strength": "strength" in text.lower() or "force" in text.lower() or "weight" in text.lower(),
        "content_preview": text[:500] if text else "",  # First 500 chars
        "full_content": text,  # Store full content
    }
    
    # Detect week count from content
    week_matches = re.findall(r'week\s*(\d+)', text.lower())
    if week_matches:
        details["detected_weeks"] = max(int(w) for w in week_matches)
    
    # Extract distances mentioned
    distances = re.findall(r'(\d+(?:\.\d+)?)\s*(?:km|miles?|mi)', text, re.IGNORECASE)
    if distances:
        details["distances_found"] = [float(d) for d in distances]
    
    return details


def create_training_example_from_program(metadata: Dict, content: str, details: Dict) -> Optional[Dict]:
    """
    Create training example for LLM dataset from program metadata
    Extract real content from PDFs like the running schedule
    """
    
    # Skip if missing key info
    if not metadata["distance"]:
        return None
    
    distance = metadata["distance"]
    level = metadata["level"] or "Intermédiaire"
    frequency = metadata["frequency"] or "4x/week"
    duration = metadata["duration"] or "12 semaines"
    
    # Map level to French format
    level_map = {
        "débutant": "débutant",
        "intermédiaire": "intermédiaire",
        "avancé": "avancé",
        "maintenance": "intermédiaire",
        "débutant complet": "débutant",
    }
    
    level_fr = level_map.get(level.lower(), "intermédiaire")
    
    # Build instruction
    instruction = f"Je suis un coureur {level_fr} et je veux préparer un {distance}"
    if metadata["goal_time"]:
        instruction += f" en {metadata['goal_time']}"
    instruction += f" en {duration}. Je peux m'entraîner {frequency}."
    
    # Build input
    input_text = f"Niveau: {level_fr}, Objectif: {distance}, Durée: {duration}, Fréquence: {frequency}"
    if metadata["goal_time"]:
        input_text += f", Record visé: {metadata['goal_time']}"
    if metadata["age_group"]:
        input_text += f", Groupe d'âge: {metadata['age_group']}"
    
    # Build output with real content from PDF
    output = f"""# Programme d'Entraînement {distance}
**Niveau:** {level_fr.capitalize()}
**Objectif:** {distance}
**Durée:** {duration}
**Fréquence d'entraînement:** {frequency}"""
    
    if metadata["goal_time"]:
        output += f"\n**Record visé:** {metadata['goal_time']}"
    if metadata["age_group"]:
        output += f"\n**Groupe d'âge:** {metadata['age_group']}"
    
    # Add detected weeks from content
    if details.get("detected_weeks"):
        output += f"\n**Semaines:** {details['detected_weeks']}"
    
    # Add content preview/schedule from PDF
    if content:
        # Extract first schedule or preview
        lines = content.split('\n')
        schedule_lines = []
        in_schedule = False
        
        for line in lines:
            if "MONDAY" in line or "WEEK" in line.upper() or "LUNDI" in line:
                in_schedule = True
            if in_schedule:
                schedule_lines.append(line)
                if len(schedule_lines) > 30:  # Limit to 30 lines
                    break
        
        if schedule_lines:
            output += "\n\n**Emploi du temps:**\n"
            output += "\n".join(schedule_lines[:20])
        else:
            # Fallback: include content preview
            output += f"\n\n**Détails du programme:**\n{content[:500]}..."
    
    return {
        "instruction": instruction,
        "input": input_text,
        "output": output,
        "metadata": {
            "source": "pdf_program",
            "pdf_file": metadata["filename"],
            "level": level_fr,
            "goal": distance,
            "duration_weeks": int(metadata["duration"].split()[0]) if metadata["duration"] else 12,
            "frequency": frequency,
            "goal_time": metadata["goal_time"],
            "age_group": metadata["age_group"],
            "category": metadata["category"],
            "has_schedule": details.get("has_schedule", False),
            "has_intervals": details.get("has_intervals", False),
        }
    }


def main():
    """Main extraction pipeline"""
    print("\n" + "="*80)
    print("EXTRACTING AND CATEGORIZING ALL PDF TRAINING PROGRAMS")
    print("="*80 + "\n")
    
    # Get all PDFs
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"📊 Found {len(pdf_files)} PDF files\n")
    
    catalog = {
        "total_programs": len(pdf_files),
        "extraction_date": "2026-01-05",
        "programs": [],
        "categories": {},
        "training_examples": [],
    }
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Processing {pdf_path.name}...")
        
        # Parse filename
        metadata = parse_pdf_filename(pdf_path.name)
        
        # Extract content
        content = extract_pdf_content(pdf_path)
        details = extract_program_details(content, metadata)
        
        # Create program entry
        program = {
            **metadata,
            **details,
            "content_length": len(content),
        }
        
        catalog["programs"].append(program)
        
        # Categorize
        category = program["category"]
        if category not in catalog["categories"]:
            catalog["categories"][category] = []
        catalog["categories"][category].append(pdf_path.name)
        
        # Create training example
        example = create_training_example_from_program(metadata, content, details)
        if example:
            catalog["training_examples"].append(example)
        
        # Print summary
        print(f"   ✓ Level: {program['level']}, Distance: {program['distance']}, Freq: {program['frequency']}")
        if program["goal_time"]:
            print(f"   🎯 Goal Time: {program['goal_time']}")
        print()
    
    # Save catalog
    with open(CATALOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print("="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    print(f"✓ Total programs extracted: {len(catalog['programs'])}")
    print(f"✓ Training examples created: {len(catalog['training_examples'])}\n")
    
    print("📁 Programs by category:")
    for category, files in sorted(catalog["categories"].items()):
        print(f"   {category}: {len(files)} programs")
    
    print(f"\n📁 Programs by distance:")
    distances = {}
    for prog in catalog["programs"]:
        dist = prog["distance"] or "Unknown"
        if dist not in distances:
            distances[dist] = 0
        distances[dist] += 1
    
    for dist, count in sorted(distances.items()):
        print(f"   {dist}: {count} programs")
    
    print(f"\n📁 Programs by level:")
    levels = {}
    for prog in catalog["programs"]:
        level = prog["level"] or "Unknown"
        if level not in levels:
            levels[level] = 0
        levels[level] += 1
    
    for level, count in sorted(levels.items()):
        print(f"   {level}: {count} programs")
    
    print(f"\n✅ Catalog saved to: {CATALOG_FILE}")
    print(f"\n🎯 Next steps:")
    print(f"   1. Merge training examples into main dataset")
    print(f"   2. Re-train model with comprehensive dataset")
    print(f"   3. Evaluate with diverse test cases\n")


if __name__ == "__main__":
    main()
