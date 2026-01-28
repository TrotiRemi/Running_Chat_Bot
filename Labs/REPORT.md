# Report — Labs LLMs (Lab 2 → Lab 7)

## 1) Introduction

L’objectif de cette série de labs est de comprendre et reconstruire progressivement les mécanismes fondamentaux des Large Language Models (LLMs), en particulier les architectures de type GPT.  
Les notebooks suivent une progression logique : préparation du texte, mécanisme d’attention, construction d’un modèle GPT complet, pré-entraînement, puis fine-tuning sur des tâches supervisées (classification) et enfin instruction-following.

Les labs abordés dans ce report :
- Lab 2 — Working with Text
- Lab 3 — Coding Attention Mechanisms
- Lab 4 — Implementing a GPT Model from Scratch (Text Generation)
- Lab 5 — Pretraining on Unlabeled Data
- Lab 6 — Fine-tuning for Classification (Spam vs Ham)
- Lab 7 — Fine-tuning to Follow Instructions (SFT)

Les Labs 2 à 4 ont été fais en local car pas besoin de beaucoup de mémoires, par contre dès le Lab 5 je suis passé sur Collab sinon c'étais impossible pour moi de faire tourner les training et fine-tunning mais aussi car je n'ai pas de place en local pour avoir les GPT-2 qui sont au dessus du modèle small.

---

## 2) Lab 2 — Working with Text

### Objectif
Mettre en place le pipeline complet permettant de transformer du texte brut en un format exploitable par un modèle de type GPT.

### Étapes principales
- Tokenisation simple puis tokenisation améliorée (regex + ponctuation)
- Construction d’un vocabulaire + mapping token ↔ id
- Gestion des mots inconnus avec <|unk|>
- Ajout du token spécial <|endoftext|> pour séparer des documents
- Introduction à la tokenisation BPE (Byte Pair Encoding) via tiktoken
- Construction de données d’entraînement “next-token prediction”
- Création d’un Dataset et DataLoader (sliding window avec stride)
- Mise en place des token embeddings + positional embeddings

### Concepts clés
- Un LLM apprend sur une séquence de tokens, pas directement sur des mots.
- Le format GPT repose sur l’apprentissage :
  input tokens → prédire le token suivant
- Les embeddings sont indispensables pour encoder :
  - le contenu du token (token embedding)
  - la position dans la séquence (positional embedding)

### Exercises
Objectifs :
- Exploring Byte Pair Encoding (BPE) Tokenization with Unknown Words
- Exploring Data Loader Behavior with Different Parameters
---

## 3) Lab 3 — Coding Attention Mechanisms

### Objectif
Comprendre et implémenter le mécanisme d’attention utilisé dans les Transformers, jusqu’à obtenir la version utilisée dans GPT.

### Étapes principales
- Self-attention “naïve” :
  - score par dot-product
  - normalisation avec softmax
  - création du context vector
- Version vectorisée (matrices)
- Attention avec paramètres entraînables :
  - projections Q, K, V
  - scores = QKᵀ
  - softmax(scores / sqrt(d_k))
  - context = weights · V
- Ajout du causal mask (GPT : pas accès au futur)
- Dropout sur les poids d’attention
- Passage à la multi-head attention
  - plusieurs têtes → concat → projection finale

### Concepts clés
- L’attention permet de relier directement deux tokens éloignés.
- La causal attention est indispensable pour la génération auto-régressive.
- La multi-head attention apprend plusieurs types de relations en parallèle.

### Exercises
Objectifs :
- Can you transfer the weights from SelfAttention_v2 to SelfAttention_v1 such that both implementations produce identical output tensors?
- How can you modify the input arguments to the MultiHeadAttentionWrapper(num_heads=2) to transform the output context vectors from four-dimensional to two-dimensional while maintaining the num_heads=2 configuration?
- Can you configure a MultiHeadAttention module that precisely replicates the architectural specifications of the smallest GPT-2 model?

---

## 4) Lab 4 — Implementing a GPT Model from Scratch (Text Generation)

### Objectif
Assembler les briques précédentes pour reconstruire une architecture complète de type GPT, capable de générer du texte.

### Étapes principales
- Définition d’une configuration GPT-2-like (124M)
- Implémentation de LayerNorm (stabilité)
- Implémentation du FeedForward Network (MLP) avec activation GELU
- Mise en évidence des skip connections / residual connections
- Construction du Transformer Block :
  - Pre-LN → attention → residual
  - Pre-LN → FFN → residual
- Construction du modèle GPTModel :
  - token embeddings + position embeddings
  - N transformer blocks
  - LayerNorm final
  - projection en logits (vocab_size)
- Implémentation de la génération :
  - greedy decoding (argmax)
  - contexte croppé à context_length

### Concepts clés
- GPT est un modèle auto-régressif : il génère token par token.
- La structure (Attention + FFN) répétée N fois forme la base du modèle.
- Les connexions résiduelles rendent l’entraînement plus stable et plus profond.

### Exercises
Objectifs :
- Parameters in the feed forward versus attention module
- Initialize larger GPT models
- Using separate dropout parameters

---

## 5) Lab 5 — Pretraining on Unlabeled Data

### Objectif
Mettre en place un pipeline complet de pré-entraînement d’un GPT en next-token prediction, puis explorer le décodage et le chargement de poids GPT-2.

### Étapes principales
- Mise en place du calcul de loss :
  - cross-entropy sur les logits
  - notion de perplexity
- Split train/validation
- Boucle d’entraînement avec AdamW
- Tracking de :
  - train loss / validation loss
  - tokens_seen
- Génération périodique pour visualiser l’amélioration
- Ajout de stratégies de decoding :
  - temperature scaling
  - top-k sampling
- Sauvegarde / rechargement de checkpoints
- Chargement des poids GPT-2 OpenAI dans le GPT “maison”
  - mapping QKV
  - vérification par génération cohérente

### Concepts clés
- Le pré-entraînement apprend une connaissance générale du langage.
- Les stratégies de décodage changent fortement la diversité et la qualité du texte.
- Charger GPT-2 permet d’obtenir un modèle performant sans entraîner depuis zéro.

### Exercises
Objectifs :
- Temperature-scaled softmax scores and sampling probabilities
- Different temperature and top-k settings
- Deterministic behavior in the decoding functions
- Continued pretraining
- Training and validation set losses of the pretrained model
- Trying larger models

---

## 6) Lab 6 — Fine-tuning for Classification (Spam vs Ham)

### Objectif
Adapter un GPT pré-entraîné à une tâche supervisée : **classification** (spam / ham).

### Étapes principales
- Chargement dataset SMS Spam Collection
- Préparation :
  - équilibrage classes
  - encodage labels (0/1)
  - split train/val/test
- Tokenisation GPT-2 + padding (<|endoftext|>)
- Construction DataLoaders batchés
- Remplacement de la tête de sortie :
  - Linear(emb_dim → 2)
- Fine-tuning partiel :
  - modèle gelé
  - entraînement du dernier bloc + head
- Calcul de :
  - cross-entropy loss
  - accuracy
- Tests sur exemples et sauvegarde du modèle

### Concepts clés
- Fine-tuning = réutiliser un modèle pré-entraîné et l’adapter à une tâche.
- Le fine-tuning partiel est souvent efficace et plus rapide.
- Le dernier token peut servir de représentation globale du texte pour classifier.

### Exercises
Objectifs :
- Increasing the context length
- Finetuning the whole model
- Finetuning the first versus last token 

---

## 7) Lab 7 — Fine-tuning to Follow Instructions (SFT)

### Objectif
Apprendre à un GPT à suivre des consignes, via Instruction Fine-Tuning supervisé (SFT).

### Étapes principales
- Chargement dataset JSON :
  - instruction
  - input (optionnel)
  - output
- Formatage prompt style Alpaca :
  -  Instruction
  -  Input (si présent)
  -  Response
- Tokenisation du prompt complet (prompt + réponse)
- Collate function personnalisée :
  - padding
  - construction inputs/targets décalés
  - masking : loss uniquement sur la réponse (ignore_index = -100)
- Fine-tuning supervisé avec AdamW
- Génération sur test set et sauvegarde des réponses
- Évaluation automatique via un autre LLM (Ollama / Llama3)
  - scoring /100

### Concepts clés
- SFT transforme un modèle “autocomplete” en modèle “assistant”.
- Le masking est essentiel : le modèle apprend à produire la réponse, pas à recopier le prompt.
- Une évaluation automatique par LLM permet de comparer rapidement des modèles.

### Exercises
Objectifs :
- Changing prompt styles
- Instruction and input masking
- Finetuning on the original Alpaca dataset

---

## 8) Conclusion

Ces labs montrent une progression complète sur la compréhension et l’implémentation d’un GPT :

- Lab 2 : préparation du texte, tokenisation, embeddings, DataLoader
- Lab 3 : attention causale et multi-head attention
- Lab 4 : construction complète d’un GPT et génération
- Lab 5 : pré-entraînement + décodage + chargement GPT-2
- Lab 6 : fine-tuning pour classification supervisée
- Lab 7 : instruction fine-tuning pour obtenir un modèle assistant

Au final, on comprend que la performance d’un LLM dépend à la fois :
- de l’architecture (attention, blocks, résiduels),
- de la préparation des données,
- du pré-entraînement,
- du fine-tuning selon la tâche,
- et des stratégies de génération/décodage.
