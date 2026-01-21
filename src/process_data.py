import os
import re
import csv
from pathlib import Path

def extract_features(filename):
    """Extrait les caracteristiques du nom de fichier"""
    
    # Initialiser tous les champs
    features = {
        'goal_distance': None,
        'goal_time': None,
        'level': None,
        'weeks_training': None,
        'training_per_week': None,
        'age': None
    }
    
    name = filename.lower()
    # Supprimer l'extension
    name_clean = re.sub(r'\.(pdf|xlsx)$', '', name)
    # Normaliser les variantes de noms de courses
    name_clean = re.sub(r'run\s*walk\s*', '', name_clean)
    
    # ========== DISTANCE ==========
    distance_match = re.search(r'(\d+)\s*(k|mile|miles)(?![a-z])', name_clean)
    if distance_match:
        value = int(distance_match.group(1))
        unit = distance_match.group(2)
        
        # Convertir miles en km (1 mile = 1.609 km)
        if unit in ['mile', 'miles']:
            km = round(value * 1.609, 1)
            features['goal_distance'] = f"{km}km"
        else:
            features['goal_distance'] = f"{value}{unit}"
    # Sinon chercher marathon/halfmarathon
    elif 'halfmarathon' in name_clean or 'half-marathon' in name_clean:
        features['goal_distance'] = 'halfmarathon'
    elif 'marathon' in name_clean:
        features['goal_distance'] = 'marathon'
    
    # ========== NIVEAU ==========
    if 'beginner' in name_clean:
        features['level'] = 'beginner'
    elif 'intermediate' in name_clean:
        features['level'] = 'intermediate'
    elif 'advanced' in name_clean:
        features['level'] = 'advanced'
    elif 'maintenance' in name_clean:
        features['level'] = 'maintenance'
    
    # ========== SEMAINES D'ENTRAINEMENT ==========
    weeks_match = re.search(r'(\d+)w', name_clean)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        if 1 <= weeks <= 100:
            features['weeks_training'] = weeks
    
    # ========== JOURS D'ENTRAINEMENT PAR SEMAINE ==========
    training_match = re.search(r'(\d{1,2})d', name_clean)
    if training_match:
        training = int(training_match.group(1))
        if 1 <= training <= 7:
            features['training_per_week'] = training
    
    # ========== TEMPS CIBLE ==========
    # Chercher XhYm ou XhY (ex: 2h15m, 2h15, 3h, 4h30)
    time_match = re.search(r'(\d+)h(\d{1,2})', name_clean)
    if time_match:
        hours = time_match.group(1)
        minutes = time_match.group(2)
        features['goal_time'] = f"{hours}h{minutes}m"
    else:
        time_match = re.search(r'(\d+)h(?![\d])', name_clean)
        if time_match:
            features['goal_time'] = f"{time_match.group(1)}h"
    
    # ========== AGE ==========
    age_match = re.search(r'(?:^|[-_])(\d{2})(?:[-_]|$)', name_clean)
    if age_match:
        age = int(age_match.group(1))
        if 20 <= age <= 80:
            features['age'] = age
    
    return features


def process_training_files():
    """Traite tous les fichiers PDF et XLSX"""
    
    data_dir = Path('Data')
    pdf_dir = data_dir / 'pdf'
    xlsx_dir = data_dir / 'xlsx'
    output_file = data_dir / 'training_analysis.csv'
    
    results = []
    
    # Traiter les PDF
    if pdf_dir.exists():
        for pdf_file in sorted(pdf_dir.glob('*.pdf')):
            features = extract_features(pdf_file.name)
            results.append({
                'fichier': str(pdf_file),
                'goal_distance': features['goal_distance'],
                'goal_time': features['goal_time'],
                'level': features['level'],
                'weeks_training': features['weeks_training'],
                'training_per_week': features['training_per_week'],
                'age': features['age']
            })
    
    # Traiter les XLSX
    if xlsx_dir.exists():
        for xlsx_file in sorted(xlsx_dir.glob('*.xlsx')):
            features = extract_features(xlsx_file.name)
            results.append({
                'fichier': str(xlsx_file),
                'goal_distance': features['goal_distance'],
                'goal_time': features['goal_time'],
                'level': features['level'],
                'weeks_training': features['weeks_training'],
                'training_per_week': features['training_per_week'],
                'age': features['age']
            })
    
    # Ecrire le CSV
    if results:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'fichier', 'goal_distance', 'goal_time', 'level',
                'weeks_training', 'training_per_week', 'age'
            ])
            writer.writeheader()
            writer.writerows(results)
        
        print(f"CSV genere: {output_file}")
        print(f"{len(results)} fichiers traites")
    else:
        print("Aucun fichier trouve dans Data/pdf ou Data/xlsx")


if __name__ == '__main__':
    process_training_files()