import json


def save_dataset(dataset, output_file: str):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Dataset sauvegardé: {output_file}\n")
