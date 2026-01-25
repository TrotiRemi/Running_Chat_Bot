from pathlib import Path

from .export_to_csv import export_to_csv
from .iter_pdfs import iter_pdfs
from .process_pdf_file import process_pdf_file


def extract_pdfs_to_csv(pdf_dir: Path, output_dir: Path = None) -> list:
    """
    Extract PDFs to CSV data.
    If output_dir is None, returns data in memory only.
    If output_dir is provided, also saves to disk.
    """
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
    
    processed_count = 0
    total_weeks = 0
    all_data = []

    for pdf_file in iter_pdfs(pdf_dir):
        training_data = process_pdf_file(pdf_file)
        if training_data:
            all_data.extend(training_data)
            if output_dir:
                output_file = output_dir / f"{pdf_file.stem}.csv"
                export_to_csv(training_data, output_file)
            processed_count += 1
            total_weeks += len(training_data)

    print(f"✅ Extraction PDF terminée: {processed_count} fichiers, {total_weeks} semaines")
    return all_data
