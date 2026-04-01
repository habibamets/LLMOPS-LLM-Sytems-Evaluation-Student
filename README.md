# Chapitre 1 : Fondamentaux de l'Évaluation LLM et Architecture Production-Ready 🚀🏗️

Ce chapitre pose les bases de l'évaluation automatisée pour les systèmes LLM, en passant d'une observation anecdotique à une télémétrie structurée et actionable.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-1` est de mettre en place une infrastructure de test robuste :
1. **Gestion du Non-Déterminisme** : Transformer des sorties textuelles variables en signaux numériques stables.
2. **Architecture Séparée** : 
    *   **L'Évaluateur** (`app.py`) : Calcule les métriques et génère les rapports.
    *   **Le Gatekeeper** (`check_limits.py`) : Prend la décision binaire (Pass/Fail) pour la CI/CD.
3. **Métriques de Base (Smoke Tests)** :
    *   **TextLength** (Longueur) : Détecter les réponses tronquées ou les bugs d'API.
    *   **OOV (Out of Vocabulary)** : Mesurer l'hallucination via le jargon inventé.
    *   **Sentiment** : Surveiller le ton de l'assistant.
    *   **RegExp** : Détecter les refus explicites du modèle ("I don't know", etc.).

---

## 🏗️ Architecture "Production-Ready"

Le système est orchestré via Docker pour garantir la reproductibilité :
*   **Conteneur Evaluator** : Isole les dépendances (uv, pandas, evidently, nltk).
*   **Volume mapping** : Le dossier `reports/` est partagé entre le conteneur et votre machine pour un accès instantané aux rapports HTML/JSON.

---

## 📁 Structure de l'Évaluation

*   `src/app.py` : Configuration des descripteurs Evidently et génération des snapshots.
*   `src/check_limits.py` : Script de décision CI/CD (Quality Gate).
*   `reports/` : Dossier contenant les rapports (HTML pour l'humain, JSON pour la machine).

---

> [!NOTE]
> En production, l'évaluation n'est pas une option, c'est le **téléscope** qui vous permet de voir ce qui se passe réellement dans la boîte noire de votre LLM.

