# Chapitre 4 : Évaluation Sémantique (LLM-as-a-Judge) 🧠⚖️

Ce chapitre se concentre sur l'audit du **sens** des réponses générées par un système RAG, en allant au-delà de la simple validation de format pour garantir l'absence d'hallucinations.

## 🎯 Intérêt de cette branche

L'objectif de la branche `chapter-4` est de mettre en place une évaluation sémantique automatisée basée sur le paradigme **LLM-as-a-Judge** :
1. **La Triade RAG** : Évaluer la qualité du système sur trois axes fondamentaux :
    *   **Context Precision** : Le contexte récupéré est-il utile ?
    *   **Faithfulness** : La réponse est-elle fidèle au contexte (anti-hallucination) ?
    *   **Answer Relevance** : La réponse répond-elle directement à la question ?
2. **Explicabilité** : Contrairement aux métriques mathématiques opaques, le Juge LLM fournit un **raisonnement textuel** pour justifier ses scores.
3. **Résilience via LiteLLM** : Utilisation d'un proxy unifié pour garantir que la pipeline d'évaluation reste disponible même en cas de surcharge d'un fournisseur d'IA.

---

## 🏗️ Architecture d'Évaluation

Le système utilise un conteneur dédié (`evaluator`) qui :
*   Simule un **Golden Dataset** (jeu de questions/réponses de référence).
*   Interroge le Juge LLM (Llama 3 via Groq) à travers le proxy **LiteLLM**.
*   Génère des rapports visuels détaillés avec **Evidently AI**.

---

## 🚀 Lancement et Utilisation

Assurez-vous d'avoir votre fichier `.env` configuré avec vos clés d'API (Groq, etc.).

### 1. Démarrer la stack RAGOPS
Lancez les services de base (Backend, Meilisearch, Proxy, etc.) :
```bash
make up
```

## 📁 Structure de l'Évaluation

*   `src/eval/eval_rag.py` : Script principal configurant Evidently et le Juge LLM.
*   `src/eval/check_semantic.py` : Le "Quality Gate" qui valide les scores finaux.
*   `reports/` : Contient les rapports HTML (ex: `chapter4_semantic_report.html`) détaillant le raisonnement du Juge.
