from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn as nn
from pathlib import Path
import json
import tiktoken
import re

app = Flask(__name__)
CORS(app)

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "output" / "model" / "running_plan_finetuned_model_2.pth"

# Variables globales
model = None
tokenizer = None

# Modèle SimpleGPT (même architecture que celle utilisée dans le notebook)
class SimpleGPT(nn.Module):
    """Simplified GPT model for instruction finetuning"""
    def __init__(self, vocab_size=50257, embedding_dim=256, n_layers=4, n_heads=4, context_length=1024):
        super().__init__()
        self.token_embedding = nn.Embedding(vocab_size, embedding_dim)
        self.pos_embedding = nn.Embedding(context_length, embedding_dim)
        
        # Transformer layers
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embedding_dim,
            nhead=n_heads,
            dim_feedforward=512,
            batch_first=True,
            dropout=0.1
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        
        # Output layer
        self.output_layer = nn.Linear(embedding_dim, vocab_size)
    
    def forward(self, input_ids):
        seq_len = input_ids.size(1)
        pos_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)
        
        token_emb = self.token_embedding(input_ids)
        pos_emb = self.pos_embedding(pos_ids)
        x = token_emb + pos_emb
        
        x = self.transformer(x)
        logits = self.output_layer(x)
        return logits


def apply_repetition_penalty(logits, generated_ids, penalty=1.2):
    """Apply repetition penalty to logits"""
    if penalty == 1.0 or generated_ids.numel() == 0:
        return logits
    unique_ids = torch.unique(generated_ids)
    logits[unique_ids] = logits[unique_ids] / penalty
    return logits


def generate_with_sampling(model, prompt_ids, tokenizer, device, max_tokens=200, 
                          top_k=50, temperature=0.7, stop_token=50256, repetition_penalty=1.2):
    """Generate text using top-k sampling with repetition penalty (from notebook)"""
    model.eval()
    output_ids = prompt_ids.clone()
    
    with torch.no_grad():
        for _ in range(max_tokens):
            logits = model(output_ids)
            next_token_logits = logits[0, -1, :] / temperature
            next_token_logits = apply_repetition_penalty(next_token_logits, output_ids[0], penalty=repetition_penalty)
            
            top_k_logits, top_k_indices = torch.topk(next_token_logits, min(top_k, next_token_logits.size(0)))
            top_k_probs = torch.softmax(top_k_logits, dim=-1)
            sampled_idx = torch.multinomial(top_k_probs, 1)
            next_token = top_k_indices[sampled_idx]
            output_ids = torch.cat([output_ids, next_token.view(1, 1)], dim=1)
            
            if next_token.item() == stop_token:
                break
    
    return output_ids


def load_model():
    """Charge le modèle au démarrage"""
    global model, tokenizer
    
    try:
        # Charger le tokenizer
        tokenizer = tiktoken.get_encoding("gpt2")
        print(f"✓ Tokenizer GPT-2 chargé")
        
        # Créer l'instance du modèle
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = SimpleGPT(
            vocab_size=50257,
            embedding_dim=256,
            n_layers=4,
            n_heads=4,
            context_length=1024
        ).to(device)
        
        # Charger les poids
        if MODEL_PATH.exists():
            state_dict = torch.load(MODEL_PATH, map_location=device)
            model.load_state_dict(state_dict)
            print(f"✓ Modèle chargé avec succès depuis {MODEL_PATH}")
            print(f"  Device: {device}")
            print(f"  Architecture: SimpleGPT (256 dim, 4 layers, 4 heads)")
        else:
            print(f"✗ Fichier modèle non trouvé: {MODEL_PATH}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Erreur lors du chargement du modèle: {e}")
        return False


def build_prompt(instruction_text, input_text):
    """Formate le prompt selon le format du notebook"""
    prompt_text = (
        f"Below is an instruction that describes a task. "
        f"Write a response that appropriately completes the request."
        f"\n\n### Instruction:\n{instruction_text}"
    )
    if input_text:
        prompt_text += f"\n\n### Input:\n{input_text}"
    prompt_text += f"\n\n### Response:\n"
    return prompt_text


def clean_content(content: str) -> str:
    """Nettoie et normalise le contenu généré"""
    c = content.strip()
    if not c:
        return "Rest"
    
    # Couper le contenu au premier jour non complètement formé
    day_names = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche",
                 "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    for day in day_names:
        if day in c and c.find(day) > 0:  # Ne pas couper au début
            c = c[:c.find(day)].strip()
            break
    
    # Nettoyer les caractères spéciaux
    c = re.sub(r"[\\/]+", " ", c)
    c = re.sub(r"\bmin\s*:\s*", "min ", c, flags=re.IGNORECASE)
    c = re.sub(r"\s+", " ", c).strip(" -;,")
    c = re.sub(r"(\d)(km|mile|miles|min)", r"\1 \2", c, flags=re.IGNORECASE)
    
    if c in {"-", "/", ""}:
        return "Rest"
    
    # Si seulement un temps, ajouter "Easy Run"
    if re.match(r"^\d+(?:\.\d+)?\s*min(utes)?$", c, flags=re.IGNORECASE):
        return c + " Easy Run"
    
    # Si seulement une distance, ajouter "Easy Run"
    if re.match(r"^\d+(?:\.\d+)?\s*(km|mile|miles)$", c, flags=re.IGNORECASE):
        return c + " Easy Run"
    
    # Si distance + activité mais sans unité, ajouter km
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(easy run|run|long run|intervals|tempo|recovery)$", c, flags=re.IGNORECASE)
    if m and "km" not in c.lower() and "mile" not in c.lower() and "min" not in c.lower():
        num = m.group(1)
        label = m.group(2).title()
        return f"{num} km {label}"
    
    return c if c else "Rest"


def enforce_week_structure(text, max_rest=3):
    """Formate la réponse en structure de semaine avec sauts de ligne"""
    text = text.replace("<|endoftext|>", "").strip()
    
    # Remplacer les noms de jours anglais par français si présents
    text = text.replace("Monday", "Lundi")
    text = text.replace("Tuesday", "Mardi")
    text = text.replace("Wednesday", "Mercredi")
    text = text.replace("Thursday", "Jeudi")
    text = text.replace("Friday", "Vendredi")
    text = text.replace("Saturday", "Samedi")
    text = text.replace("Sunday", "Dimanche")
    
    # Normaliser les sauts de ligne
    # Si des jours sont sur la même ligne (ex: "Lundi: Rest Mardi: Run"), les séparer
    day_order = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    day_labels = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    
    # Ajouter des sauts de ligne avant chaque jour (sauf le premier)
    for day_label in day_labels[1:]:
        text = re.sub(rf'([^\n])\s+{day_label}:', r'\1\n' + day_label + ':', text, flags=re.IGNORECASE)
    
    # Diviser en lignes et traiter chacune
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    day_map = {}
    
    for line in lines:
        lower = line.lower()
        for i, day in enumerate(day_order):
            if lower.startswith(day):
                # Extraire le contenu après le jour
                if ":" in line:
                    content = line.split(":", 1)[1].strip()
                else:
                    content = ""
                
                content = clean_content(content)
                if not content:
                    content = "Rest"
                if day not in day_map:
                    day_map[day] = content
                break
    
    # Construire la sortie avec tous les jours
    output_lines = []
    for day, label in zip(day_order, day_labels):
        content = day_map.get(day, "Rest")
        output_lines.append(f"{label}: {content}")
    
    return "\n".join(output_lines)


@app.route("/api/health", methods=["GET"])
def health():
    """Endpoint de santé"""
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None,
        "device": "cuda" if torch.cuda.is_available() else "cpu"
    })


@app.route("/api/chat", methods=["GET", "POST", "OPTIONS"])
def chat():
    """Endpoint principal du chat"""
    if request.method == "OPTIONS":
        return '', 204
    
    if request.method == "GET":
        return jsonify({"error": "Use POST for chat messages"}), 405
    
    try:
        data = request.json
        user_message = data.get("message", "").strip()
        
        if not user_message:
            return jsonify({"error": "Message vide"}), 400
        
        if model is None:
            return jsonify({"error": "Modèle non chargé"}), 500
        
        # Générer la réponse
        device = next(model.parameters()).device
        
        # Construire le prompt
        instruction = "Generate a complete week (1) of a running training program."
        prompt = build_prompt(instruction, user_message)
        
        # Tokeniser
        prompt_ids = tokenizer.encode(prompt)
        prompt_ids_tensor = torch.tensor([prompt_ids[:1024]], dtype=torch.long).to(device)
        
        # Générer avec top-k sampling
        output_ids = generate_with_sampling(
            model, 
            prompt_ids_tensor, 
            tokenizer, 
            device,
            max_tokens=200,
            top_k=50,
            temperature=0.7,
            repetition_penalty=1.2
        )
        
        # Décoder
        full_text = tokenizer.decode(output_ids[0].cpu().numpy())
        
        # Extraire la réponse
        if "### Response:\n" in full_text:
            generated_week = full_text.split("### Response:\n")[-1].strip()
        else:
            generated_week = full_text[-400:]
        
        # Formater en structure de semaine
        generated_week = enforce_week_structure(generated_week)
        
        return jsonify({
            "user_message": user_message,
            "bot_response": generated_week
        })
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Charger le modèle au démarrage
    if load_model():
        print("\n🚀 Démarrage du serveur Flask...")
        app.run(debug=True, host="0.0.0.0", port=5000)
    else:
        print("✗ Impossible de démarrer le serveur sans modèle")
