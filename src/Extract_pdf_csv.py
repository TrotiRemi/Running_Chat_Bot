import csv
import pdfplumber
import re
from pathlib import Path


def extract_training_table(pdf_path):
    """Extrait les tableaux d'entraînement d'un PDF avec pdfplumber"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_tables = []
            for page_idx, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables()
                    if tables:
                        all_tables.extend(tables)
                except Exception as e:
                    print(f"  ⚠️  Erreur page {page_idx + 1}: {type(e).__name__}")
                    continue
            return all_tables
    except Exception as e:
        print(f"Erreur lecture {pdf_path}: {e}")
        return None


def clean_text(text):
    """Nettoie le texte"""
    if not text:
        return ""
    text = str(text).strip()
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def extract_workout_from_cell(text):
    """Extrait le contenu workout d'une cellule"""
    if not text:
        return ""
    
    text = clean_text(text)
    
    # Supprimer les patterns "DAY X" au début
    text = re.sub(r'^day\s*\d+\s*', '', text, flags=re.IGNORECASE)
    
    # Supprimer le bruit OCR et caractères spéciaux au début
    noise_patterns = [
        r'^[.…\-—–owqn]+\s*', # Symboles au début (., ..., -, —, o, w, q, n, etc.)
        r'^(?:days?|ill::|o ll::|ll::)\s*', # DAYS, DAY, ill::, o ll::, etc.
        r'ill::', r'o ll::', r'll::', r'\.i', r'ill\s*:', r'::', r'—', 
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    
    # Supprimer les caractères de contrôle mais garder les essentiels
    text = re.sub(r'[^\w\s\-/\.()\']', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def detect_format(headers):
    """Détecte si c'est format nommé (Monday, Tuesday) ou numérique (DAY 1, DAY 2)"""
    day_patterns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                    'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    has_named_days = False
    has_day_numbers = False
    
    for header in headers:
        if not header:
            continue
        header_lower = clean_text(header).lower()
        
        # Chercher jours nommés
        if any(pattern in header_lower for pattern in day_patterns):
            has_named_days = True
        
        # Chercher format "DAY X" ou "DAYX" (avec ou sans espace)
        if re.match(r'^day\s*\d+', header_lower):
            has_day_numbers = True
    
    if has_named_days:
        return 'named'
    elif has_day_numbers:
        return 'numbered'
    else:
        return None


def detect_day_columns_named(headers):
    """Détecte colonnes jours pour format nommé (Monday, Tuesday, etc.)"""
    day_patterns = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
                    'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    day_columns = {}
    
    for idx, header in enumerate(headers):
        if not header:
            continue
        
        header_lower = clean_text(header).lower()
        
        for pattern in day_patterns:
            if pattern in header_lower:
                day_columns[idx] = header
                break
    
    return day_columns


def detect_day_columns_numbered(headers):
    """Détecte colonnes jours pour format numérique (DAY 1, DAY 2, DAY1, DAY2, etc.)"""
    day_columns = {}
    
    for idx, header in enumerate(headers):
        if not header:
            continue
        
        header_lower = clean_text(header).lower()
        
        # Chercher "DAY X" ou "DAYX" (avec ou sans espace)
        if re.match(r'^day\s*\d+', header_lower):
            day_columns[idx] = header
    
    return day_columns


def process_training_table_optimized(table, week_offset=0):
    """Traite un tableau en format semaine/jour"""
    if not table or len(table) < 2:
        return None
    
    # Nettoyer les headers
    headers = [clean_text(h) for h in table[0]]
    
    # Détecter le format (nommé ou numérique)
    format_type = detect_format(headers)
    
    if format_type == 'named':
        return process_training_table_named(table, headers, week_offset)
    elif format_type == 'numbered':
        return process_training_table_numbered(table, headers, week_offset)
    else:
        print("  ⚠️  Aucune colonne jour détectée")
        return None


def process_training_table_named(table, headers, week_offset):
    """Traite tableau avec jours nommés (Monday, Tuesday, etc.)"""
    # Détecter les colonnes jours
    day_columns = detect_day_columns_named(headers)
    
    if not day_columns:
        print("  ⚠️  Aucune colonne jour détectée")
        return None
    
    # Créer les jours triés
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ordered_days = []
    
    for idx in sorted(day_columns.keys()):
        day_name = day_columns[idx]
        day_lower = clean_text(day_name).lower()
        
        for day in day_order:
            if day.lower() in day_lower:
                ordered_days.append(day)
                break
    
    if not ordered_days:
        print("  ⚠️  Aucune colonne jour détectée")
        return None
    
    # Déterminer si on a une structure alternée (2 lignes par semaine)
    has_alternating_pattern = False
    if len(table) > 2:
        # Compter les colonnes non-vides pour les 2 premières lignes de données
        line1_empty_cols = sum(1 for i in range(len(table[1])) if not clean_text(table[1][i]))
        line2_empty_cols = sum(1 for i in range(len(table[2])) if not clean_text(table[2][i]))
        # Si une ligne a beaucoup plus de colonnes vides, c'est probablement alternée
        if abs(line1_empty_cols - line2_empty_cols) > len(table[1]) * 0.3:
            has_alternating_pattern = True
    
    # Extraire les données
    training_data = []
    week_idx = week_offset + 1
    row_offset = 1  # Commence à la ligne 1 (après headers)
    
    if has_alternating_pattern:
        # Mode alternée: fusionner 2 lignes en 1 semaine
        while row_offset < len(table):
            row1 = table[row_offset] if row_offset < len(table) else []
            row2 = table[row_offset + 1] if row_offset + 1 < len(table) else []
            
            week_row = [f"Week {week_idx}"]
            
            # Fusionner les données des 2 lignes
            for col_idx in sorted(day_columns.keys()):
                # Prendre la première ligne qui a du contenu
                value1 = clean_text(row1[col_idx]) if col_idx < len(row1) else ""
                value2 = clean_text(row2[col_idx]) if col_idx < len(row2) else ""
                
                # Nettoyer et fusionner
                value1 = extract_workout_from_cell(value1) if value1 else ""
                value2 = extract_workout_from_cell(value2) if value2 else ""
                
                # Prendre la valeur non-vide
                final_value = value1 if value1 else value2
                week_row.append(final_value)
            
            training_data.append(week_row)
            week_idx += 1
            row_offset += 2
    else:
        # Mode normal: une ligne = une semaine
        while row_offset < len(table):
            row = table[row_offset]
            week_row = [f"Week {week_idx}"]
            
            for col_idx in sorted(day_columns.keys()):
                if col_idx < len(row):
                    value = clean_text(row[col_idx])
                    if value:
                        value = extract_workout_from_cell(value)
                    week_row.append(value)
                else:
                    week_row.append("")
            
            training_data.append(week_row)
            week_idx += 1
            row_offset += 1
    
    return {
        'headers': ['Week'] + ordered_days,
        'data': training_data
    }


def process_training_table_numbered(table, headers, week_offset):
    """Traite tableau avec jours numérotés - Format continu: Day 0, Day 1, Day 2, etc."""
    # Détecter les colonnes jours
    day_columns = detect_day_columns_numbered(headers)
    
    if not day_columns:
        print("  ⚠️  Aucune colonne jour détectée")
        return None
    
    # Déterminer si on a une structure alternée (2 lignes par semaine)
    has_alternating_pattern = False
    if len(table) > 2:
        line1_empty_cols = sum(1 for i in range(len(table[1])) if not clean_text(table[1][i]))
        line2_empty_cols = sum(1 for i in range(len(table[2])) if not clean_text(table[2][i]))
        if abs(line1_empty_cols - line2_empty_cols) > len(table[1]) * 0.3:
            has_alternating_pattern = True
    
    # Extraire TOUS les jours de manière continue
    all_days = []
    day_counter = 0
    row_offset = 1
    
    if has_alternating_pattern:
        # Mode alternée: fusionner 2 lignes
        while row_offset < len(table):
            row1 = table[row_offset] if row_offset < len(table) else []
            row2 = table[row_offset + 1] if row_offset + 1 < len(table) else []
            
            for col_idx in sorted(day_columns.keys()):
                value1 = clean_text(row1[col_idx]) if col_idx < len(row1) else ""
                value2 = clean_text(row2[col_idx]) if col_idx < len(row2) else ""
                
                value1 = extract_workout_from_cell(value1) if value1 else ""
                value2 = extract_workout_from_cell(value2) if value2 else ""
                
                final_value = value1 if value1 else value2
                # Toujours ajouter (même vide) pour garder la numérotation continue
                all_days.append(f"Day {day_counter}: {final_value if final_value else 'Rest'}")
                day_counter += 1
            
            row_offset += 2
    else:
        # Mode normal
        while row_offset < len(table):
            row = table[row_offset]
            
            for col_idx in sorted(day_columns.keys()):
                if col_idx < len(row):
                    value = clean_text(row[col_idx])
                    if value:
                        value = extract_workout_from_cell(value)
                    all_days.append(f"Day {day_counter}: {value if value else 'Rest'}")
                else:
                    all_days.append(f"Day {day_counter}: Rest")
                day_counter += 1
            
            row_offset += 1
    
    return {
        'headers': None,
        'data': [[", ".join(all_days)]]  # Une seule ligne avec tous les jours
    }


def process_all_pdfs_to_csv():
    """Traite tous les PDF et crée des fichiers CSV"""
    data_dir = Path('Data')
    pdf_dir = data_dir / 'pdf'
    csv_output_dir = data_dir / 'csv'
    
    csv_output_dir.mkdir(exist_ok=True)
    
    processed_count = 0
    
    if pdf_dir.exists():
        pdf_files = sorted(pdf_dir.glob('*.pdf'))
        
        for pdf_file in pdf_files:
            print(f"📄 Traitement: {pdf_file.name}")
            
            tables = extract_training_table(pdf_file)
            
            if tables:
                all_headers = None
                all_data = []
                week_counter = 1
                
                for table_idx, table in enumerate(tables):
                    processed_table = process_training_table_optimized(table, week_offset=week_counter - 1)
                    
                    if processed_table:
                        if all_headers is None:
                            all_headers = processed_table['headers']
                        
                        all_data.extend(processed_table['data'])
                        week_counter += len(processed_table['data'])
                        print(f"    📊 Tableau {table_idx + 1}: {len(processed_table['data'])} semaines")
                
                # Pour format numéroté (all_headers = None), on écrit juste les données
                if all_data and (all_headers or all_headers is None):
                    csv_filename = pdf_file.stem + '.csv'
                    csv_path = csv_output_dir / csv_filename
                    
                    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        if all_headers:
                            writer.writerow(all_headers)
                        writer.writerows(all_data)
                    
                    processed_count += 1
                    print(f"  ✅ OK: {csv_path}")
                    if all_headers:
                        print(f"     {len(all_data)} semaines, {len(all_headers)-1} jours")
                    else:
                        # Format numéroté: compter les jours à partir du contenu
                        if all_data:
                            day_count = len(all_data[0][0].split(', ')) if all_data[0] else 0
                            print(f"     {day_count} jours")
                else:
                    print(f"  ❌ Erreur de traitement")
            else:
                print(f"  ❌ Aucun tableau")
    
    print(f"\n✨ {processed_count} fichiers traites")
    print(f"📁 CSV dans: {csv_output_dir}")


if __name__ == '__main__':
    process_all_pdfs_to_csv()
